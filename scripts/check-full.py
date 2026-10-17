"""检查完整横版或代码版 PDF 的文字是否越出所在栏；需要 PyMuPDF。

规则（2026-10-14 用户确认）：
- 两栏文字越过各自栏右边界时统一输出警告（容差 0.5 pt），不导致检查失败。
- 不设置接受清单或溢出上限；越过纸边也仅附加提示。PDF 读取等运行错误仍正常报错。
- 中文全角标点按字形前进宽度计算时会虚报约 6.7 pt，跳过；页眉、页脚与通栏目录标题跳过。
- 以右栏左边界区分两栏：字框起点在右栏之前的字符都计入左栏，完整落在栏距内的越栏文字
  也会报出。右栏行首的“等标点经 xeCJK 压缩后字框约提前 0.5 pt，故留 1 pt 容差。
- 扉页通栏居中、不分栏，以 44 pt 书名识别并整页跳过（2026-10-15 起横版、代码版均有扉页）。
- 几何自检（2026-10-16）：先核对每页为 A4 横向，且正文中左右两栏的左、右缘各至少有 20 行对齐
  （容差 0.2 mm）。布局参数改了而这里的常量没有同步时直接报错，不输出不可信的越栏结果。

用法（从任意目录）：python3 scripts/check-full.py [PDF 路径]
默认检查 build/landscape/main-landscape.pdf，即 ./run.sh landscape 的产物；代码版传入
build/code/main-code.pdf（栏宽与栏距与横版相同）。
返回值：0 检查完成（越栏只输出警告）；1 几何与本脚本的常量不符；2 找不到 PDF。
"""
from pathlib import Path
import sys
import unicodedata

try:
    import fitz
except ImportError:
    sys.exit('缺少 PyMuPDF：请先运行 python3 -m pip install --user pymupdf')

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / 'build/landscape/main-landscape.pdf'

MM = 72 / 25.4
PAGE_WIDTH, PAGE_HEIGHT = 297 * MM, 210 * MM   # A4 横向
LEFT_START = 12 * MM                    # 左栏左边界
LEFT_END = (12 + 132.5) * MM            # 左栏右边界
RIGHT_START = (12 + 132.5 + 8) * MM     # 右栏左边界
RIGHT_END = (12 + 132.5 * 2 + 8) * MM   # 右栏右边界
OVERFLOW_TOLERANCE = 0.5
RIGHT_START_TOLERANCE = 1.0             # 右栏行首标点的字框可略早于栏左缘
HEADER_BOTTOM = 48                      # 页眉区域，与 preamble/tests/pdfcheck.py 一致
FOOTER_TOP = 548                        # 页脚区域：版心下缘约 544 pt，页码字顶约 554 pt
TITLE_SIZE = 20                         # 目录通栏标题为 22 pt
TITLEPAGE_SIZE = 40                     # 扉页书名为 44 pt，所在页整页跳过
EDGE_TOLERANCE = 0.2 * MM               # 几何自检：行首、行尾与栏边的容差
EDGE_MIN_LINES = 20                     # 几何自检：每条栏边至少对齐的正文行数
EDGES = (('左栏左缘', LEFT_START, 'start'), ('左栏右缘', LEFT_END, 'end'),
         ('右栏左缘', RIGHT_START, 'start'), ('右栏右缘', RIGHT_END, 'end'))


def is_card_line_number(span):
    """只跳过位于规定框外位置的行号，不笼统忽略栏距中的小字或数字。"""
    text = ''.join(ch['c'] for ch in span['chars']).strip()
    return (text.isascii() and text.isdigit() and 'Maple' in span['font']
            and abs(span['size'] - 4 * 72 / 72.27) < .02
            and span['color'] == 0x808080
            and any(abs(span['bbox'][2] - (edge - MM)) < .05
                    for edge in (LEFT_START, RIGHT_START)))


def read(path):
    """读取 PDF，返回 (逐字记录, 文字行记录, 各页尺寸)。

    逐字记录为 (页码, 页宽, 字符, 左端, 右端, 顶边, 字号)；文字行记录为 (页码, 左端, 右端, 顶边)；
    页面尺寸为 (页码, 宽, 高)。坐标单位为 bp。
    """
    chars, lines, sizes = [], [], []
    with fitz.open(path) as doc:
        for page in doc:
            number, width = page.number + 1, page.rect.width
            sizes.append((number, page.rect.width, page.rect.height))
            for block in page.get_text('rawdict')['blocks']:
                for line in block.get('lines', []):
                    text = []
                    boxes = []
                    for span in line['spans']:
                        if is_card_line_number(span):
                            continue
                        for ch in span['chars']:
                            x0, y0, x1, _ = ch['bbox']
                            chars.append((number, width, ch['c'], x0, x1, y0, span['size']))
                            text.append(ch['c'])
                            boxes.append(ch['bbox'])
                    if ''.join(text).strip():
                        x0 = min(b[0] for b in boxes)
                        y0 = min(b[1] for b in boxes)
                        x1 = max(b[2] for b in boxes)
                        lines.append((number, x0, x1, y0))
    return chars, lines, sizes


def title_pages(chars):
    """含 44 pt 书名的页（扉页），整页跳过。"""
    return sorted({page for page, *_, size in chars if size >= TITLEPAGE_SIZE})


def geometry_problems(lines, sizes, skipped):
    """核对纸张尺寸与四条栏边是否与本脚本的常量一致；返回问题说明列表，空表示一致。"""
    problems = []
    wrong = [(page, width, height) for page, width, height in sizes
             if abs(width - PAGE_WIDTH) > 0.5 or abs(height - PAGE_HEIGHT) > 0.5]
    if wrong:
        page, width, height = wrong[0]
        problems.append(f'{len(wrong)} 页不是 A4 横向，例如第 {page} 页为 {width / MM:.1f} × {height / MM:.1f} mm')
    body = [(x0, x1) for page, x0, x1, top in lines
            if page not in skipped and HEADER_BOTTOM <= top < FOOTER_TOP]
    for name, edge, side in EDGES:
        hits = sum(abs((x0 if side == 'start' else x1) - edge) <= EDGE_TOLERANCE for x0, x1 in body)
        if hits < EDGE_MIN_LINES:
            problems.append(f'{name}应在 {edge / MM:.1f} mm，但只有 {hits} 行正文与之对齐'
                            f'（至少应有 {EDGE_MIN_LINES} 行）')
    return problems


def ignored(text, top, size):
    if (not text or text.isspace() or top < HEADER_BOTTOM or top >= FOOTER_TOP
            or size >= TITLE_SIZE):
        return True
    c = text[0]
    return ord(c) >= 0x2E80 and unicodedata.category(c).startswith('P')


def overflows(chars, skipped):
    """按页、栏汇总最大越界量：{(页码, 栏): (越界量, 末字, 是否越过纸边, 是否伸到右栏位置)}。"""
    worst = {}
    for page, width, text, x0, x1, top, size in chars:
        if page in skipped or ignored(text, top, size):
            continue
        # 不能以左栏右边界分栏：越栏文字可能整个落在栏距内，按右栏计算会得到负溢出而漏报。
        if x0 < RIGHT_START - RIGHT_START_TOLERANCE:
            column, overflow = '左', x1 - LEFT_END
        else:
            column, overflow = '右', x1 - RIGHT_END
        if overflow <= OVERFLOW_TOLERANCE:
            continue
        key = (page, column)
        if overflow > worst.get(key, (0, ''))[0]:
            worst[key] = (overflow, text, x1 > width, x1 >= RIGHT_START)
    return worst


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    pdf = Path(argv[0]) if argv else DEFAULT_PDF
    if not pdf.is_file():
        print(f'找不到 {pdf}；请先运行 ./run.sh landscape 或 ./run.sh code。', file=sys.stderr)
        return 2
    chars, lines, sizes = read(pdf)
    skipped = title_pages(chars)
    problems = geometry_problems(lines, sizes, set(skipped))
    if problems:
        print(f'{pdf.name}: 纸张或栏边与本脚本的几何常量不符，不输出越栏结果：', file=sys.stderr)
        for problem in problems:
            print('  - ' + problem, file=sys.stderr)
        print('布局参数改变时，请同步修改 scripts/check-full.py 中的几何常量。', file=sys.stderr)
        return 1
    worst = overflows(chars, set(skipped))
    for (page, column), (overflow, text, off_page, reaches_right) in sorted(worst.items()):
        mm = overflow / MM
        # 伸到右栏位置之后的字符无法与右栏正文区分，只能报出下限。
        note = '，已伸至右栏位置，实际越界可能更大' if column == '左' and reaches_right else ''
        if off_page:
            note += '，已越过纸边'
        print(f'警告：第 {page} 页{column}栏：越界 {overflow:.1f} pt（{mm:.1f} mm），末字“{text}”{note}',
              file=sys.stderr)
    note = f'；跳过扉页：第 {"、".join(map(str, skipped))} 页' if skipped else ''
    print(f'{pdf.name}: 检查完成，越栏警告 {len(worst)} 项（按页、栏汇总最大越界量{note}）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
