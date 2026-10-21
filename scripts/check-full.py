"""整书双栏越界检查，版心与扉页标记读取 PDF 编译时嵌入的记录。

越栏只输出警告，不设上限或接受清单；缺少版心记录的旧 PDF 须重新编译。
用法：python3 scripts/check-full.py [PDF]；默认 build/landscape/main-landscape.pdf。
返回 0 表示完成，1 表示版心记录无效或不是双栏，2 表示找不到 PDF。
"""
from pathlib import Path
import re
import sys
import unicodedata

try:
    import fitz
except ImportError:
    sys.exit('缺少 PyMuPDF：请先运行 python3 -m pip install --user pymupdf')

sys.path.insert(0, str(Path(__file__).resolve().parent))
from pdf_geometry import read_geometry, is_titlepage, line_number_spans

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_PDF = ROOT / 'build/landscape/main-landscape.pdf'
MM = 72 / 25.4
OVERFLOW_TOLERANCE = 0.5
STAMP = re.compile(r'LAST COMMIT (\d{4}-\d{2}-\d{2}) ([0-9a-f]{7,40})\b( 含未提交修改)?')


def read(path):
    """逐字记录保留原格式；另返回逐页版心、扉页集合与文字片段。"""
    chars, geometries, skipped, texts = [], {}, set(), []
    with fitz.open(path) as doc:
        for page in doc:
            number = page.number + 1
            g = geometries[number] = read_geometry(page)
            if is_titlepage(page):
                skipped.add(number)
            elif g.columns != 2:
                raise ValueError('整书越栏检查只接受双栏 PDF')
            numbers = {tuple(s['bbox']) for s in line_number_spans(page, g)}
            for block in page.get_text('rawdict')['blocks']:
                for line in block.get('lines', []):
                    # 目录通栏标题由文本识别，避免依赖标题字号。
                    title = ''.join(ch['c'] for s in line['spans'] for ch in s['chars']).strip() == '目录'
                    for span in line['spans']:
                        texts.append((number, ''.join(ch['c'] for ch in span['chars'])))
                        if tuple(span['bbox']) in numbers or title:
                            continue
                        for ch in span['chars']:
                            x0, _, x1, _ = ch['bbox']
                            chars.append((number, g.width, ch['c'], x0, x1, ch['origin'][1], span['size']))
    return chars, geometries, skipped, texts


def commit_stamp(texts):
    """从扉页的文字片段读出提交信息，返回 (日期, 短哈希, 是否含未提交修改)；找不到时返回 None。"""
    match = STAMP.search(' '.join(t.strip() for t in texts if t.strip()))
    return (match[1], match[2], bool(match[3])) if match else None


def ignored(text, baseline, geometry):
    if not text or text.isspace() or baseline < geometry.top - 1 or baseline > geometry.bottom + 1:
        return True
    return ord(text[0]) >= 0x2E80 and unicodedata.category(text[0]).startswith('P')


def overflows(chars, skipped, geometries):
    """按页、栏汇总最大右侧越界量；左栏整字落入栏距仍属于左栏。"""
    worst = {}
    for page, width, text, x0, x1, baseline, size in chars:
        g = geometries[page]
        if page in skipped or ignored(text, baseline, g):
            continue
        index = g.column(x0)
        column = '左' if index == 0 else '右'
        overflow = x1 - (g.starts[index] + g.column_width)
        if overflow <= OVERFLOW_TOLERANCE:
            continue
        key = page, column
        if overflow > worst.get(key, (0, ''))[0]:
            worst[key] = (overflow, text, x1 > width, x1 >= g.starts[1])
    return worst


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    pdf = Path(argv[0]) if argv else DEFAULT_PDF
    if not pdf.is_file():
        print(f'找不到 {pdf}；请先运行 ./run.sh landscape 或 ./run.sh code。', file=sys.stderr)
        return 2
    try:
        chars, geometries, skipped, texts = read(pdf)
    except ValueError as error:
        print(f'{pdf.name}: {error}，不输出越栏结果。', file=sys.stderr)
        return 1
    first = min(skipped) if skipped else None
    stamp = commit_stamp([text for page, text in texts if page == first])
    if stamp:
        date, commit, dirty = stamp
        print(f'{pdf.name}: 扉页提交 {commit}（{date}{"，含未提交修改" if dirty else ""}）', flush=True)
    else:
        print(f'{pdf.name}: 扉页上没有提交信息', flush=True)
    worst = overflows(chars, set(skipped), geometries)
    for (page, column), (overflow, text, off_page, reaches_right) in sorted(worst.items()):
        mm = overflow / MM
        # 伸到右栏位置之后的字符无法与右栏正文区分，只能报出下限。
        note = '，已伸至右栏位置，实际越界可能更大' if column == '左' and reaches_right else ''
        if off_page:
            note += '，已越过纸边'
        print(f'警告：第 {page} 页{column}栏：越界 {overflow:.1f} pt（{mm:.1f} mm），末字“{text}”{note}',
              file=sys.stderr)
    note = f'；跳过扉页：第 {"、".join(map(str, sorted(skipped)))} 页' if skipped else ''
    print(f'{pdf.name}: 检查完成，越栏警告 {len(worst)} 项（按页、栏汇总最大越界量{note}）')
    return 0


if __name__ == '__main__':
    sys.exit(main())
