"""读取构建时嵌入 PDF 的实际版心（TeX pt 转 bp）；不维护设计参数副本。"""
from dataclasses import dataclass
import re


@dataclass(frozen=True)
class Geometry:
    width: float
    height: float
    left: float
    top: float
    column_width: float
    gap: float
    body_height: float
    columns: int

    @property
    def bottom(self):
        return self.top + self.body_height

    @property
    def starts(self):
        return [self.left + i * (self.column_width + self.gap) for i in range(self.columns)]

    def column(self, x):
        return int(self.columns == 2 and x >= self.starts[1] - 1)


def read_geometry(page):
    """缺少或损坏元数据时明确失败，不能退回猜测的布局。"""
    kind, raw = page.parent.xref_get_key(page.xref, 'BookGeometry')
    values = re.findall(r'-?\d+(?:\.\d+)?', raw)
    if kind != 'array' or len(values) != 8:
        raise ValueError('PDF 缺少版心记录，请用当前构建脚本重新编译')
    g = Geometry(*(float(v) * 72 / 72.27 for v in values[:7]), int(values[7]))
    if (g.columns not in (1, 2) or g.column_width <= 0 or g.body_height <= 0
            or g.gap < 0 or g.left < 0 or g.top < 0
            or g.starts[-1] + g.column_width > g.width + 1 or g.bottom > g.height + 1
            or abs(g.width - page.rect.width) > 1 or abs(g.height - page.rect.height) > 1):
        raise ValueError('PDF 版心记录与纸张不符')
    return g


def is_titlepage(page):
    return page.parent.xref_get_key(page.xref, 'BookTitlePage') == ('bool', 'true')


def line_number_spans(page, geometry):
    """用卡片外框与同行代码识别框外行号，不依赖行号的字体、颜色或字号。

    只认左缘与栏左缘对齐的卡片，且数字右侧须有同基线的框内文字；
    空行通过同一卡片其他已识别行号的右缘归属，避免把栏距中的任意数字忽略。
    """
    spans = [s for b in page.get_text('dict')['blocks'] for line in b.get('lines', []) for s in line['spans']]
    frames = {tuple(d['rect']) for d in page.get_drawings()
              if any(abs(d['rect'].x0 - x) < 1 for x in geometry.starts)
              and d['rect'].width > geometry.column_width / 2 and d['rect'].height > 1}
    found = {}
    for x0, y0, x1, y1 in frames:
        candidates = [s for s in spans if s['text'].strip().isascii() and s['text'].strip().isdigit()
                      and y0 <= s['origin'][1] <= y1
                      and x0 - max(geometry.gap, s['size'] * 4) <= s['bbox'][0]
                      and s['bbox'][2] < x0]
        aligned = [n['bbox'][2] for n in candidates if any(
            x0 <= s['bbox'][0] < x1 and abs(s['origin'][1] - n['origin'][1]) < .1
            and s['text'].strip() for s in spans)]
        for n in candidates:
            if any(abs(n['bbox'][2] - right) < .1 for right in aligned):
                found[(n['text'], tuple(n['bbox']))] = n
    return list(found.values())
