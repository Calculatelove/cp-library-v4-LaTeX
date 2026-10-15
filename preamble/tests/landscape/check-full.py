"""检查完整横版 PDF 的文字是否越出所在栏；需要 PyMuPDF（缺少时可用 pdfplumber）。

规则（2026-10-14 用户确认）：
- 两栏文字越过各自栏右边界时统一输出警告（容差 0.5 pt），不导致检查失败。
- 不设置接受清单或溢出上限；越过纸边也仅附加提示。PDF 读取等运行错误仍正常报错。
- 中文全角标点按字形前进宽度计算时会虚报约 6.7 pt，跳过；页眉、页脚与通栏目录标题跳过。
- 以右栏左边界区分两栏：字框起点在右栏之前的字符都计入左栏，完整落在栏距内的越栏文字
  也会报出。右栏行首的“等标点经 xeCJK 压缩后字框约提前 0.5 pt，故留 1 pt 容差。
- 扉页通栏居中、不分栏，以 44 pt 书名识别并整页跳过（2026-10-15 起横版、代码版均有扉页）。

用法（从任意目录）：python3 preamble/tests/landscape/check-full.py [PDF 路径]
默认检查 build/landscape/main-landscape.pdf，即 ./run.sh landscape 的产物。
"""
from pathlib import Path
import sys
import unicodedata

ROOT = Path(__file__).resolve().parents[3]
PDF = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / 'build/landscape/main-landscape.pdf'

MM = 72 / 25.4
LEFT_END = (12 + 132.5) * MM            # 左栏右边界
RIGHT_START = (12 + 132.5 + 8) * MM     # 右栏左边界
RIGHT_END = (12 + 132.5 * 2 + 8) * MM   # 右栏右边界
OVERFLOW_TOLERANCE = 0.5
RIGHT_START_TOLERANCE = 1.0             # 右栏行首标点的字框可略早于栏左缘
HEADER_BOTTOM = 48                      # 页眉区域，与 check-layout.py 一致
FOOTER_TOP = 548                        # 页脚区域：版心下缘约 544 pt，页码字顶约 554 pt
TITLE_SIZE = 20                         # 目录通栏标题为 22 pt
TITLEPAGE_SIZE = 40                     # 扉页书名为 44 pt，所在页整页跳过


def chars_pymupdf(path):
    import fitz
    with fitz.open(path) as doc:
        for page in doc:
            width = page.rect.width
            for block in page.get_text('rawdict')['blocks']:
                for line in block.get('lines', []):
                    for span in line['spans']:
                        for ch in span['chars']:
                            x0, y0, x1, _ = ch['bbox']
                            yield page.number + 1, width, ch['c'], x0, x1, y0, span['size']


def chars_pdfplumber(path):
    import pdfplumber
    with pdfplumber.open(path) as pdf:
        for number, page in enumerate(pdf.pages, 1):
            for ch in page.chars:
                yield number, page.width, ch['text'], ch['x0'], ch['x1'], ch['top'], ch['size']


def chars(path):
    try:
        import fitz  # noqa: F401
        return chars_pymupdf(path)
    except ImportError:
        return chars_pdfplumber(path)


def ignored(text, top, size):
    if (not text or text.isspace() or top < HEADER_BOTTOM or top >= FOOTER_TOP
            or size >= TITLE_SIZE):
        return True
    c = text[0]
    return ord(c) >= 0x2E80 and unicodedata.category(c).startswith('P')


records = list(chars(PDF))
title_pages = sorted({page for page, *_, size in records if size >= TITLEPAGE_SIZE})
worst = {}
for page, width, text, x0, x1, top, size in records:
    if page in title_pages or ignored(text, top, size):
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

for (page, column), (overflow, text, off_page, reaches_right) in sorted(worst.items()):
    mm = overflow / MM
    # 伸到右栏位置之后的字符无法与右栏正文区分，只能报出下限。
    note = '，已伸至右栏位置，实际越界可能更大' if column == '左' and reaches_right else ''
    if off_page:
        note += '，已越过纸边'
    print(f'警告：第 {page} 页{column}栏：越界 {overflow:.1f} pt（{mm:.1f} mm），末字“{text}”{note}', file=sys.stderr)

skipped = f'；跳过扉页：第 {"、".join(map(str, title_pages))} 页' if title_pages else ''
print(f'{PDF.name}: 检查完成，越栏警告 {len(worst)} 项（按页、栏汇总最大越界量{skipped}）')
