"""横版功能检查；加 code 时只检查代码版的扉页。"""
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdfcheck as pc
from pdfcheck import fitz

edition = sys.argv[1] if len(sys.argv) > 1 else 'landscape'
if edition not in ('landscape', 'code'):
    sys.exit('可用版本：landscape、code')
OUT = pc.BUILD / edition
HINT = f'请先运行 bash preamble/tests/{edition}/run.sh'
c = pc.Checker('代码版' if edition == 'code' else '横版')
pc.check_titlepage(c, OUT / 'titlepage.pdf', HINT, marker='（代码版）' if edition == 'code' else '')
if edition == 'code':
    sys.exit(c.finish())

with c.section('quotes：对照写法与局部作用域'):
    with c.open(OUT / 'quotes.pdf', HINT) as doc:
        pc.check_quotes(c, doc)

with c.section('flow：连续章节、标题保护与页眉'):
    with c.open(OUT / 'flow.pdf', HINT) as doc:
        positions = {name: pc.column(doc, pc.locate(c, doc, name + '-body'))
                     for name in ('Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon')}
        c.check(positions['Alpha'] == positions['Beta'], '相邻短章应连续排在同栏')
        c.check(positions['Delta'] == positions['Epsilon'], '空标题后应连续排版')
        c.check(positions['Alpha'] < positions['Gamma'] < positions['Delta'], '显式换栏换页应保持阅读顺序')
        for name, header in [('Alpha', 'Alpha 章'), ('Gamma', 'Alpha 章'), ('Delta', 'Delta 章')]:
            page = doc[positions[name][0]]
            g = pc.read_geometry(page)
            c.check(header in page.get_text(clip=fitz.Rect(0, 0, g.width, g.top - 1)),
                    '页眉应取页顶所在的章', header)
        for title, body in [('Boundary-title', 'Boundary-body'), ('Formula-title', 'FormulaBody')]:
            title_pos = pc.column(doc, pc.locate(c, doc, title))
            body_pos = pc.column(doc, pc.locate(c, doc, body))
            c.check(title_pos == body_pos, '栏底标题应与后文同栏', title)
            c.check(body_pos[1] == 1, '边界样张应实际触发换栏', body)

with c.section('code-cards：跨栏跨页内容与行号'):
    with c.open(OUT / 'code-cards.pdf', HINT) as doc:
        pc.check_code_line_numbers(c, doc, twocolumn=True)
        segments, lines = [], []
        for page in doc:
            for col, text in pc.column_texts(page):
                found = re.findall(r'int landscape_value_(\d{3}) = (\d+);', text)
                if found:
                    lines.extend(found)
                    segments.append((page.number, col))
        c.check(lines == [(f'{i:03d}', str(i)) for i in range(1, 101)], '长代码应完整、按序且不重复')
        pc.check_spanning(c, segments, '代码卡片')
        c.check(sum(p.get_text().count('Landscape-long-card') for p in doc) == 1, '跨栏卡片标题只出现一次')

with c.section('interfaces：引用跨栏跨页'):
    with c.open(OUT / 'interfaces.pdf', HINT) as doc:
        numbers, segments = [], []
        for page in doc:
            for col, text in pc.column_texts(page):
                found = re.findall(r'Quote-(\d{3})', text)
                if found:
                    numbers.extend(found)
                    segments.append((page.number, col))
        c.check(numbers == [f'{i:03d}' for i in range(1, 66)], '引用应完整、按序且不重复')
        pc.check_spanning(c, segments, '引用块')

with c.section('toc-layout：目录'):
    with c.open(OUT / 'toc-layout.pdf', HINT) as doc:
        toc_pages = [p for p in doc if p.get_links()]
        c.require(len(toc_pages) >= 2, '目录应至少两页', len(toc_pages))
        heading = [r for r in pc.text_rows(doc[0]) if r['text'].strip() == '目录']
        c.require(len(heading) == 1, '首页应有一个“目录”标题', heading)
        bookmarks = doc.get_toc(simple=False)
        c.require(bookmarks, '应有书签')
        c.check(len(bookmarks) == 90, '应有 90 个书签', len(bookmarks))
        c.check({b[0] for b in bookmarks} == {1, 2, 3, 4, 5}, '书签应有 5 个层级', sorted({b[0] for b in bookmarks}))
        c.check(all(b[3].get('collapse', True) for b in bookmarks), '初始只显示一级：可展开的书签都应闭合')
        body_first = bookmarks[0][2] - 1
        c.check(body_first == len(toc_pages), '正文应紧接目录页', body_first, len(toc_pages))
        expected = {b[1].split()[0]: b[2] - 1 for b in bookmarks if b[0] <= 3}
        positions = {}
        for page in toc_pages:
            text = page.get_text()
            c.check('Fourth-only' not in text and 'Fifth-only' not in text,
                    f'目录第 {page.number + 1} 页不应出现四、五级标题')
            c.check(not page.get_text(clip=fitz.Rect(0, 0, page.rect.width, pc.read_geometry(page).top - 1)).strip(),
                    f'目录第 {page.number + 1} 页不应有页眉')
            for token in expected:
                for rect in page.search_for(token):
                    c.check(token not in positions, f'目录条目“{token}”只应出现一次')
                    positions[token] = (page.number, pc.read_geometry(page).column(rect.x0))
                    links = [link for link in page.get_links() if link['from'].intersects(rect)]
                    c.check(links and all(link.get('page') == expected[token] for link in links),
                            f'目录条目“{token}”应链接到第 {expected[token] + 1} 页',
                            [link.get('page') for link in links])
            for link in page.get_links():
                c.check(0 <= link.get('page', -1) < len(doc), '链接目标应在文档范围内', link.get('page'))
                r = link['from']
                g = pc.read_geometry(page)
                c.check(r.x0 >= g.left - 1 and r.x1 <= g.starts[-1] + g.column_width + 1,
                        '链接区域应在版心内', r)
                c.check(any(r.x0 >= x - 1 and r.x1 <= x + g.column_width + 1 for x in g.starts),
                        '链接区域不应跨栏', r)
        c.check(positions.keys() == expected.keys(), '每个目录条目都应出现', sorted(set(expected) - set(positions)))

        def same_column(a, b):
            return a in positions and b in positions and positions[a] == positions[b]

        # 父标题与首个子条目同栏，不捆绑整个章节。
        for i in range(1, 9):
            c.check(same_column(f'TOC-Chapter-{i:02d}', f'TOC-Topic-{i:02d}-1'),
                    f'TOC-Chapter-{i:02d} 应与首个二级条目同栏')
            for j in (1, 2):
                c.check(same_column(f'TOC-Topic-{i:02d}-{j}', f'TOC-Item-{i:02d}-{j}-1'),
                        f'TOC-Topic-{i:02d}-{j} 应与首个三级条目同栏')

sys.exit(c.finish())
