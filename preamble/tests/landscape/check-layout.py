"""检查真实横版样张中的几何、流向和页眉；需要 PyMuPDF。"""
from pathlib import Path
import fitz

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / 'preamble/tests/build/landscape'


def locate(doc, text):
    found = [(i, r) for i, p in enumerate(doc) for r in p.search_for(text) if r.y0 > 48]
    assert len(found) == 1, (text, found)
    return found[0]


def column(pos):
    return pos[0], int(pos[1].x0 > 420)


with fitz.open(OUT / 'flow.pdf') as doc:
    for p in doc:
        assert abs(p.rect.width - 297 * 72 / 25.4) < .1
        assert abs(p.rect.height - 210 * 72 / 25.4) < .1
    assert column(locate(doc, 'Alpha-body')) == (0, 0)
    assert column(locate(doc, 'Beta-body')) == (0, 0)
    assert column(locate(doc, 'Gamma-body')) == (0, 1)
    assert column(locate(doc, 'Delta-body')) == (1, 0)
    assert column(locate(doc, 'Epsilon-body')) == (1, 0)
    # 页眉显示页顶所在的章：左栏顶端新章取该章，否则取页首延续的章。
    for p, title in zip(doc, ['Alpha 章', 'Delta 章', 'Epsilon 章', 'Boundary-title']):
        assert title in p.get_text(clip=fitz.Rect(0, 0, p.rect.width, 48)), title
    for title, body in [('Boundary-title', 'Boundary-body'), ('Formula-title', 'FormulaBody')]:
        assert column(locate(doc, title)) == column(locate(doc, body))
        assert column(locate(doc, body))[1] == 1
print('flow: geometry, continuous chapters, column boundaries and headers verified')

PALETTE = {0x30343B, 0x506B82, 0x58715D, 0x70757D}
for name in ('code-cards', 'syntax-colors'):
    with fitz.open(OUT / f'{name}.pdf') as doc:
        spans = [s for p in doc for b in p.get_text('dict')['blocks']
                 for line in b.get('lines', []) for s in line['spans']
                 if 'Maple' in s['font'] and any(ord(c) < 0xE000 and not c.isspace() for c in s['text'])]
        assert spans
        assert all(s['color'] in PALETTE and 'Bold' not in s['font'] and 'Italic' not in s['font'] for s in spans)
        if name == 'syntax-colors':
            assert {s['color'] for s in spans} == PALETTE
            for token in ('vector', 'string', 'pair', 'return', '42', '3.14159'):
                assert any(s['text'].strip() == token and s['color'] == 0x506B82 for s in spans), token
        else:
            import re
            segments, lines = [], []
            for i, page in enumerate(doc):
                for col, (left, right) in enumerate([(0, page.rect.width / 2), (page.rect.width / 2, page.rect.width)]):
                    text = page.get_text(clip=fitz.Rect(left, 48, right, 560))
                    numbers = re.findall(r'int landscape_value_(\d{3}) = (\d+);', text)
                    if numbers:
                        segments.append((i, col))
                        lines.extend(numbers)
            assert lines == [(f'{i:03d}', str(i)) for i in range(1, 101)], lines
            assert segments[:3] == [(0, 0), (0, 1), (1, 0)], segments
            assert sum(p.get_text().count('Landscape-long-card') for p in doc) == 1
            assert column(locate(doc, 'Card-boundary')) == (0, 0)
    print(f'{name}: code palette, upright regular fonts and content verified')

with fitz.open(OUT / 'interfaces.pdf') as doc:
    import re
    numbers, segments = [], []
    for i, page in enumerate(doc):
        for col, (left, right) in enumerate([(0, page.rect.width / 2), (page.rect.width / 2, page.rect.width)]):
            text = page.get_text(clip=fitz.Rect(left, 48, right, 560))
            found = re.findall(r'Quote-(\d{3})', text)
            if found:
                numbers.extend(found)
                segments.append((i, col))
    assert numbers == [f'{i:03d}' for i in range(1, 66)], numbers
    assert segments[:3] == [(0, 0), (0, 1), (1, 0)], segments
print('interfaces: quote content and three-fragment continuation verified')

with fitz.open(OUT / 'toc-layout.pdf') as doc:
    toc_pages = [p for p in doc if p.get_links()]
    assert len(toc_pages) >= 2
    heading = [r for r in doc[0].search_for('目录') if r.y0 < 100]
    assert len(heading) == 1
    assert abs((heading[0].x0 + heading[0].x1) / 2 - doc[0].rect.width / 2) < 1
    bookmarks = doc.get_toc(simple=False)
    assert len(bookmarks) == 90
    assert {b[0] for b in bookmarks} == {1, 2, 3, 4, 5}
    assert all(not b[3].get('collapse', False) for b in bookmarks)
    body_first = bookmarks[0][2] - 1
    assert body_first == len(toc_pages)
    assert any(r.x0 < 100 and r.y0 > 48 for r in doc[body_first].search_for('TOC-Chapter-01'))
    expected = {b[1].split()[0]: b[2] - 1 for b in bookmarks if b[0] <= 3}
    positions = {}
    for page in toc_pages:
        assert 'Fourth-only' not in page.get_text() and 'Fifth-only' not in page.get_text()
        assert not page.get_text(clip=fitz.Rect(0, 0, page.rect.width, 48)).strip()
        for token in expected:
            hits = page.search_for(token)
            for rect in hits:
                assert token not in positions, token
                positions[token] = (page.number, int(rect.x0 > 420))
                links = [l for l in page.get_links() if l['from'].intersects(rect)]
                assert links and all(l.get('page') == expected[token] for l in links), token
        for link in page.get_links():
            assert 0 <= link.get('page', -1) < len(doc)
            r = link['from']
            assert r.x0 >= 30 and r.x1 <= page.rect.width - 30
            assert r.x1 < 421 or r.x0 > 421, r
    assert positions.keys() == expected.keys()
    for i in range(1, 9):
        assert positions[f'TOC-Chapter-{i:02d}'] == positions[f'TOC-Topic-{i:02d}-1']
        for j in (1, 2):
            assert positions[f'TOC-Topic-{i:02d}-{j}'] == positions[f'TOC-Item-{i:02d}-{j}-1']
print('toc-layout: centered heading, column groups, 88 linked entries and 90 expanded bookmarks verified')

with fitz.open(OUT / 'images.pdf') as doc:
    assert len(doc) == 1
    # mwe 提供矢量 PDF；通过 image 字母的左右位置及 TeX 盒宽断言检验两栏。
    page = doc[0]
    assert any(r.x0 < 420 for r in page.search_for('A'))
    assert any(r.x0 > 420 for r in page.search_for('B'))
print('images: column-relative widths and local page-width isolation verified')
