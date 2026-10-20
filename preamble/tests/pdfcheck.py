"""preamble/tests 各组 check.py 共用的 PDF 检查工具；需要 PyMuPDF。

- Checker：显式检查。失败只记录、不中断，最后统一汇总并以非零状态退出；
  不使用 assert，`python3 -O` 下照常生效。
- 单位：PDF 坐标的单位是 bp（1/72 in）。mm()、pt() 把毫米、TeX pt 换算为 bp，
  to_pt() 把 bp 换算回 TeX pt。不再使用含义容易混淆的 PT 常量。
- 几何常量：竖版的页眉线，横版与代码版共用的页眉线、正文下缘与栏分界；代码配色；读取文字行与代码文字的函数。
- 几版共用的断言：扉页 check_titlepage、代码配色 check_code_palette、框外行号 check_code_line_numbers、
  块间距 check_block_spacing。各版的 check.py 传入与本版布局一致的参数。
"""
from contextlib import contextmanager
from pathlib import Path
import re
import sys

try:
    import fitz
except ImportError:
    sys.exit('缺少 PyMuPDF：请先运行 python3 -m pip install --user pymupdf')

ROOT = Path(__file__).resolve().parents[2]
BUILD = ROOT / 'preamble/tests/build'
FIXTURES = ROOT / 'preamble/tests/fixtures'

BP_PER_MM = 72 / 25.4
BP_PER_PT = 72 / 72.27


def mm(value):
    """毫米换算为 bp。"""
    return value * BP_PER_MM


def pt(value):
    """TeX pt 换算为 bp。"""
    return value * BP_PER_PT


def to_pt(value):
    """bp 换算为 TeX pt。"""
    return value / BP_PER_PT


A4_SHORT, A4_LONG = mm(210), mm(297)

# 竖版页眉文字位于此线以上（页眉字框下缘约 53 bp，正文顶约 69 bp），单位 bp。
PORTRAIT_HEADER_BOTTOM = 60

# 横版与代码版（A4 横向双栏）共用的几何，单位 bp。
HEADER_BOTTOM = 48           # 页眉文字位于此线以上
BODY_BOTTOM = 560            # 正文区下缘，用于按栏裁剪文字
COLUMN_SPLIT = A4_LONG / 2   # 左右栏分界：纸张中线，位于 8 mm 栏距之内

# 代码配色：深灰正文、灰蓝关键字与数字、灰绿字符串、灰色注释。
CODE_TEXT, CODE_KEYWORD, CODE_STRING, CODE_COMMENT = 0x30343B, 0x506B82, 0x58715D, 0x70757D
CODE_PALETTE = {CODE_TEXT, CODE_KEYWORD, CODE_STRING, CODE_COMMENT}


class Abort(Exception):
    """require() 未通过：放弃当前小节余下的检查。"""


def _show(value):
    """失败详情的显示形式：小数保留两位，矩形只显示四个坐标。"""
    if isinstance(value, float):
        return f'{value:.2f}'
    if isinstance(value, (list, tuple)):
        inner = ', '.join(_show(v) for v in value)
        return f'[{inner}]' if isinstance(value, list) else f'({inner})'
    if all(hasattr(value, name) for name in ('x0', 'y0', 'x1', 'y1')):
        return f'Rect({value.x0:.2f}, {value.y0:.2f}, {value.x1:.2f}, {value.y1:.2f})'
    return repr(value)


class Checker:
    """按小节组织检查；每项失败都记录下来，最后一起报告。"""

    def __init__(self, name):
        self.name = name
        self.failures = []
        self.total = 0
        self.current = None

    def check(self, ok, message, *details):
        """记录一项检查，返回是否通过；details 只在失败时显示。"""
        self.total += 1
        if not ok:
            prefix = f'[{self.current}] ' if self.current else ''
            suffix = '；'.join(_show(d) for d in details)
            self.failures.append(prefix + message + (f'：{suffix}' if suffix else ''))
        return bool(ok)

    def require(self, ok, message, *details):
        """后续检查依赖的前提；不通过时记录失败并结束当前小节。"""
        if not self.check(ok, message, *details):
            raise Abort

    @contextmanager
    def section(self, title):
        """一个检查小节；其中的异常记为失败，不影响后续小节。"""
        self.current = title
        before = len(self.failures)
        try:
            yield
        except Abort:
            pass
        except Exception as error:  # 读取 PDF 出错等，记为失败后继续下一小节
            self.failures.append(f'[{title}] 检查脚本出错：{type(error).__name__}: {error}')
        finally:
            self.current = None
            print(('通过' if len(self.failures) == before else '未通过') + f'：{self.name} · {title}')

    def open(self, path, hint):
        """打开 PDF；不存在时记录失败并结束当前小节。hint 说明如何生成该 PDF。"""
        path = Path(path).resolve()
        shown = path.relative_to(ROOT) if ROOT in path.parents else path
        self.require(path.is_file(), f'找不到 {shown}，{hint}')
        return fitz.open(path)

    def finish(self):
        """打印汇总，返回退出码：全部通过为 0，否则为 1。"""
        if self.failures:
            print(f'{self.name}：{len(self.failures)} 项未通过（共 {self.total} 项检查）', file=sys.stderr)
            for failure in self.failures:
                print('  - ' + failure, file=sys.stderr)
            return 1
        print(f'{self.name}：{self.total} 项检查全部通过')
        return 0


def compact(text):
    """xeCJK 的中西文间距是胶而非空格字符，比较前去掉全部空白。"""
    return ''.join(text.split())


def text_rows(page, min_size=0):
    """按基线（容差 0.6 bp）归并文字，返回自上而下的行 {y, spans, text, x0, x1, bottom}。

    min_size 大于 0 时，只保留行内最大字号不小于它的行，用于忽略上下标、页眉页码等小字。
    """
    rows = []
    for block in page.get_text('dict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                if not span['text'].strip():
                    continue
                y = span['origin'][1]
                row = next((r for r in rows if abs(r['y'] - y) < 0.6), None)
                if row is None:
                    rows.append({'y': y, 'spans': [span]})
                else:
                    row['spans'].append(span)
    rows = [r for r in rows if max(s['size'] for s in r['spans']) >= min_size]
    for r in rows:
        r['spans'].sort(key=lambda s: s['origin'][0])
        r['text'] = ''.join(s['text'] for s in r['spans'])
        r['x0'] = min(s['bbox'][0] for s in r['spans'])
        r['x1'] = max(s['bbox'][2] for s in r['spans'])
        r['bottom'] = max(s['bbox'][3] for s in r['spans'])
    return sorted(rows, key=lambda r: r['y'])


def is_icon(char):
    """Nerd Font 图标位于 Unicode 私用区：U+E000–F8FF 与 U+F0000 起的辅助私用区。"""
    code = ord(char)
    return 0xE000 <= code <= 0xF8FF or code >= 0xF0000


def code_spans(doc):
    """Maple Mono 字体的代码文字；跳过只含空白或图标的 span（代码卡片标题的语言图标）。"""
    return [span for page in doc for block in page.get_text('dict')['blocks']
            for line in block.get('lines', []) for span in line['spans']
            if 'Maple' in span['font'] and not is_code_line_number(span)
            and not all(c.isspace() or is_icon(c) for c in span['text'])]


def is_code_line_number(span):
    """行号单独检查，不计入代码 token 的四色配色。"""
    return (span['text'].strip().isascii() and span['text'].strip().isdigit()
            and 'Maple' in span['font'] and abs(span['size'] - pt(4)) < .02
            and span['color'] == 0x808080)


def check_code_line_numbers(checker, doc, twocolumn=False):
    """检查框外位置、基线、逐行编号、折行与空行；复用 code-cards 样张。"""
    all_numbers = []
    for page in doc:
        spans = [s for b in page.get_text('dict')['blocks']
                 for line in b.get('lines', []) for s in line['spans']]
        numbers = [s for s in spans if is_code_line_number(s)]
        frames = [d['rect'] for d in page.get_drawings() if d.get('fill')
                  and all(abs(a - b / 255) < .005
                          for a, b in zip(d['fill'], (209, 209, 214)))]
        for s in numbers:
            # tcolorbox 先填充整个灰色外框，再覆盖白色代码区；取外框填充路径。
            matches = [r for r in frames
                       if r.y0 <= s['origin'][1] <= r.y1
                       and abs(r.x0 - s['bbox'][2] - mm(1)) < .05]
            checker.check(bool(matches), '行号须在左边框外 1 mm，且位于卡片高度内', s['text'], s['bbox'])
            checker.check(s['bbox'][0] >= 0, '行号不得越过纸边', s['text'])
            checker.check('Bold' not in s['font'] and 'Italic' not in s['font'], '行号须为常规正体')
        all_numbers.extend(numbers)
        # 同一源文件的逐行人工声明，包括跨栏、跨页；文件首行是注释。
        for s in spans:
            if 'landscape_value_' in s['text']:
                match = re.search(r'landscape_value_(\d{3})', s['text'])
                if match:
                    found = [n for n in numbers if abs(n['origin'][1] - s['origin'][1]) < .02
                             and 0 < s['bbox'][0] - n['bbox'][2] < mm(50)]
                    checker.check(len(found) == 1 and int(found[0]['text']) == int(match[1]) + 1,
                                  '人工长代码的行号须与源文件行一致', s['text'])
        if page.search_for('Wrap-start:'):
            start = next(s for s in spans if 'Wrap-start:' in s['text'])
            end = next(s for s in spans if 'final_line' in s['text'])
            selected = [n for n in numbers
                        if start['origin'][1] - .02 <= n['origin'][1] <= end['origin'][1] + .02
                        and 0 < start['bbox'][0] - n['bbox'][2] < mm(10)]
            checker.check([n['text'] for n in selected] == ['1', '2', '3', '4'],
                          '折行只标一次，空行也显示编号，新卡片从 1 开始', [n['text'] for n in selected])
            wrap_end = next(s for s in spans if 'Wrap-end.' in s['text'])
            checker.check(wrap_end['origin'][1] > start['origin'][1], '样张长行须实际折行')
    checker.require(all_numbers, '代码卡片应有 4 pt、808080、Maple 行号')
    if twocolumn:
        checker.check(any(int(s['text']) >= 100 for s in all_numbers), '应覆盖三位行号')


def check_code_palette(checker, doc, name, sample_tokens=False):
    """代码文字只用四种配色、常规直立字形；sample_tokens 时另查配色样张的全部颜色与关键字。"""
    spans = code_spans(doc)
    checker.require(spans, f'{name}：没有找到代码文字')
    wrong = [(s['text'], f"{s['color']:06X}", s['font']) for s in spans
             if s['color'] not in CODE_PALETTE or 'Bold' in s['font'] or 'Italic' in s['font']]
    checker.check(not wrong, f'{name}：代码文字须为四种配色之一，且不用粗体、斜体', *wrong[:5])
    if sample_tokens:
        colors = {s['color'] for s in spans}
        checker.check(colors == CODE_PALETTE, f'{name}：四种配色都应出现', sorted(f'{c:06X}' for c in colors))
        for token in ('vector', 'string', 'pair', 'return', '42', '3.14159'):
            checker.check(any(s['text'].strip() == token and s['color'] == CODE_KEYWORD for s in spans),
                          f'{name}：{token} 应为关键字色 {CODE_KEYWORD:06X}')
    return spans


def commit_subject(name):
    """扉页样张所用提交信息资源中的提交说明（第 3 行）。"""
    return (FIXTURES / name).read_text(encoding='utf-8').splitlines()[2]


def is_cjk(char):
    return 0x4E00 <= ord(char) <= 0x9FFF


def cjk_advances(page):
    """提交信息（小于 9 bp）中直接相邻的两个汉字之间的步进，返回 [(步进, 字号)]，单位 bp。"""
    result = []
    for block in page.get_text('rawdict')['blocks']:
        for line in block.get('lines', []):
            for span in line['spans']:
                if span['size'] >= 9:
                    continue
                chars = span['chars']
                result += [(b['origin'][0] - a['origin'][0], span['size'])
                           for a, b in zip(chars, chars[1:]) if is_cjk(a['c']) and is_cjk(b['c'])]
    return result


def hairline_frames(page):
    """0.4 pt、D1D1D6 描边的路径（未提交修改标签的圆角细框）。"""
    return [d['rect'] for d in page.get_drawings()
            if d.get('color') and all(abs(a - b / 255) < 0.005 for a, b in zip(d['color'], (209, 209, 214)))
            and abs(d.get('width', 0) - pt(0.4)) < 0.02]


# titlepage 样张的标题区：文字、苹方字重、字号（pt）、颜色，以及 \TitlePageSetup 中给出其基线位置的键。
TITLEPAGE_ROWS = [('算法竞赛小记', 'Semibold', 44, 0x1D1D1F, 'title'),
                  ('Competitive Programming Library', 'Regular', 15, 0x6E6E73, 'english'),
                  ('Calculatelove', 'Medium', 12, 0x1D1D1F, 'author')]


def check_titlepage(checker, path, hint, setup, *, landscape, side, bottom, header_bottom,
                    marker='', body_header=None):
    """检查 titlepage 样张（4 页），分小节记录，小节名以“titlepage：”开头。

    setup 为该版 \\TitlePageSetup 的取值，单位 mm，以纸张中心为原点、向上为正：title、english、author、
    image、stamp 与 image_width、image_height。landscape 表示 A4 横向；side、bottom 为左右与下边距（mm）；
    header_bottom 为页眉文字区的下缘（bp）。marker 为第 1、2 页书名后悬挂的版本标记；body_header 为
    第 4 页页眉应含的文字，为 None 时不查第 4 页的页眉。
    """
    title, author = TITLEPAGE_ROWS[0][0], TITLEPAGE_ROWS[2][0]
    pages = []
    with checker.section('titlepage：读取样张'):
        with checker.open(path, hint) as doc:
            checker.check(doc.metadata['title'] == title + marker, 'PDF 文档属性中的标题', doc.metadata['title'])
            checker.check(doc.metadata['author'] == author, 'PDF 文档属性中的作者', doc.metadata['author'])
            checker.require(len(doc) == 4, '样张应为 4 页', len(doc))
            pages = [text_rows(page) for page in doc]
            images = [[info['bbox'] for info in page.get_image_info()] for page in doc]
            advances = [cjk_advances(doc[i]) for i in range(2)]
            frames = [hairline_frames(page) for page in doc]
            headers = [page.get_text(clip=fitz.Rect(0, 0, page.rect.width, header_bottom)).strip()
                       for page in doc]
            width, height = doc[0].rect.width, doc[0].rect.height
    if not pages:
        return

    cx, cy = width / 2, height / 2
    stamp_south = cy - mm(setup['stamp'])

    with checker.section('titlepage：纸张与标题区'):
        paper = (A4_LONG, A4_SHORT) if landscape else (A4_SHORT, A4_LONG)
        checker.check(abs(width - paper[0]) < 0.1 and abs(height - paper[1]) < 0.1,
                      f'纸张应为 A4 {"横" if landscape else "纵"}向', (width, height))
        # 三页位置一致，不随配图、提交信息或版本标记变化；三行均以页面中轴居中。
        for number in range(3):
            head = pages[number][:3]
            checker.require(len(head) == 3, f'第 {number + 1} 页应有三行标题区', [r['text'] for r in head])
            for row, (text, weight, size, color, key) in zip(head, TITLEPAGE_ROWS):
                span = row['spans'][0]
                checker.check(span['text'] == text, f'第 {number + 1} 页标题区文字应为“{text}”', span['text'])
                checker.check('PingFang' in span['font'] and weight in span['font'], f'“{text}”应为苹方 {weight}',
                              span['font'])
                checker.check(abs(span['size'] - pt(size)) < 0.05 and span['color'] == color, f'“{text}”的字号与颜色',
                              round(span['size'], 2), f"{span['color']:06X}")
                checker.check(abs(row['y'] - (cy - mm(setup[key]))) < 0.3, f'“{text}”的基线位置', row['y'])
                checker.check(abs((span['bbox'][0] + span['bbox'][2]) / 2 - cx) < 0.5, f'“{text}”应以页面中轴居中',
                              span['bbox'])
            # 版本标记：苹方常规体 22 pt、次要灰，与书名同基线，紧接书名右侧，不参与居中；第 3 页不设版本标记。
            tag_text = marker if number < 2 else ''
            title_row = head[0]
            checker.check(title_row['text'] == title + tag_text, f'第 {number + 1} 页书名行', title_row['text'])
            if tag_text:
                if checker.check(len(title_row['spans']) == 2, '书名行应由书名与版本标记两段组成',
                                 [s['text'] for s in title_row['spans']]):
                    name, tag = title_row['spans']
                    checker.check(tag['text'] == tag_text, '版本标记文字', tag['text'])
                    checker.check('PingFang' in tag['font'] and 'Regular' in tag['font'], '版本标记应为苹方 Regular',
                                  tag['font'])
                    checker.check(abs(tag['size'] - pt(22)) < 0.05 and tag['color'] == 0x6E6E73, '版本标记的字号与颜色',
                                  round(tag['size'], 2), f"{tag['color']:06X}")
                    checker.check(abs(tag['origin'][1] - name['origin'][1]) < 0.1, '版本标记应与书名同基线',
                                  tag['origin'], name['origin'])
                    checker.check(abs(tag['bbox'][0] - name['bbox'][2]) < 0.5, '版本标记应紧接书名右侧',
                                  tag['bbox'], name['bbox'])
                    checker.check(tag['bbox'][2] < width - mm(side), '版本标记不应进入右边距', tag['bbox'])
            else:
                checker.check(len(title_row['spans']) == 1, f'第 {number + 1} 页书名行不应有版本标记',
                              [s['text'] for s in title_row['spans']])
            # 扉页不显示页眉页码。
            checker.check(not headers[number], f'第 {number + 1} 页不应有页眉', headers[number])
            checker.check(not any(r['text'].strip().isdigit() for r in pages[number]), f'第 {number + 1} 页不应显示页码')

    with checker.section('titlepage：配图区域'):
        # 在 image_width × image_height 区域内等比缩放：横向配图（800 × 300 像素）占满区域宽度，
        # 纵向配图（300 × 800 像素）占满区域高度；中心按 \TitlePageSetup 的 image 定位。
        w, h = setup['image_width'], setup['image_height']
        center = cy - mm(setup['image'])
        for number, (iw, ih) in ((0, (w, w * 300 / 800)), (1, (h * 300 / 800, h))):
            if not checker.check(len(images[number]) == 1, f'第 {number + 1} 页应有一张配图', images[number]):
                continue
            x0, y0, x1, y1 = images[number][0]
            checker.check(abs((x1 - x0) - mm(iw)) < 0.5 and abs((y1 - y0) - mm(ih)) < 0.5,
                          f'第 {number + 1} 页配图尺寸', (x1 - x0, y1 - y0))
            checker.check(abs((x0 + x1) / 2 - cx) < 0.5 and abs((y0 + y1) / 2 - center) < 0.5,
                          f'第 {number + 1} 页配图中心', ((x0 + x1) / 2, (y0 + y1) / 2))
            stamp_top = pages[number][3]['y'] - pt(6.5)
            checker.check(pages[number][2]['y'] < y0 and y1 < stamp_top,
                          f'第 {number + 1} 页配图不应与标题区、提交信息重叠', (y0, y1, stamp_top))
        checker.check(images[2] == [], '第 3 页不应有配图', images[2])
        # 配图区域本身也不与标题区、提交信息相交（区域上缘在作者基线之下，下缘在眉题之上）。
        area_top, area_bottom = center - mm(h / 2), center + mm(h / 2)
        checker.check(pages[0][2]['y'] < area_top and area_bottom < pages[0][3]['y'] - pt(6.5),
                      '配图区域不应与标题区、提交信息相交', (area_top, area_bottom))

    with checker.section('titlepage：眉题式提交信息'):
        # 眉题、日期与哈希、提交说明各占一行，不使用“·”等分隔符。
        for number, (date, digest, dirty) in enumerate((('2026-10-15', '0123abc', False),
                                                       ('2026-10-15', 'abcdef0', True))):
            eyebrow, ident = pages[number][3], pages[number][4]
            span = eyebrow['spans'][0]
            checker.check(compact(eyebrow['text']) == 'LASTCOMMIT', f'第 {number + 1} 页眉题文字', eyebrow['text'])
            checker.check('PingFang' in span['font'] and 'Medium' in span['font'], '眉题应为苹方 Medium', span['font'])
            checker.check(abs(span['size'] - pt(6.5)) < 0.05 and span['color'] == 0x6E6E73, '眉题的字号与颜色',
                          round(span['size'], 2), f"{span['color']:06X}")
            checker.check(abs((eyebrow['x0'] + eyebrow['x1']) / 2 - cx) < 0.5, '眉题应水平居中',
                          eyebrow['x0'], eyebrow['x1'])
            checker.check(compact(ident['text']) == date + digest + ('含未提交修改' if dirty else ''),
                          f'第 {number + 1} 页日期与哈希行', ident['text'])
            code = [s for s in ident['spans'] if s['text'].strip() in (date, digest)]
            checker.check(len(code) == 2 and all('MapleMono' in s['font'] for s in code), '日期与哈希应为 Maple Mono',
                          [(s['text'], s['font']) for s in code])
            checker.check(all(abs(s['size'] - pt(8)) < 0.05 for s in code), '日期与哈希应为 8 pt',
                          [round(s['size'], 2) for s in code])
            checker.check(len(code) == 2 and code[0]['color'] == 0x6E6E73 and code[1]['color'] == 0x506B82,
                          '日期应为次要灰、哈希应为灰蓝色', [f"{s['color']:06X}" for s in code])
            checker.check(not any('·' in r['text'] for r in pages[number][3:]), '提交信息不应使用“·”分隔',
                          [r['text'] for r in pages[number]])
            if dirty:
                # 未提交修改：深色 6.5 pt 文字，外有一个 0.4 pt 浅灰细框；连同细框整行居中。
                tag = next((s for s in ident['spans'] if '含未提交修改' in s['text']), None)
                checker.require(tag is not None, f'第 {number + 1} 页应有“含未提交修改”标签')
                checker.check(tag['color'] == 0x1D1D1F and abs(tag['size'] - pt(6.5)) < 0.05, '标签文字的颜色与字号',
                              f"{tag['color']:06X}", round(tag['size'], 2))
                checker.require(len(frames[number]) == 1, '标签外应有一个细框', frames[number])
                frame = frames[number][0]
                checker.check(frame.x0 < tag['bbox'][0] and tag['bbox'][2] < frame.x1, '细框应在水平方向包住标签文字',
                              frame, tag['bbox'])
                checker.check(frame.y0 < tag['origin'][1] < frame.y1, '细框应在竖直方向包住标签基线',
                              frame, tag['origin'])
                checker.check(len(code) == 2 and abs((code[0]['bbox'][0] + frame.x1) / 2 - cx) < 0.5,
                              '连同细框整行应居中', frame)
            else:
                checker.check(frames[number] == [], '干净状态不应有细框', frames[number])
                checker.check(abs((ident['x0'] + ident['x1']) / 2 - cx) < 0.5, '日期与哈希行应水平居中',
                              ident['x0'], ident['x1'])

    with checker.section('titlepage：提交说明原样输出与换行'):
        # 第 1 页：特殊字符原样输出（`--` 不被替换为连接号），提交说明为苹方。
        second = pages[0][5]
        checker.check(compact(second['text']) == compact(commit_subject('titlepage-special.commit')),
                      '第 1 页提交说明应原样输出', second['text'])
        checker.check('--' in second['text'] and '–' not in second['text'], '`--` 不应被替换为连接号', second['text'])
        checker.check(all('PingFang' in s['font'] for s in second['spans']), '提交说明应为苹方',
                      [s['font'] for s in second['spans']])
        checker.check(len(pages[0]) == 6, '第 1 页应共 6 行', [r['text'] for r in pages[0]])
        # 第 2 页：超长说明居中换行，整体向上增长、底边不变。
        rest = pages[1][5:]
        checker.check(len(rest) >= 2, '第 2 页超长说明应换行', [r['text'] for r in rest])
        long_subject = commit_subject('titlepage-long-dirty.commit')
        checker.check(compact(''.join(r['text'] for r in rest)) == compact(long_subject), '第 2 页提交说明应完整')
        checker.check(all(abs((r['x0'] + r['x1']) / 2 - cx) < 1 for r in rest), '换行后每行都应居中',
                      [(r['x0'], r['x1']) for r in rest])
        checker.check(pages[1][3]['y'] < pages[0][3]['y'], '超长说明应使提交信息整体向上增长',
                      pages[1][3]['y'], pages[0][3]['y'])

    with checker.section('titlepage：字距与底边'):
        # 居中不拉开字距：汉字步进等于字号（短行也不把 xeCJK 字间胶撑开）。
        for number in range(2):
            checker.check(advances[number], f'第 {number + 1} 页应找到相邻汉字')
            checker.check(all(abs(step - size) < 0.1 for step, size in advances[number]),
                          f'第 {number + 1} 页居中不应拉开字距', advances[number][:5])
        # 提交信息贴近底边：末行基线位于底边以上 3 bp 内，且不进入下边距。
        for number in range(2):
            last = pages[number][-1]
            checker.check(stamp_south - 3 < last['y'] <= stamp_south, f'第 {number + 1} 页提交信息末行应贴近底边',
                          last['y'], stamp_south)
            checker.check(last['bottom'] <= height - mm(bottom),
                          f'第 {number + 1} 页提交信息不应进入 {bottom} mm 下边距', last['bottom'])

    with checker.section('titlepage：无提交信息与正文页'):
        # 第 3 页：提交信息文件不存在、未设版本标记时只显示标题区。
        checker.check([r['text'] for r in pages[2]] == [row[0] for row in TITLEPAGE_ROWS], '第 3 页只应显示标题区',
                      [r['text'] for r in pages[2]])
        # 第 4 页：扉页之后照常显示页码；给出 body_header 时，页眉也应恢复。
        if body_header is not None:
            checker.check(body_header in headers[3], '第 4 页页眉应恢复', headers[3])
        checker.check(any(r['text'] == '4' and r['y'] > height - mm(20) for r in pages[3]), '第 4 页应显示页码 4',
                      [r['text'] for r in pages[3]])


def _fill_is(drawing, rgb):
    return drawing.get('fill') and all(abs(a - b / 255) < 0.005 for a, b in zip(drawing['fill'], rgb))


def check_block_spacing(checker, doc, baselineskip, parskip, box_before, box_after, itemsep=1, parsep=1):
    """检查 fixtures/block-spacing-body.tex 的竖向间距；长度参数为 TeX pt，取值与该版布局一致。

    标记行（LINE-、HEAD-、ITEM- 加组号）取基线；代码卡片取 D1D1D6 外框，引用块取 F7F7F7 背景，
    分隔线取 A0A0A0 描边的中线（线宽 0.4 pt）。盒前的标记行没有下伸笔画，盒顶到其基线即为前距。
    """
    tolerance = pt(0.05)
    marks, boxes, rules = {}, [], []
    for page in doc:
        half = page.rect.width / 2
        for row in text_rows(page, min_size=9):
            found = re.search(r'(LINE|HEAD|ITEM)-[A-D]\d', compact(row['text']))
            if found:
                checker.check(found[0] not in marks, f'标记“{found[0]}”只应出现一次')
                marks[found[0]] = (page.number, int(row['x0'] > half), row['y'])
        for d in page.get_drawings():
            r = d['rect']
            where = (page.number, int(r.x0 > half))
            if _fill_is(d, (209, 209, 214)):
                boxes.append((*where, r.y0, r.y1, '卡片'))
            elif _fill_is(d, (247, 247, 247)):
                boxes.append((*where, r.y0, r.y1, '引用块'))
            elif d.get('color') and all(abs(a - b / 255) < .005 for a, b in zip(d['color'], (160, 160, 160))):
                rules.append((*where, r.y0))
    missing = [m for m in ('LINE-A1', 'LINE-A2', 'LINE-A4', 'LINE-A5', 'HEAD-B1', 'HEAD-B2', 'LINE-B2',
                           'HEAD-B3', 'ITEM-C1', 'ITEM-C2', 'ITEM-C3', 'ITEM-C4', 'LINE-D1', 'LINE-D2')
               if m not in marks]
    checker.require(not missing, '应找到全部标记行', missing)

    def after(where, y):
        """同页同栏中，顶边在 y 以下的第一个盒。"""
        found = sorted((b for b in boxes if b[:2] == where[:2] and b[2] >= y - tolerance), key=lambda b: b[2])
        checker.require(found, '标记之后应有盒', where, y)
        return found[0]

    def before(where, y):
        """同页同栏中，底边在 y 以上的最后一个盒。"""
        found = sorted((b for b in boxes if b[:2] == where[:2] and b[3] <= y + tolerance), key=lambda b: b[3])
        checker.require(found, '标记之前应有盒', where, y)
        return found[-1]

    def close(actual, expected, message):
        checker.check(abs(actual - pt(expected)) < tolerance, message,
                      f'实测 {to_pt(actual):.3f} pt', f'应为 {expected:.3f} pt')

    next_line = box_after + parskip + baselineskip
    # A 组：正文 → 卡片 → 卡片 → 正文；正文 → 引用块 → 卡片 → 引用块 → 正文。
    a1, a4 = marks['LINE-A1'], marks['LINE-A4']
    card1 = after(a1, a1[2])
    card2 = after(card1, card1[3])
    quote1 = after(a4, a4[2])
    card3 = after(quote1, quote1[3])
    quote2 = after(card3, card3[3])
    checker.check([b[4] for b in (card1, card2, quote1, card3, quote2)] == ['卡片', '卡片', '引用块', '卡片', '引用块'],
                  '盒的顺序应与样张一致', [b[4] for b in (card1, card2, quote1, card3, quote2)])
    close(card1[2] - a1[2], box_before, '正文 → 卡片：盒顶距上一行的底应为盒前距')
    close(card2[2] - card1[3], box_before, '卡片 → 卡片：间距应为盒前距')
    close(marks['LINE-A2'][2] - before(marks['LINE-A2'], marks['LINE-A2'][2])[3], next_line,
          '卡片 → 正文：基线距盒底应为盒后距 + 段距 + 行距')
    close(quote1[2] - a4[2], box_before, '正文 → 引用块：盒顶距上一行的底应为盒前距')
    close(card3[2] - quote1[3], box_before, '引用块 → 卡片：间距应为盒前距')
    close(quote2[2] - card3[3], box_before, '卡片 → 引用块：间距应为盒前距')
    close(marks['LINE-A5'][2] - before(marks['LINE-A5'], marks['LINE-A5'][2])[3], next_line,
          '引用块 → 正文：基线距盒底应为盒后距 + 段距 + 行距')
    # B 组：盒后的标题以盒底为准，与正文后的标题以上一行基线为准相同。
    card4 = before(marks['HEAD-B2'], marks['HEAD-B2'][2])
    checker.check(card4 == after(marks['HEAD-B1'], marks['HEAD-B1'][2]), 'HEAD-B1 与 HEAD-B2 之间应恰有一张卡片')
    checker.check(abs((marks['HEAD-B2'][2] - card4[3]) - (marks['HEAD-B3'][2] - marks['LINE-B2'][2])) < tolerance,
                  '卡片 → 标题应与正文 → 标题的基线距相同',
                  f'{to_pt(marks["HEAD-B2"][2] - card4[3]):.3f} pt',
                  f'{to_pt(marks["HEAD-B3"][2] - marks["LINE-B2"][2]):.3f} pt')
    # C 组：二级列表不加上下间距，子项紧随父项；同级条目之间为条目间距 + 段间距。
    items = [marks[f'ITEM-C{i}'][2] for i in range(1, 5)]
    close(items[1] - items[0], baselineskip + parsep, '一级条目 → 首个二级条目：应为行距 + 段间距')
    close(items[2] - items[1], baselineskip + itemsep + parsep, '二级条目之间：应为行距 + 条目间距 + 段间距')
    close(items[3] - items[2], baselineskip + itemsep + parsep, '末个二级条目 → 下一个一级条目：应为行距 + 条目间距 + 段间距')
    # D 组：横线按正常行距排在上一行之后，下方另加 0.4 倍行距。
    d1, d2 = marks['LINE-D1'], marks['LINE-D2']
    found = [r for r in rules if r[:2] == d1[:2] and d1[2] < r[2] < d2[2]]
    checker.require(len(found) == 1, 'LINE-D1 与 LINE-D2 之间应恰有一条分隔线', found)
    middle = found[0][2]
    close(middle - pt(0.2) - d1[2], parskip + baselineskip - 0.4, '分隔线顶边距上一行基线应为段距 + 行距 − 线宽')
    close(d2[2] - (middle + pt(0.2)), 0.4 * baselineskip + parskip + baselineskip,
          '下一行基线距分隔线底边应为 0.4 倍行距 + 段距 + 行距')
