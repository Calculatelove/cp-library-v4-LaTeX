"""生成器边界、以横版入口为模板的三处变换及真实内容回归；不编译算法片段。"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    'generator', Path(__file__).resolve().parents[1] / 'generate-code.py')
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)

# 与真实横版入口结构相同的最小模板，供临时目录中的测试使用。
SKELETON = r'''\documentclass{article}

\input{preamble/packages.tex}
\input{preamble/layout-landscape.tex}
\input{preamble/mystyle.tex}

\title{书名}
\date{}

\begin{document}

\maketitle

\tableofcontents

%s

\end{document}'''


class GeneratorTests(unittest.TestCase):
    def make_root(self, tmp, entry, chapters):
        """在临时目录写入横版入口与章节；chapters 为 {相对路径: 内容}。"""
        root = Path(tmp)
        (root / 'contents').mkdir()
        (root / 'main-landscape.tex').write_text(entry, encoding='utf-8')
        for path, text in chapters.items():
            (root / path).write_text(text, encoding='utf-8')
        return root

    def test_comments_nested_titles_and_literal_code(self):
        source = r'''% \InputCode{cpp}{missing}
\section{章 \textbf{嵌套}}
\subsection[短标题]{长标题}
\begin{minted}[linenos]{cpp}
// \section{这不是标题}
// 100% unchanged
\InputCode{cpp}{not-a-reference}
\end{minted}
'''
        events = list(g.scan(source, 'fixture'))
        self.assertEqual([e[0] for e in events], ['heading', 'heading', 'inline'])
        self.assertIn('// 100% unchanged', events[-1][2])
        self.assertEqual(events[0][2], r'\section{章 \textbf{嵌套}}')

    def test_pruning_order_and_missing_reference(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_root(tmp, SKELETON % r'\input{contents/0x11 test.tex}', {
                'contents/a b.cpp': 'int x;',
                'contents/0x11 test.tex': r'''\section{章}
\subsection{空分支}
\subsubsection{也为空}
\subsection{有效分支}
\InputCode[标题 {含括号}]{cpp}{contents/a b.cpp}
\subsection{末尾空分支}
'''})
            result, counts, _ = g.generate(root)
            self.assertNotIn('空分支', result)
            self.assertLess(result.index(r'\section{章}'), result.index(r'\subsection{有效分支}'))
            self.assertEqual(counts[0][1:], (1, 0))
            (root / 'contents/a b.cpp').unlink()
            with self.assertRaisesRegex(ValueError, '文件不存在'):
                g.generate(root)

    def test_malformed_and_unsupported(self):
        for source in [r'\section{unclosed', r'\begin{minted}{cpp}',
                       r'\inputminted{cpp}{x}', r'\section*{x}']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                list(g.scan(source, 'fixture'))

    def test_three_transformations(self):
        """只换布局一行、在导言区末尾加版本标记、把章节引用换成代码；其余内容原样沿用。"""
        entry = SKELETON % '\n\n'.join([r'\input{contents/0x11 a.tex}', r'% 横版入口中的注释',
                                        r'\input{contents/0x12 b.tex}'])
        with tempfile.TemporaryDirectory() as tmp:
            root = self.make_root(tmp, entry, {
                'contents/0x11 a.tex': '\\section{甲}\n正文不收录。\n\\begin{minted}{cpp}\nint a;\n\\end{minted}\n',
                'contents/0x12 b.tex': '\\section{乙}\n没有代码的章节整章省略。\n'})
            result, _, _ = g.generate(root)
        expected = '\n'.join([
            g.HEADER,
            r'\documentclass{article}', '',
            r'\input{preamble/packages.tex}', r'\input{preamble/layout-code.tex}', r'\input{preamble/mystyle.tex}', '',
            r'\title{书名}', r'\date{}', r'\EditionLabel{代码版}', '',
            r'\begin{document}', '', r'\maketitle', '', r'\tableofcontents', '',
            r'\section{甲}', '',
            '\\begin{minted}{cpp}\nint a;\n\\end{minted}', '',
            '% 横版入口中的注释', '',
            r'\end{document}', ''])
        self.assertEqual(result, expected)

    def test_prose_edits_keep_entry(self):
        """入口不含来源与行号：只增删正文或注释行时，代码版入口不变。"""
        chapter = '\\section{甲}\n正文。\n\\begin{minted}{cpp}\nint a;\n\\end{minted}\n'
        edited = chapter.replace('正文。\n', '正文。\n\n新增的一段正文。\n% 新增的注释\n')
        results = []
        for text in (chapter, edited):
            with tempfile.TemporaryDirectory() as tmp:
                root = self.make_root(tmp, SKELETON % r'\input{contents/0x11 a.tex}', {'contents/0x11 a.tex': text})
                results.append(g.generate(root)[0])
        self.assertEqual(results[0], results[1])

    def test_template_structure_errors(self):
        """布局行或 \\begin{document} 缺失、重复，或章节引用与其他内容同行时报错，不生成入口。"""
        chapter = {'contents/0x11 a.tex': '\\section{甲}\n\\begin{minted}{cpp}\nint a;\n\\end{minted}\n'}
        good = SKELETON % r'\input{contents/0x11 a.tex}'
        cases = {
            '缺少布局行': good.replace('\\input{preamble/layout-landscape.tex}\n', ''),
            '布局行重复': good.replace('\\input{preamble/mystyle.tex}', '\\input{preamble/layout-landscape.tex}'),
            '缺少 begin': good.replace('\\begin{document}', ''),
            '章节引用不单独成行': SKELETON % r'说明 \input{contents/0x11 a.tex}',
        }
        for name, entry in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                with self.assertRaises(ValueError):
                    g.generate(self.make_root(tmp, entry, chapter))

    def test_real_content_exact_order_and_bytes(self):
        chapters = [e[1] for e in g.scan((g.ROOT / 'main-landscape.tex').read_text(encoding='utf-8'), 'entry')
                    if e[0] == 'input' and e[1].startswith('contents/')]
        expected = [e[2] for p in chapters for e in g.scan((g.ROOT / p).read_text(encoding='utf-8'), p)
                    if e[0] in ('file', 'inline')]
        generated, _, _ = g.generate(g.ROOT)
        actual = [e[2] for e in g.scan(generated, 'generated') if e[0] in ('file', 'inline')]
        self.assertEqual(actual, expected)

    def test_real_entry_preamble(self):
        """真实入口：代码版导言区等于横版导言区换布局一行再加版本标记。"""
        landscape = (g.ROOT / 'main-landscape.tex').read_text(encoding='utf-8')
        generated, _, _ = g.generate(g.ROOT)
        before = landscape.split(g.BEGIN_LINE)[0].rstrip('\n').split('\n')
        expected = [g.HEADER] + [g.CODE_LAYOUT_LINE if line == g.LAYOUT_LINE else line for line in before]
        self.assertEqual(generated.split(g.BEGIN_LINE)[0].rstrip('\n').split('\n'),
                         expected + [g.EDITION_LABEL])


if __name__ == '__main__':
    unittest.main()
