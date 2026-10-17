"""完整 PDF 越栏检查的分栏、越界判定与几何自检；用构造的数据测试，不依赖 build/ 中的 PDF。"""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import unittest

HAS_PYMUPDF = importlib.util.find_spec('fitz') is not None
if HAS_PYMUPDF:
    spec = importlib.util.spec_from_file_location(
        'check_full', Path(__file__).resolve().parents[1] / 'check-full.py')
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)


@unittest.skipUnless(HAS_PYMUPDF, '需要 PyMuPDF')
class CheckFullTests(unittest.TestCase):
    def char(self, x0, x1, text='字', page=2, top=100, size=10):
        """逐字记录：(页码, 页宽, 字符, 左端, 右端, 顶边, 字号)。"""
        return (page, c.PAGE_WIDTH, text, x0, x1, top, size)

    def test_overflow_columns(self):
        """左栏越过栏边、整个落在栏距内、右栏越过纸边都要报出；容差内、标点、页眉与扉页不报。"""
        chars = [
            self.char(c.LEFT_END - 20, c.LEFT_END + 5),                       # 左栏越界 5 bp
            self.char(c.LEFT_END + 2, c.LEFT_END + 9, page=3),                # 整个落在栏距内，仍算左栏
            self.char(c.RIGHT_END - 5, c.PAGE_WIDTH + 3, page=4),              # 右栏越过纸边
            self.char(c.LEFT_END - 10, c.LEFT_END + 0.4, page=5),              # 容差内
            self.char(c.LEFT_END - 3, c.LEFT_END + 7, '，', page=5),           # 全角标点按前进宽度虚报，跳过
            self.char(c.LEFT_END - 3, c.LEFT_END + 7, page=5, top=20),         # 页眉区域
            self.char(c.RIGHT_START - 0.5, c.RIGHT_END - 1, page=5),           # 右栏行首标点略早于栏边
            self.char(c.LEFT_END - 3, c.LEFT_END + 9, page=1),                 # 扉页
        ]
        worst = c.overflows(chars, skipped={1})
        self.assertEqual(sorted(worst), [(2, '左'), (3, '左'), (4, '右')])
        self.assertAlmostEqual(worst[(2, '左')][0], 5)
        self.assertEqual(worst[(4, '右')][2], True)        # 越过纸边
        self.assertEqual(worst[(3, '左')][3], False)       # 未伸到右栏位置

    def test_title_pages(self):
        chars = [self.char(100, 140, page=1, size=c.TITLEPAGE_SIZE + 4), self.char(100, 110, page=2)]
        self.assertEqual(c.title_pages(chars), [1])

    def test_card_line_numbers_are_identified_narrowly(self):
        """框外行号可跳过；同位置的正文数字、错误字号或偏移的数字仍须检查。"""
        span = {'chars': [{'c': ch} for ch in '123'], 'font': 'MapleMono-NF-CN-Regular',
                'size': 4 * 72 / 72.27, 'color': 0x808080,
                'bbox': (c.RIGHT_START - 14, 100, c.RIGHT_START - c.MM, 108)}
        self.assertTrue(c.is_card_line_number(span))
        for changed in ({'color': 0x30343B}, {'size': 8}, {'font': 'LatinModernMath'},
                        {'chars': [{'c': 'x'}]},
                        {'bbox': (c.RIGHT_START - 14, 100, c.RIGHT_START - 2 * c.MM, 108)}):
            self.assertFalse(c.is_card_line_number(dict(span, **changed)))

    def test_geometry_matches(self):
        """四条栏边各有足够多的正文行对齐、纸张为 A4 横向时没有问题。"""
        lines = [(2, c.LEFT_START, c.LEFT_END, 100), (2, c.RIGHT_START, c.RIGHT_END, 100)] * c.EDGE_MIN_LINES
        sizes = [(2, c.PAGE_WIDTH, c.PAGE_HEIGHT)]
        self.assertEqual(c.geometry_problems(lines, sizes, skipped=set()), [])

    def test_geometry_mismatch(self):
        """边距改 2 mm、页面改竖向、对齐行数不足或只在扉页上对齐时，都报出问题。"""
        shift = 2 * c.MM
        moved = [(2, c.LEFT_START + shift, c.LEFT_END + shift, 100),
                 (2, c.RIGHT_START + shift, c.RIGHT_END + shift, 100)] * c.EDGE_MIN_LINES
        sizes = [(2, c.PAGE_WIDTH, c.PAGE_HEIGHT)]
        self.assertEqual(len(c.geometry_problems(moved, sizes, skipped=set())), 4)
        portrait = [(n, c.PAGE_HEIGHT, c.PAGE_WIDTH) for n in (2, 3)]
        lines = [(2, c.LEFT_START, c.LEFT_END, 100), (2, c.RIGHT_START, c.RIGHT_END, 100)] * c.EDGE_MIN_LINES
        problems = c.geometry_problems(lines, portrait, skipped=set())
        self.assertEqual(len(problems), 1)
        self.assertIn('2 页不是 A4 横向', problems[0])
        too_few = lines[:2 * (c.EDGE_MIN_LINES - 1)]
        self.assertEqual(len(c.geometry_problems(too_few, sizes, skipped=set())), 4)
        self.assertEqual(len(c.geometry_problems(lines, sizes, skipped={2})), 4)

    def test_missing_pdf(self):
        stderr = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(stderr):
            self.assertEqual(c.main(['不存在的文件.pdf']), 2)
        self.assertIn('找不到', stderr.getvalue())


if __name__ == '__main__':
    unittest.main()
