"""竖版、横版两个手写入口除布局一行外逐行相同；代码版入口由生成器以横版入口为模板生成，另有测试。"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
LAYOUT = r'\input{preamble/layout-%s.tex}'


class EntryTests(unittest.TestCase):
    def test_portrait_differs_only_in_layout_line(self):
        """章节清单、元信息、扉页与目录等全部一致；需要差异时应放进各版布局，而不是写在入口。"""
        portrait = (ROOT / 'main-portrait.tex').read_text(encoding='utf-8').splitlines()
        landscape = (ROOT / 'main-landscape.tex').read_text(encoding='utf-8').splitlines()
        self.assertEqual(portrait.count(LAYOUT % 'portrait'), 1)
        self.assertEqual(landscape.count(LAYOUT % 'landscape'), 1)
        self.assertEqual([LAYOUT % 'landscape' if line == LAYOUT % 'portrait' else line for line in portrait],
                         landscape)


if __name__ == '__main__':
    unittest.main()
