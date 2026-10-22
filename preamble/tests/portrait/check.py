"""竖版功能检查；字体、配色与间距通过样张目视验收。"""
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdfcheck as pc

OUT = pc.BUILD / 'portrait'
HINT = '请先运行 bash preamble/tests/portrait/run.sh'
c = pc.Checker('竖版')
pc.check_titlepage(c, OUT / 'titlepage.pdf', HINT)

with c.section('quotes：对照写法与局部作用域'):
    with c.open(OUT / 'quotes.pdf', HINT) as doc:
        pc.check_quotes(c, doc)

with c.section('code-cards：行号与跨页内容'):
    with c.open(OUT / 'code-cards.pdf', HINT) as doc:
        pc.check_code_line_numbers(c, doc)
        text = pc.compact(''.join(p.get_text() for p in doc))
        source = (pc.FIXTURES / 'long-code.cpp').read_text()
        expected = re.findall(r'int value\d+ = \d+;', source)
        actual = re.findall(r'intvalue\d+=\d+;', text)
        c.check(actual == [pc.compact(s) for s in expected], '长代码应完整、按序且不重复')
        pages = {p.number for p in doc if re.search(r'value\d+', p.get_text())}
        c.check(len(pages) > 1, '长代码应实际跨页')
        c.check(text.count('long-code.cpp') == 1, '跨页卡片标题只出现一次')

with c.section('heading-levels：独立标题、后文同页与书签'):
    with c.open(OUT / 'heading-levels.pdf', HINT) as doc:
        headings = [(level, pc.compact(title)) for level, title, _ in doc.get_toc() if level >= 4]
        c.require({level for level, _ in headings} == {4, 5}, '应有四、五级书签')
        headers = {pc.compact(title) for level, title, _ in doc.get_toc() if level == 1}
        rows = [[r for r in pc.text_rows(p) if not r['text'].strip().isdigit()
                 and pc.compact(r['text']) not in headers] for p in doc]
        for _, title in headings:
            prefix = title[:18]
            hits = [(i, j) for i, page in enumerate(rows) for j, row in enumerate(page)
                    if pc.compact(row['text']).startswith(prefix)]
            c.require(len(hits) == 1, '标题应完整出现一次', title)
            i, j = hits[0]
            joined = ''
            while j < len(rows[i]) and title.startswith(joined + pc.compact(rows[i][j]['text'])):
                joined += pc.compact(rows[i][j]['text'])
                j += 1
                if joined == title:
                    break
            c.check(joined == title, '标题应独立成行，换行后完整保留', title)
            # 连续标题允许相邻，但最终须跟随正文，不检查字体或固定间距。
            while j < len(rows[i]) and any(t == pc.compact(rows[i][j]['text']) for _, t in headings):
                j += 1
            c.check(j < len(rows[i]), '标题应与后文同页', title)
        for filler, title in [('边界一：本行之后', '页底四级标题：后接正文'), ('边界二：本行之后', '页底四级标题：后接行间公式')]:
            before = pc.locate(c, doc, filler)[0]
            after = pc.locate(c, doc, title)[0]
            c.check(after > before, '样张应实际触发页底标题保护', title)

with c.section('toc-layout：父子条目同页'):
    with c.open(OUT / 'toc-layout.pdf', HINT) as doc:
        for parent, child in [('页底保护：', '此条目跟随页底主题'), ('分页一级标题', '分页二级标题'),
                              ('分页二级标题', '分页三级首条')]:
            c.check(pc.locate(c, doc, parent)[0] == pc.locate(c, doc, child)[0], '父子目录条目应同页', parent)

sys.exit(c.finish())
