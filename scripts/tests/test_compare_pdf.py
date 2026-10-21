"""逐页比较的差异判定与基线清单；用构造的数据测试，不依赖 build/ 中的 PDF。"""
import importlib.util
from pathlib import Path
import unittest

HAS_PYMUPDF = importlib.util.find_spec('fitz') is not None
if HAS_PYMUPDF:
    spec = importlib.util.spec_from_file_location(
        'compare_pdf', Path(__file__).resolve().parents[1] / 'compare-pdf.py')
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)


def page(text, font='F', color=0, x0=0, links=()):
    """一页横排文字，每字宽 10 bp；逐字为 (字符, 字体, 字号, 颜色, x, y)。"""
    return {'size': (0, 0, 595.28, 841.89), 'drawings': [], 'images': [], 'links': list(links),
            'chars': [(ch, font, 10.0, color, x0 + 10 * i, 100) for i, ch in enumerate(text)]}


@unittest.skipUnless(HAS_PYMUPDF, '需要 PyMuPDF')
class ComparePdfTests(unittest.TestCase):
    def test_identical(self):
        doc = ([page('甲乙'), page('丙')], [[1, '甲', 1]])
        self.assertEqual(c.differences(doc, doc), [])

    def test_attribute_changes(self):
        """文字相同时逐字比较：字体、颜色按“旧 → 新”汇总次数与涉及的字符，位置给出移动的字数与最大位移。"""
        old = ([page('“甲”乙'), page('丙')], [])
        new = ([page('“甲”乙', font='G'), page('丙', color=0x506B82, x0=1.5)], [])
        self.assertEqual(c.differences(old, new), [
            '字体：F → G 4 处，涉及 “、甲、”、乙（第 1 页）',
            '颜色：000000 → 506B82 1 处，涉及 丙（第 2 页）',
            '位置：1 字移动，最大 1.50 bp（第 2 页）',
        ])

    def test_text_pages_links_and_bookmarks(self):
        """文字不同时按字符对齐，只比较对上的字；页数、链接与书签的差异另行报出。"""
        old = ([page('甲乙丙'), page('丁')], [[1, '甲', 1], [2, '乙', 1]])
        new = ([page('甲乙戊', font='G', links=[('https://example.com', None, None, (0, 0, 1, 1))])],
               [[1, '甲', 1], [2, '乙', 2]])
        self.assertEqual(c.differences(old, new), [
            '页数 2 → 1',
            '文字：第 1 页；第 1 页首处 甲乙丙 → 甲乙戊',
            '字体：F → G 2 处，涉及 甲、乙（第 1 页）',
            '链接：第 1 页',
            '书签：1 项不同',
        ])

    def test_baseline_lists_books_and_samples(self):
        """基线包含三版整书，以及各组 run.sh 列出、确有源码的样张。"""
        paths = c.current_pdfs()
        self.assertEqual(paths[:3], [f'build/{e}/main-{e}.pdf' for e in ('portrait', 'landscape', 'code')])
        self.assertGreater(len(paths), 3)
        for path in paths[3:]:
            group, name = Path(path).parent.name, Path(path).stem
            self.assertTrue((c.ROOT / f'preamble/tests/{group}/{name}.tex').is_file(), path)


if __name__ == '__main__':
    unittest.main()
