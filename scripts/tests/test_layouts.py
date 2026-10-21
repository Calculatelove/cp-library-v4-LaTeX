"""代码版、横版两份布局除注释外逐行相同；两版取值要分开时，先为代码版加回其余样张，再删去本文件。"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
# 第一个未转义的 %：紧挨在它前面的反斜杠为偶数个。
COMMENT = re.compile(r'(?<!\\)(?:\\\\)*%')


def without_comments(text):
    """去掉注释后的各行。整行注释删去；% 前有空白时与没有注释等价；
    紧贴内容的 % 会吃掉行尾空格，只保留 % 本身。"""
    lines = []
    for line in text.splitlines():
        found = COMMENT.search(line)
        if not found:
            lines.append(line.rstrip(' \t'))
            continue
        before = line[:found.end() - 1]
        if before.strip():
            lines.append(before.rstrip(' \t') if before[-1] in ' \t' else before + '%')
    return lines


class LayoutTests(unittest.TestCase):
    def test_comment_rules(self):
        """整行注释与空白后的行尾注释可以增删；紧贴内容的 % 仍要一致；\\% 不是注释。"""
        text = 'a\n% 说明\n  % 缩进的说明\nb % 说明\nc% 说明\nd%\n\\% 不是注释\nf\\\\% 注释\ne \n'
        self.assertEqual(without_comments(text), ['a', 'b', 'c%', 'd%', '\\% 不是注释', 'f\\\\%', 'e'])

    def test_code_layout_matches_landscape(self):
        """代码版只留扉页样张，其余版式由横版样张检验，所以两份布局的取值与做法须完全相同。"""
        landscape, code = (without_comments((ROOT / f'preamble/layout-{name}.tex').read_text(encoding='utf-8'))
                           for name in ('landscape', 'code'))
        self.assertEqual(code, landscape, '代码版布局与横版除注释外不一致，见 preamble/tests/code/README.md')


if __name__ == '__main__':
    unittest.main()
