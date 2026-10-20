"""preamble/tests 各检查脚本共用的 PDF 检查工具；需要 PyMuPDF。

- Checker：显式检查。失败只记录、不中断，最后统一汇总并以非零状态退出；
  不使用 assert，`python3 -O` 下照常生效。
- 单位：PDF 坐标的单位是 bp（1/72 in）。mm()、pt() 把毫米、TeX pt 换算为 bp，
  to_pt() 把 bp 换算回 TeX pt。不再使用含义容易混淆的 PT 常量。
- 横版与代码版共用的几何常量，以及多个脚本共用的文字行、代码配色和扉页读取函数。
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
