"""生成器边界及真实内容回归；不编译算法片段。"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('generator', Path(__file__).with_name('generate-code.py'))
g = importlib.util.module_from_spec(spec)
spec.loader.exec_module(g)


class GeneratorTests(unittest.TestCase):
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
            root = Path(tmp)
            (root / 'contents').mkdir()
            (root / 'main-landscape.tex').write_text(r'\input{contents/0x11 test.tex}')
            chapter = root / 'contents/0x11 test.tex'
            (root / 'contents/a b.cpp').write_text('int x;')
            chapter.write_text(r'''\section{章}
\subsection{空分支}
\subsubsection{也为空}
\subsection{有效分支}
\InputCode[标题 {含括号}]{cpp}{contents/a b.cpp}
\subsection{末尾空分支}
''')
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

    def test_real_content_exact_order_and_bytes(self):
        chapters = [e[1] for e in g.scan((g.ROOT / 'main-landscape.tex').read_text(), 'entry')
                    if e[0] == 'input' and e[1].startswith('contents/')]
        expected = [e[2] for p in chapters for e in g.scan((g.ROOT / p).read_text(), p)
                    if e[0] in ('file', 'inline')]
        generated, _, _ = g.generate(g.ROOT)
        actual = [e[2] for e in g.scan(generated, 'generated') if e[0] in ('file', 'inline')]
        self.assertEqual(actual, expected)


if __name__ == '__main__':
    unittest.main()
