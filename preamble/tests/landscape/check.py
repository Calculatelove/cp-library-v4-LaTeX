"""检查横版或代码版样张的扉页、纸张、阅读流向、页眉、代码配色与跨栏、引用跨栏、列表符号、块间距、目录及图片；
需要 PyMuPDF。

用法（从任意目录）：python3 preamble/tests/landscape/check.py [landscape|code]
默认检查 preamble/tests/build/landscape/ 的样张；code 检查 preamble/tests/build/code/ 的样张。
代码版布局参数与横版相同，样张正文共用，只是没有 interfaces、images 两份样张；扉页另查书名后悬挂的“（代码版）”。
竖版的检查在 preamble/tests/portrait/check.py。
"""
from pathlib import Path
import re
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdfcheck as pc  # noqa: E402
from pdfcheck import fitz  # noqa: E402

SAMPLES = {
    'landscape': ('titlepage', 'flow', 'code-cards', 'syntax-colors', 'interfaces', 'block-spacing', 'toc-layout',
                  'images'),
    'code': ('titlepage', 'flow', 'code-cards', 'syntax-colors', 'block-spacing', 'toc-layout'),
}
edition = sys.argv[1] if len(sys.argv) > 1 else 'landscape'
if edition not in SAMPLES:
    sys.exit(f'未知版本：{edition}（可用 landscape 或 code）')
OUT = pc.BUILD / edition
HINT = f'请先运行 bash preamble/tests/{edition}/run.sh'
c = pc.Checker({'landscape': '横版', 'code': '代码版'}[edition])


def locate(doc, text):
    """正文区内唯一一处 text 的 (页码, 矩形)。"""
    found = [(i, r) for i, p in enumerate(doc) for r in p.search_for(text) if r.y0 > pc.HEADER_BOTTOM]
    c.require(len(found) == 1, f'应恰好找到一处“{text}”', found)
    return found[0]


def column(pos):
    """(页码, 栏)：栏 0 为左栏，1 为右栏。"""
    return pos[0], int(pos[1].x0 > pc.COLUMN_SPLIT)


def column_texts(page):
    """按栏裁剪正文区文字，返回 [(栏, 文字)]。"""
    half = page.rect.width / 2
    return [(col, page.get_text(clip=fitz.Rect(left, pc.HEADER_BOTTOM, right, pc.BODY_BOTTOM)))
            for col, (left, right) in enumerate([(0, half), (half, page.rect.width)])]


# 与 layout-landscape.tex、layout-code.tex 一致：\TitlePageSetup 的取值（mm），四边 12 mm。
pc.check_titlepage(c, OUT / 'titlepage.pdf', HINT,
                   dict(title=57, english=43.5, author=32, image=-17, stamp=-88, image_width=110, image_height=70),
                   landscape=True, side=12, bottom=12, header_bottom=pc.HEADER_BOTTOM,
                   marker='（代码版）' if edition == 'code' else '', body_header='扉页之后')

with c.section('flow：纸张、连续章节、栏边界与页眉'):
    with c.open(OUT / 'flow.pdf', HINT) as doc:
        for p in doc:
            c.check(abs(p.rect.width - pc.A4_LONG) < .1 and abs(p.rect.height - pc.A4_SHORT) < .1,
                    f'第 {p.number + 1} 页应为 A4 横向', p.rect)
        for text, expected in (('Alpha-body', (0, 0)), ('Beta-body', (0, 0)), ('Gamma-body', (0, 1)),
                               ('Delta-body', (1, 0)), ('Epsilon-body', (1, 0))):
            actual = column(locate(doc, text))
            c.check(actual == expected, f'“{text}”应位于第 {expected[0] + 1} 页{"左右"[expected[1]]}栏', actual)
        # 页眉显示页顶所在的章：左栏顶端新章取该章，否则取页首延续的章。
        for p, title in zip(doc, ['Alpha 章', 'Delta 章', 'Epsilon 章', 'Boundary-title']):
            header = p.get_text(clip=fitz.Rect(0, 0, p.rect.width, pc.HEADER_BOTTOM))
            c.check(title in header, f'第 {p.number + 1} 页页眉应为“{title}”', header.strip())
        for title, body in [('Boundary-title', 'Boundary-body'), ('Formula-title', 'FormulaBody')]:
            title_pos, body_pos = column(locate(doc, title)), column(locate(doc, body))
            c.check(title_pos == body_pos, f'“{title}”应与后文同栏', title_pos, body_pos)
            c.check(body_pos[1] == 1, f'“{body}”应移入右栏', body_pos)

for name in ('code-cards', 'syntax-colors'):
    with c.section(f'{name}：代码配色与内容'):
        with c.open(OUT / f'{name}.pdf', HINT) as doc:
            pc.check_code_palette(c, doc, name, sample_tokens=(name == 'syntax-colors'))
            if name == 'code-cards':
                pc.check_code_line_numbers(c, doc, twocolumn=True)
                segments, lines = [], []
                for i, page in enumerate(doc):
                    for col, text in column_texts(page):
                        numbers = re.findall(r'int landscape_value_(\d{3}) = (\d+);', text)
                        if numbers:
                            segments.append((i, col))
                            lines.extend(numbers)
                c.check(lines == [(f'{i:03d}', str(i)) for i in range(1, 101)], '100 行人工代码应完整、按序',
                        len(lines), lines[:3])
                c.check(segments[:3] == [(0, 0), (0, 1), (1, 0)], '代码卡片应从左栏跨到右栏、再到下一页',
                        segments[:3])
                c.check(sum(p.get_text().count('Landscape-long-card') for p in doc) == 1,
                        '跨栏跨页的卡片标题只应出现一次')
                c.check(column(locate(doc, 'Card-boundary')) == (0, 0), '“Card-boundary”应位于第 1 页左栏')

if 'interfaces' in SAMPLES[edition]:
    with c.section('interfaces：引用跨栏跨页'):
        with c.open(OUT / 'interfaces.pdf', HINT) as doc:
            numbers, segments = [], []
            for i, page in enumerate(doc):
                for col, text in column_texts(page):
                    found = re.findall(r'Quote-(\d{3})', text)
                    if found:
                        numbers.extend(found)
                        segments.append((i, col))
            c.check(numbers == [f'{i:03d}' for i in range(1, 66)], '65 段引用应完整、按序', len(numbers), numbers[:3])
            c.check(segments[:3] == [(0, 0), (0, 1), (1, 0)], '引用应从左栏跨到右栏、再到下一页', segments[:3])
    with c.section('interfaces：列表符号'):
        with c.open(OUT / 'interfaces.pdf', HINT) as doc:
            marks = [(char['c'], span['font'], round(span['size'], 2))
                     for page in doc for block in page.get_text('rawdict')['blocks']
                     for line in block.get('lines', ()) for span in line['spans']
                     for char in span['chars'] if char['c'] in '•◦']
            c.check([m[0] for m in marks] == ['•', '◦'], '一级、二级列表符号应依次为实心、空心圆点', marks)
            # Latin Modern 中两个圆点的外框相同；同字体、同字号即保证二级圆点与一级同径同高。
            c.check(len(set(m[1:] for m in marks)) == 1 and marks[0][1] == 'LMRoman10-Regular',
                    '两级圆点应为同字号的 Latin Modern Roman 常规体', marks)

with c.section('block-spacing：卡片、引用块、二级列表与分隔线'):
    with c.open(OUT / 'block-spacing.pdf', HINT) as doc:
        # 横版、代码版布局一致：行距 14 pt、段距 2 pt、盒前距 9 pt、盒后距 1.5 pt。
        pc.check_block_spacing(c, doc, baselineskip=14, parskip=2, box_before=9, box_after=1.5)

with c.section('toc-layout：目录'):
    with c.open(OUT / 'toc-layout.pdf', HINT) as doc:
        toc_pages = [p for p in doc if p.get_links()]
        c.require(len(toc_pages) >= 2, '目录应至少两页', len(toc_pages))
        heading = [r for r in doc[0].search_for('目录') if r.y0 < 100]
        c.require(len(heading) == 1, '首页应有一个“目录”标题', heading)
        c.check(abs((heading[0].x0 + heading[0].x1) / 2 - doc[0].rect.width / 2) < 1, '“目录”标题应通栏居中',
                heading[0])
        bookmarks = doc.get_toc(simple=False)
        c.require(bookmarks, '应有书签')
        c.check(len(bookmarks) == 90, '应有 90 个书签', len(bookmarks))
        c.check({b[0] for b in bookmarks} == {1, 2, 3, 4, 5}, '书签应有 5 个层级', sorted({b[0] for b in bookmarks}))
        c.check(all(b[3].get('collapse', True) for b in bookmarks), '初始只显示一级：可展开的书签都应闭合')
        body_first = bookmarks[0][2] - 1
        c.check(body_first == len(toc_pages), '正文应紧接目录页', body_first, len(toc_pages))
        c.check(any(r.x0 < 100 and r.y0 > pc.HEADER_BOTTOM for r in doc[body_first].search_for('TOC-Chapter-01')),
                '正文首章应位于左栏')
        expected = {b[1].split()[0]: b[2] - 1 for b in bookmarks if b[0] <= 3}
        positions = {}
        for page in toc_pages:
            text = page.get_text()
            c.check('Fourth-only' not in text and 'Fifth-only' not in text,
                    f'目录第 {page.number + 1} 页不应出现四、五级标题')
            c.check(not page.get_text(clip=fitz.Rect(0, 0, page.rect.width, pc.HEADER_BOTTOM)).strip(),
                    f'目录第 {page.number + 1} 页不应有页眉')
            for token in expected:
                for rect in page.search_for(token):
                    c.check(token not in positions, f'目录条目“{token}”只应出现一次')
                    positions[token] = (page.number, int(rect.x0 > pc.COLUMN_SPLIT))
                    links = [link for link in page.get_links() if link['from'].intersects(rect)]
                    c.check(links and all(link.get('page') == expected[token] for link in links),
                            f'目录条目“{token}”应链接到第 {expected[token] + 1} 页',
                            [link.get('page') for link in links])
            for link in page.get_links():
                c.check(0 <= link.get('page', -1) < len(doc), '链接目标应在文档范围内', link.get('page'))
                r = link['from']
                c.check(r.x0 >= 30 and r.x1 <= page.rect.width - 30, '链接区域应在页边距以内', r)
                c.check(r.x1 < pc.COLUMN_SPLIT or r.x0 > pc.COLUMN_SPLIT, '链接区域不应跨栏', r)
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

if 'images' in SAMPLES[edition]:
    with c.section('images：图片按栏宽'):
        with c.open(OUT / 'images.pdf', HINT) as doc:
            c.require(len(doc) == 1, '图片样张应为 1 页', len(doc))
            # mwe 提供矢量 PDF；通过 image 字母的左右位置及 TeX 盒宽断言检验两栏。
            page = doc[0]
            c.check(any(r.x0 < pc.COLUMN_SPLIT for r in page.search_for('A')), '图片 A 应位于左栏')
            c.check(any(r.x0 > pc.COLUMN_SPLIT for r in page.search_for('B')), '图片 B 应位于右栏')

sys.exit(c.finish())
