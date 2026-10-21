"""逐页比较改动前后的 PDF：文字及其字体、字号、颜色与位置，纸张、矢量图形、图片、链接与书签；需要 PyMuPDF。

用于判断排版改动的影响：改动前构建整书与样张并保存基线，改动后重新构建，再与基线比较；
导言区改动的比较范围见 preamble/AGENTS.md。坐标与字号取到 0.01 bp，更小的差别不计。

用法（从任意目录）：
  python3 scripts/compare-pdf.py --save <基线目录>   保存已构建的三版整书与回归样张；须为新目录或空目录
  python3 scripts/compare-pdf.py <基线目录>          与项目中相对路径相同的 PDF 逐份比较
  python3 scripts/compare-pdf.py <旧> <新>           比较两个 PDF，或两个目录中相对路径相同的 PDF
返回值：0 全部相同；1 有差异或缺少对应的 PDF；2 用法错误或找不到输入。
"""
from collections import defaultdict
import difflib
from pathlib import Path
import re
import shutil
import sys

try:
    import fitz
except ImportError:
    sys.exit('缺少 PyMuPDF：请先运行 python3 -m pip install --user pymupdf')

ROOT = Path(__file__).resolve().parents[1]
EDITIONS = ('portrait', 'landscape', 'code')
LISTED_PAGES = 8      # 页码最多列出几页
LISTED_CHANGES = 5    # 字体、字号、颜色的“旧 → 新”最多列出几种
LISTED_CHARS = 10     # 每种变化最多列出几个涉及的字符
USAGE = ('用法：python3 scripts/compare-pdf.py --save <基线目录>\n'
         '      python3 scripts/compare-pdf.py <基线目录>\n'
         '      python3 scripts/compare-pdf.py <旧> <新>')


def current_pdfs():
    """基线包含的 PDF（相对项目根目录）：三版整书，以及各组 run.sh 列出的样张。"""
    paths = [f'build/{edition}/main-{edition}.pdf' for edition in EDITIONS]
    for script in sorted(ROOT.glob('preamble/tests/*/run.sh')):
        names = re.search(r'^\s*set -- (.+)$', script.read_text(encoding='utf-8'), re.M)[1].split()
        paths += [f'preamble/tests/build/{script.parent.name}/{name}.pdf' for name in names]
    return paths


def rounded(values):
    return tuple(round(value, 2) for value in values)


def read(path):
    """逐页读取纸张、逐字的 (字符, 字体, 字号, 颜色, x, y)、矢量图形、图片与链接，以及书签。"""
    with fitz.open(path) as doc:
        pages = []
        for page in doc:
            chars = [(ch['c'], span['font'], round(span['size'], 2), span['color'], *rounded(ch['origin']))
                     for block in page.get_text('rawdict')['blocks'] for line in block.get('lines', [])
                     for span in line['spans'] for ch in span['chars'] if not ch['c'].isspace()]
            pages.append({
                'size': rounded(page.rect),
                'chars': chars,
                'drawings': [(rounded(d['rect']), d.get('fill'), d.get('color'), d.get('width'))
                             for d in page.get_drawings()],
                'images': [rounded(info['bbox']) for info in page.get_image_info()],
                'links': [(link.get('uri'), link.get('page'), None if link.get('to') is None else rounded(link['to']),
                           rounded(link['from'])) for link in page.get_links()],
            })
        return pages, doc.get_toc()


def page_list(numbers):
    numbers = sorted(numbers)
    more = f' 等 {len(numbers)} 页' if len(numbers) > LISTED_PAGES else ''
    return f'第 {"、".join(map(str, numbers[:LISTED_PAGES]))} 页{more}'


def matched_chars(old_chars, new_chars):
    """文字相同时逐字配对；不同时按字符对齐，只配对两边相同的片段。返回配对与首处不同。"""
    old_text, new_text = (''.join(ch[0] for ch in chars) for chars in (old_chars, new_chars))
    if old_text == new_text:
        return list(zip(old_chars, new_chars)), None
    blocks = difflib.SequenceMatcher(None, old_text, new_text, autojunk=False).get_opcodes()
    pairs = [pair for tag, i1, i2, j1, j2 in blocks if tag == 'equal'
             for pair in zip(old_chars[i1:i2], new_chars[j1:j2])]
    # 首处不同连同前面几个字一起摘出：只摘不同的片段时，相近的字串会被对齐成零碎的几段。
    _, i, _, j, _ = next(block for block in blocks if block[0] != 'equal')
    return pairs, (old_text[max(i - 6, 0):i + 14] or '（无）', new_text[max(j - 6, 0):j + 14] or '（无）')


def differences(old, new):
    """两份读取结果的差异，每类一行；完全相同时返回空列表。"""
    (old_pages, old_toc), (new_pages, new_toc) = old, new
    report = [f'页数 {len(old_pages)} → {len(new_pages)}'] if len(old_pages) != len(new_pages) else []
    pages = defaultdict(set)                         # 类别 → 页码
    changes = defaultdict(dict)                      # 字体、字号、颜色 → {(旧, 新): [次数, 涉及的字符]}
    first_text, moved, shift = None, 0, 0
    for number, (a, b) in enumerate(zip(old_pages, new_pages), 1):
        for key, name in (('size', '纸张'), ('drawings', '矢量图形'), ('images', '图片'), ('links', '链接')):
            if a[key] != b[key]:
                pages[name].add(number)
        pairs, text = matched_chars(a['chars'], b['chars'])
        if text:
            pages['文字'].add(number)
            first_text = first_text or (number, *text)
        for x, y in pairs:
            for index, name in ((1, '字体'), (2, '字号'), (3, '颜色')):
                if x[index] != y[index]:
                    entry = changes[name].setdefault((x[index], y[index]), [0, {}])
                    entry[0] += 1
                    entry[1][x[0]] = None
                    pages[name].add(number)
            if x[4:] != y[4:]:
                moved += 1
                shift = max(shift, abs(x[4] - y[4]), abs(x[5] - y[5]))
                pages['位置'].add(number)
    if pages['纸张']:
        report.append(f'纸张：{page_list(pages["纸张"])}')
    if first_text:
        report.append(f'文字：{page_list(pages["文字"])}；第 {first_text[0]} 页首处 {first_text[1]} → {first_text[2]}')
    for name, show in (('字体', str), ('字号', str), ('颜色', lambda value: f'{value:06X}')):
        if changes[name]:
            ranked = sorted(changes[name].items(), key=lambda item: -item[1][0])
            listed = '；'.join(f'{show(before)} → {show(after)} {count} 处，涉及 {"、".join(list(chars)[:LISTED_CHARS])}'
                               + (' 等' if len(chars) > LISTED_CHARS else '')
                               for (before, after), (count, chars) in ranked[:LISTED_CHANGES])
            more = f'；另有 {len(ranked) - LISTED_CHANGES} 种' if len(ranked) > LISTED_CHANGES else ''
            report.append(f'{name}：{listed}{more}（{page_list(pages[name])}）')
    if moved:
        report.append(f'位置：{moved} 字移动，最大 {shift:.2f} bp（{page_list(pages["位置"])}）')
    for name in ('矢量图形', '图片', '链接'):
        if pages[name]:
            report.append(f'{name}：{page_list(pages[name])}')
    if old_toc != new_toc:
        changed = sum(x != y for x, y in zip(old_toc, new_toc)) + abs(len(old_toc) - len(new_toc))
        report.append(f'书签：{changed} 项不同')
    return report


def save(target):
    """把已构建的整书与样张复制到新的基线目录，保留相对路径；不覆盖、不删除已有文件。"""
    if target.exists() and (not target.is_dir() or any(target.iterdir())):
        print(f'{target} 已存在且不是空目录；请换一个新目录，以免与旧基线混在一起。', file=sys.stderr)
        return 2
    saved = 0
    for rel in current_pdfs():
        if not (ROOT / rel).is_file():
            print(f'跳过尚未构建的 {rel}', file=sys.stderr)
            continue
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / rel, target / rel)
        saved += 1
    if not saved:
        print('没有已构建的整书或样张；请先运行 ./run.sh all 与 scripts/check.sh --full。', file=sys.stderr)
        return 2
    print(f'已把 {saved} 份 PDF 保存到 {target}')
    return 0


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) == 2 and argv[0] == '--save':
        return save(Path(argv[1]))
    if not 1 <= len(argv) <= 2 or any(arg.startswith('-') for arg in argv):
        print(USAGE, file=sys.stderr)
        return 2
    old, new = Path(argv[0]), Path(argv[1]) if len(argv) == 2 else ROOT
    for path in (old, new):
        if not path.exists():
            print(f'找不到 {path}', file=sys.stderr)
            return 2
    if old.is_dir() and new.is_dir():
        pairs = [(path, new / path.relative_to(old)) for path in sorted(old.rglob('*.pdf'))]
    elif old.is_file() and new.is_file():
        pairs = [(old, new)]
    else:
        print('两个参数须同为 PDF 或同为目录；只给一个参数时，它须是 --save 保存的基线目录。', file=sys.stderr)
        return 2
    if not pairs:
        print(f'{old} 中没有 PDF', file=sys.stderr)
        return 2
    same = changed = missing = 0
    for a, b in pairs:
        label = b.relative_to(new) if new.is_dir() else b
        if not b.is_file():
            print(f'{label}：缺少对应的 PDF')
            missing += 1
            continue
        report = differences(read(a), read(b))
        if report:
            print(f'{label}：有差异')
            print('\n'.join('  ' + line for line in report), flush=True)
            changed += 1
        else:
            same += 1
    print(f'共比较 {len(pairs)} 份：相同 {same} 份，有差异 {changed} 份，缺少对应 PDF {missing} 份')
    return 1 if changed or missing else 0


if __name__ == '__main__':
    sys.exit(main())
