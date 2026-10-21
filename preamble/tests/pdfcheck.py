"""样张的功能检查：内容、导航与作用域；外观由样张目视验收。"""
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
sys.path.insert(0, str(ROOT / 'scripts'))
from pdf_geometry import read_geometry, is_titlepage, line_number_spans


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


def text_rows(page):
    """按基线归并文字，返回自上而下的行，不按字号筛选。"""
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
    for r in rows:
        r['spans'].sort(key=lambda s: s['origin'][0])
        r['text'] = ''.join(s['text'] for s in r['spans'])
        r['x0'] = min(s['bbox'][0] for s in r['spans'])
        r['x1'] = max(s['bbox'][2] for s in r['spans'])
        r['bottom'] = max(s['bbox'][3] for s in r['spans'])
    return sorted(rows, key=lambda r: r['y'])


def body_rect(page, column=None):
    g = read_geometry(page)
    left = g.left if column is None else g.starts[column]
    right = g.starts[-1] + g.column_width if column is None else left + g.column_width
    return fitz.Rect(left, g.top - 1, right, g.bottom + 3)


def column_texts(page):
    return [(col, page.get_text(clip=body_rect(page, col)))
            for col in range(read_geometry(page).columns)]


def locate(checker, doc, text):
    hits = [(p.number, r) for p in doc for r in p.search_for(text)
            if body_rect(p).contains((r.tl + r.br) / 2)]
    checker.require(len(hits) == 1, f'正文应恰好有一处“{text}”', hits)
    return hits[0]


def column(doc, position):
    page, rect = position
    return page, read_geometry(doc[page]).column(rect.x0)


def check_spanning(checker, segments, message):
    checker.check(len({p for p, _ in segments}) > 1, message + '应实际跨页', segments)
    checker.check({col for _, col in segments} == {0, 1}, message + '应实际跨栏', segments)


def check_code_line_numbers(checker, doc, twocolumn=False):
    """按源文件行对应，检查折行、空行、新卡片重置及跨栏连续编号。"""
    numbers, spans = [], []
    for page in doc:
        g = read_geometry(page)
        numbers += [(page.number, n) for n in line_number_spans(page, g)]
        spans += [(page.number, s) for b in page.get_text('dict')['blocks']
                  for line in b.get('lines', []) for s in line['spans']]
    checker.require(numbers, '代码卡片应有框外行号')
    for page, s in spans:
        match = re.search(r'landscape_value_(\d{3})', s['text'])
        if match:
            col = read_geometry(doc[page]).column(s['bbox'][0])
            found = [n for p, n in numbers if p == page
                     and abs(n['origin'][1] - s['origin'][1]) < .1
                     and read_geometry(doc[p]).column(n['bbox'][2] + n['size'] * 2) == col
                     and n['bbox'][2] < s['bbox'][0]]
            checker.check(len(found) == 1 and int(found[0]['text']) == int(match[1]) + 1,
                          '长代码行号应与源文件行一致', s['text'])

    def position(item):
        page, s = item
        # 行号在框外，以右侧的代码归栏；宽栏距也不依赖固定毫米数。
        g = read_geometry(doc[page])
        col = (min(range(g.columns), key=lambda i: abs(g.starts[i] - s['bbox'][0]))
               if s['text'].strip().isdigit() else g.column(s['bbox'][0]))
        return page, col, s['origin'][1]

    def token(text):
        found = [item for item in spans if text in item[1]['text']]
        checker.require(len(found) == 1, f'应找到唯一的 {text}')
        return position(found[0])

    start, wrap_end, end = token('Wrap-start:'), token('Wrap-end.'), token('final_line')
    selected = sorted((position(item), item[1]['text'].strip()) for item in numbers
                      if start <= position(item) <= end)
    checker.check([n for _, n in selected] == ['1', '2', '3', '4'],
                  '折行只标一次、空行计数、新卡片从 1 开始', selected)
    checker.check(wrap_end > start, '样张长行应实际折行')
    if twocolumn:
        checker.check(any(int(n['text']) >= 100 for _, n in numbers), '应覆盖三位行号')


def check_titlepage(checker, path, hint, marker=''):
    repository = 'https://example.com/~cl/cp_library%20v4'
    title, english, author = '算法竞赛小记', 'Competitive Programming Library', 'Calculatelove'
    with checker.section('titlepage：元信息、可选分支与链接'):
        with checker.open(path, hint) as doc:
            pages = [p for p in doc if is_titlepage(p)]
            checker.require(len(pages) == 3, '应有三种扉页分支')
            checker.check(doc.metadata['title'] == title + marker, 'PDF 标题元信息')
            checker.check(doc.metadata['author'] == author, 'PDF 作者元信息')
            for i, page in enumerate(pages):
                text = compact(page.get_text())
                for expected in (title, english, author):
                    checker.check(compact(expected) in text, '扉页文字应完整', expected)
                checker.check(('（代码版）' in text) == bool(marker and i < 2), '版本标记应按设置显示或省略')
                images = page.get_image_info()
                checker.check(len(images) == (1 if i < 2 else 0), '配图应按设置显示或省略')
                if images:
                    w, h = ((800, 300) if i == 0 else (300, 800))
                    box = fitz.Rect(images[0]['bbox'])
                    checker.check(abs(box.width / box.height - w / h) < .01, '配图应保持纵横比')
                uris = sorted(link.get('uri', '') for link in page.get_links())
                expected_links = ([repository, repository + '/commit/0123abc'] if i == 0
                                  else [] if i == 1 else [repository])
                checker.check(uris == sorted(expected_links), '仓库与提交链接应按设置生成', uris)
                if i < 2:
                    fixture = 'titlepage-special.commit' if i == 0 else 'titlepage-long-dirty.commit'
                    date, digest, subject, state = (FIXTURES / fixture).read_text().splitlines()
                    for value in (date, digest, subject):
                        checker.check(compact(value) in text, '提交信息及特殊字符应完整', value)
                    checker.check(('含未提交修改' in text) == (state == 'dirty'), 'dirty 标签应按状态显示')
                else:
                    checker.check('LASTCOMMIT' not in text and '0123abc' not in text,
                                  '缺少提交文件时应省略提交信息')
                g = read_geometry(page)
                checker.check(not page.get_text(clip=fitz.Rect(0, 0, g.width, g.top)).strip(), '扉页不显示页眉')
                checker.check(not any(r['text'].strip().isdigit() for r in text_rows(page) if r['y'] > g.bottom),
                              '扉页不显示页码')
            body = [p for p in doc if not is_titlepage(p)]
            checker.require(body, '扉页后应有正文')
            checker.check('扉页之后' in body[0].get_text(), '扉页后正文应保留')
            g = read_geometry(body[0])
            footer = body[0].get_text(clip=fitz.Rect(0, g.bottom, g.width, g.height))
            checker.check(str(body[0].number + 1) in footer, '正文页码应恢复')


def check_quotes(c, doc):
    """对照写法与局部作用域，不锁定具体字体名、字号或颜色。"""
    rows = []
    for page in doc:
        for block in page.get_text('rawdict')['blocks']:
            for line in block.get('lines', []):
                chars = [(ch['c'], s['font'], s['size'], ch['origin'], s['color'])
                         for s in line['spans'] for ch in s['chars'] if not ch['c'].isspace()]
                if chars:
                    rows.append((''.join(ch[0] for ch in chars), chars))

    def pair(word):
        phrase = f'“{word}”'
        found = [chars[text.index(phrase):text.index(phrase) + len(phrase)]
                 for text, chars in rows if phrase in text]
        c.require(len(found) == 1, f'应找到唯一的 {phrase}')
        return [(ch[1], ch[2], ch[4]) for ch in (found[0][0], found[0][-1])]

    for word in ('内层', '恢复', '码后', '项目', '强调', '段落', '块后', '换页'):
        c.check(pair(word) == pair('常规'), f'“{word}”应使用当前正文字体，局部切换不应泄漏')
    c.check(pair('外层') == pair('返回'), '嵌套结束应恢复外层字体')

    def signature(prefix):
        matches = [chars for text, chars in rows if text.startswith(prefix)]
        c.require(len(matches) == 1, f'应找到唯一的 {prefix} 对照行')
        chars = matches[0][len(prefix):]
        x0, y0 = chars[0][3]
        return [(ch, font, round(size, 3), color, round(pos[0] - x0, 2), round(pos[1] - y0, 2))
                for ch, font, size, pos, color in chars]

    for current, original in [('新版：', '参考：'), ('苹方现状：', '苹方对照：'), ('代码现状：', '代码对照：')]:
        c.check(signature(current) == signature(original), f'{current}应与对照写法等效')
    for text, _ in rows:
        c.check(not text.endswith('“') and not text.startswith('”'), '引号不能出现在错误的行首或行尾', text)
    c.check([entry[1] for entry in doc.get_toc()] == ['引号“一级”', '引号“二级”', '引号“三级”'],
            '书签应保留 Unicode 引号与标题文本')
