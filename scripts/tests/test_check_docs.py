"""文档与脚本静态检查的各项判定；在临时目录中构造文件，不依赖本仓库的现状。"""
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('check_docs', Path(__file__).resolve().parents[1] / 'check-docs.py')
c = importlib.util.module_from_spec(spec)
spec.loader.exec_module(c)


class CheckDocsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, name, text='', size=None):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('x' * size if size is not None else text, encoding='utf-8')

    def run_check(self, check):
        return check(self.root, c.project_files(self.root, use_git=False))[0]

    def test_doc_paths(self):
        """存在的、按文档目录或后缀解析的、生成的、有意不存在的路径都不报；改名或删除的路径报出行号。
        样张等 PDF 是构建产物，不检查；assets/ 下的 PDF 是素材，照常检查。"""
        for name in ('preamble/layout-portrait.tex', 'preamble/shared/fonts.tex', 'scripts/generate-code.py',
                     'contents/0x10 基础/code/a.cpp', 'preamble/tests/fixtures/body.tex', 'run.sh'):
            self.write(name)
        self.write('preamble/tests/portrait/README.md', '共用 `../fixtures/body.tex`；`../fixtures/gone.tex`\n')
        self.write('preamble/README.md', '\n'.join([
            '`layout-portrait.tex`、`shared/`、`scripts/generate-code.py`、`generate-code.py`、`./run.sh code`',
            '代码在 `code/`；产物 `build/portrait/main-portrait.pdf`、`tests/build/`、`titlepage.pdf`',
            '占位与通配：`layout-<版本>.tex`、`fixtures/*-body.tex`、`\\InputCode{cpp}{contents/0x10 基础/code/a.cpp}`',
            '不创建 `setup.tex`、`docs/`；旧文件 `contents/AGENTS.md`；不带 `./`、`../` 的写法',
            '```sh',
            'python3 scripts/generate-code.py build/code/main-code.pdf',
            'bash preamble/tests/old/run.sh',
            '```',
            '`titlepage-portrait.tex` 与 `tests/landscape/generate-code.py`',
            '素材 `assets/cover.pdf`',
        ]) + '\n')
        self.write('README.md', '`missing.tex`\n')    # 根目录 README 由用户维护，不检查
        self.assertEqual(self.run_check(c.doc_paths), [
            'preamble/README.md:7：`preamble/tests/old/run.sh` 不存在',
            'preamble/README.md:9：`titlepage-portrait.tex` 不存在',
            'preamble/README.md:9：`tests/landscape/generate-code.py` 不存在',
            'preamble/README.md:10：`assets/cover.pdf` 不存在',
            'preamble/tests/portrait/README.md:1：`../fixtures/gone.tex` 不存在',
        ])

    def test_readmes(self):
        """允许上级说明完整目录名；拒绝缺失说明与名称子串误匹配；contents/ 不要求。"""
        for name in ('preamble/README.md', 'preamble/a.tex', 'scripts/tests/test_a.py', 'scripts/README.md',
                     'contents/0x10 基础/code/a.cpp'):
            self.write(name)
        missing = ['scripts/tests/ 缺少 README.md，且直接上级 README.md 未说明该目录']
        self.assertEqual(self.run_check(c.readmes), missing)
        self.write('scripts/README.md', '说明 `contest-tests/`，不是目标目录。')
        self.assertEqual(self.run_check(c.readmes), missing)
        self.write('scripts/README.md', '`tests/` 存放工具测试。')
        self.assertEqual(self.run_check(c.readmes), [])
        self.write('scripts/tests/data/example.txt')
        self.assertEqual(self.run_check(c.readmes), [
            'scripts/tests/data/ 缺少 README.md，且直接上级 README.md 未说明该目录'])
        self.write('scripts/tests/README.md', '`data/` 存放测试资源。')
        self.assertEqual(self.run_check(c.readmes), [])

    def test_shell_variables(self):
        """$变量名 后紧跟中文标点时报出；写了花括号或后接 ASCII 字符时不报。"""
        self.write('scripts/a.sh', '\n'.join([
            'a="Overfull $overfull，"',
            'b="Overfull ${overfull}，"',
            'c="$job: $pass"',
            "printf '%s' \"${brief:+（末轮警告：$brief）}\"",
        ]) + '\n')
        self.assertEqual(self.run_check(c.shell_variables), [
            'scripts/a.sh:1：$overfull 后紧跟非 ASCII 字符，请写成 ${overfull}',
            'scripts/a.sh:4：$brief 后紧跟非 ASCII 字符，请写成 ${brief}',
        ])

    def test_agents_sizes(self):
        """根文件超过 8 KiB，或从根目录到某个子目录的 AGENTS.md 合计超过 32 KiB 时报出。"""
        self.write('AGENTS.md', size=6000)
        self.write('preamble/AGENTS.md', size=20000)
        self.write('scripts/AGENTS.md', size=20000)
        self.assertEqual(self.run_check(c.agents_sizes), [])     # 两个子目录各自与根文件合计
        self.write('preamble/tests/AGENTS.md', size=7000)          # 根 + preamble + preamble/tests
        problems = self.run_check(c.agents_sizes)
        self.assertEqual(len(problems), 1)
        self.assertIn('preamble/tests/AGENTS.md', problems[0])
        self.write('AGENTS.md', size=9000)
        self.assertEqual(len(self.run_check(c.agents_sizes)), 2)  # 根文件超标；preamble/tests 一路合计超标


if __name__ == '__main__':
    unittest.main()
