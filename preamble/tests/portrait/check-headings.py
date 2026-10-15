"""检查四、五级标题的字体、独立成行、与后文同页、竖向间距及书签；需要 PyMuPDF。

用法（从任意目录）：python3 preamble/tests/portrait/check-headings.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdfcheck as pc  # noqa: E402

c = pc.Checker('竖版四、五级标题')
HEADINGS = [
    '四级标题：紧接三级', '四级标题：正文之间', '四级标题：后接行间公式',
    '四级标题：行间公式之后', '四级标题：引用块之后', '四级标题：后接列表',
    '四级标题：后接五级标题', '五级标题：与四级同字号', '一个用于检验四级标题换行的长标题',
    '页底四级标题：后接正文', '页底四级标题：后接行间公式',
]


def is_heading(row):
    """标题行内的文字全为苹方 Semibold 10.5 pt，没有同行的正文字体。"""
    spans = [s for s in row['spans'] if 'Math' not in s['font']]
    return bool(spans) and all(
        'PingFang' in s['font'] and 'Semibold' in s['font']
        and abs(pc.to_pt(s['size']) - 10.5) < 0.05 for s in spans)


pages, bookmarks = [], {}
with c.section('读取样张'):
    with c.open(pc.BUILD / 'portrait/heading-levels.pdf', '请先运行 bash preamble/tests/portrait/run.sh') as doc:
        # 忽略上下标、页眉页码等小于 9.5 bp 的行；比较文字时去掉空格。
        pages = [pc.text_rows(page, min_size=9.5) for page in doc]
        for rows in pages:
            for row in rows:
                row['flat'] = row['text'].replace(' ', '')
        bookmarks = {title.replace(' ', ''): level for level, title, _ in doc.get_toc()}
if not pages:
    sys.exit(c.finish())


def lookup(prefix):
    return [(i, j) for i, rows in enumerate(pages)
            for j, row in enumerate(rows) if row['flat'].startswith(prefix)]


def find(prefix):
    hits = lookup(prefix)
    c.require(len(hits) == 1, f'应恰好找到一处“{prefix}”', hits)
    return hits[0]


def above(prefix):
    """与上一行的基线距，单位 TeX pt。"""
    i, j = find(prefix)
    c.require(j > 0, f'“{prefix}”上方应有一行')
    return pc.to_pt(pages[i][j]['y'] - pages[i][j - 1]['y'])


def below(prefix):
    """与下一行的基线距，单位 TeX pt。"""
    i, j = find(prefix)
    c.require(j + 1 < len(pages[i]), f'“{prefix}”下方应有一行')
    return pc.to_pt(pages[i][j + 1]['y'] - pages[i][j]['y'])


with c.section('标题字体、独立成行与后文同页'):
    for prefix in HEADINGS:
        hits = lookup(prefix)
        if not c.check(len(hits) == 1, f'应恰好找到一处“{prefix}”', hits):
            continue
        i, j = hits[0]
        rows = pages[i]
        c.check(is_heading(rows[j]), f'“{prefix}”应为苹方 Semibold 10.5 pt 的独立标题行',
                [(s['font'], round(s['size'], 2)) for s in rows[j]['spans']])
        # 长标题的续行、紧随的五级标题同属标题；其后第一行正文或公式须与标题同页。
        k = j + 1
        while k < len(rows) and is_heading(rows[k]):
            k += 1
        c.check(k < len(rows), f'“{prefix}”不应与后文分页')

with c.section('竖向间距'):
    # 基线距：四级标题上方 24 pt、下方 20 pt，均小于三级标题。
    level4 = above('四级标题：正文之间'), below('四级标题：正文之间')
    level3 = above('三级标题：正文之后'), below('三级标题：正文之后')
    c.check(abs(level4[0] - 24) < 1 and abs(level4[1] - 20) < 1, '四级标题上方约 24 pt、下方约 20 pt', level4)
    c.check(level3[0] > level4[0] + 1 and level3[1] > level4[1], '三级标题的上下间距应大于四级', level3, level4)
    adjacent = above('四级标题：紧接三级')
    c.check(15 < adjacent < level4[0], '紧接三级标题时，四级标题上方间距应在 15 pt 与常规值之间', adjacent)
    print(f'  四级上/下 {level4[0]:.1f}/{level4[1]:.1f} pt，三级上/下 {level3[0]:.1f}/{level3[1]:.1f} pt，'
          f'三级到四级 {adjacent:.1f} pt')

with c.section('页底边界'):
    # 标题移到下一页页首，不留在上一页页底。
    for filler, heading in (('边界一：', '页底四级标题：后接正文'),
                            ('边界二：', '页底四级标题：后接行间公式')):
        (fi, _), (hi, hj) = find(filler), find(heading)
        c.check((hi, hj) == (fi + 1, 0), f'“{heading}”应移到下一页页首', (fi, hi, hj))

with c.section('书签层级'):
    c.check(bookmarks.get('四级标题：正文之间') == 4, '四级标题的书签应为第 4 级',
            bookmarks.get('四级标题：正文之间'))
    c.check(bookmarks.get('五级标题：与四级同字号') == 5, '五级标题的书签应为第 5 级',
            bookmarks.get('五级标题：与四级同字号'))

sys.exit(c.finish())
