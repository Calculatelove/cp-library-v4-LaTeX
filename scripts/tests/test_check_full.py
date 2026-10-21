"""检查 PDF 自带版心、越界判定与行号识别，不依赖当前设计参数或 build/。"""
from contextlib import redirect_stderr, redirect_stdout
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest

HAS_PYMUPDF = importlib.util.find_spec('fitz') is not None
if HAS_PYMUPDF:
    spec = importlib.util.spec_from_file_location('check_full', Path(__file__).resolve().parents[1] / 'check-full.py')
    c = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(c)
    from pdf_geometry import Geometry, read_geometry, is_titlepage, line_number_spans


@unittest.skipUnless(HAS_PYMUPDF, '需要 PyMuPDF')
class CheckFullTests(unittest.TestCase):
    def test_overflow_columns(self):
        """不同边距与栏距下，栏距文字、右侧越纸边、标点与页眉保持相同判定。"""
        for left, width, gap in [(25, 230, 30), (40, 200, 60)]:
            g = Geometry(600, 400, left, 40, width, gap, 300, 2)
            end, right = left + width, g.starts[1]
            def char(x0, x1, text='字', page=2, top=100):
                return page, 600, text, x0, x1, top, 10
            chars = [char(end - 20, end + 5), char(end + 2, end + 9, page=3),
                     char(right + width - 5, 603, page=4), char(end - 10, end + .4, page=5),
                     char(end - 3, end + 7, '，', page=5), char(end - 3, end + 7, page=5, top=20),
                     char(right - .5, right + width - 1, page=5), char(end, end + 9, page=1)]
            worst = c.overflows(chars, {1}, {i: g for i in range(1, 6)})
            self.assertEqual(sorted(worst), [(2, '左'), (3, '左'), (4, '右')])
            self.assertEqual(worst[(2, '左')][0], 5)
            self.assertTrue(worst[(4, '右')][2])

    def test_geometry_and_title_marker(self):
        """版心来自被检查的 PDF；缺失、损坏或与纸张不符时拒绝，扉页不靠字号识别。"""
        with c.fitz.open() as doc:
            page = doc.new_page(width=600, height=400)
            with self.assertRaises(ValueError):
                read_geometry(page)
            values = [600, 400, 25, 40, 230, 30, 300]
            doc.xref_set_key(page.xref, 'BookGeometry', '[' + ' '.join(str(v * 72.27 / 72) for v in values) + ' 2]')
            self.assertAlmostEqual(read_geometry(page).starts[1], 285)
            self.assertFalse(is_titlepage(page))
            doc.xref_set_key(page.xref, 'BookTitlePage', 'true')
            self.assertTrue(is_titlepage(page))
            doc.xref_set_key(page.xref, 'BookGeometry', '[1 2 3]')
            with self.assertRaises(ValueError):
                read_geometry(page)
            doc.xref_set_key(page.xref, 'BookGeometry', '[1 2 3 4 5 6 7 2]')
            with self.assertRaises(ValueError):
                read_geometry(page)

    def test_line_numbers_need_frame_and_code(self):
        """颜色、字体、字号可变；栏距里的孤立数字不能被当作行号忽略。"""
        g = Geometry(600, 400, 25, 40, 230, 30, 300, 2)
        for font, size, color in [('helv', 6, (1, 0, 0)), ('cour', 8, (0, 0, 1))]:
            with c.fitz.open() as doc:
                page = doc.new_page(width=600, height=400)
                page.draw_rect(c.fitz.Rect(285, 80, 515, 180), color=(.3, .2, .1))
                page.insert_text((270, 100), '1', fontname=font, fontsize=size, color=color)
                page.insert_text((300, 100), 'int x;', fontsize=10)
                page.insert_text((270, 120), '2', fontname=font, fontsize=size, color=color)
                page.insert_text((270, 220), '9', fontname=font, fontsize=size, color=color)
                page = doc.reload_page(page)
                self.assertEqual(sorted(s['text'] for s in line_number_spans(page, g)), ['1', '2'])

    def test_commit_stamp(self):
        self.assertEqual(c.commit_stamp(['LAST COMMIT', '2026-10-17', '1422e16', '含未提交修改', 'fix abcdef1']),
                         ('2026-10-17', '1422e16', True))
        self.assertIsNone(c.commit_stamp(['fix abcdef1']))

    def test_missing_pdf_and_old_pdf(self):
        with redirect_stdout(io.StringIO()), redirect_stderr(io.StringIO()):
            self.assertEqual(c.main(['不存在的文件.pdf']), 2)
            with tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / 'old.pdf'
                with c.fitz.open() as doc:
                    doc.new_page()
                    doc.save(path)
                self.assertEqual(c.main([str(path)]), 1)


if __name__ == '__main__':
    unittest.main()
