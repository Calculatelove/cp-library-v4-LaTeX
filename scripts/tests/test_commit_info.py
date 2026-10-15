"""commit-info.sh 的 Git 状态边界；在临时仓库中运行，不读取本项目历史及用户 Git 配置。"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'commit-info.sh'
SUBJECT = r'fix: a_b & c% #1 $x^2$ {y} \LaTeX ~ ^^41 -- 中文“引号”——破折号'


class CommitInfoTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name) / 'project'
        (self.root / 'scripts').mkdir(parents=True)
        shutil.copy(SCRIPT, self.root / 'scripts/commit-info.sh')
        self.env = {k: v for k, v in os.environ.items() if not k.startswith('GIT_')}
        self.env.update(GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM='1',
                        GIT_CEILING_DIRECTORIES=self.tmp.name, TZ='UTC',
                        GIT_AUTHOR_NAME='t', GIT_AUTHOR_EMAIL='t@example.com',
                        GIT_COMMITTER_NAME='t', GIT_COMMITTER_EMAIL='t@example.com')

    def tearDown(self):
        self.tmp.cleanup()

    def git(self, *args, date=None):
        env = dict(self.env)
        if date:
            env['GIT_AUTHOR_DATE'] = env['GIT_COMMITTER_DATE'] = date
        return subprocess.run(['git', '-C', str(self.root), *args], env=env, check=True,
                              capture_output=True, text=True).stdout.strip()

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def commit(self, path, text, message, date='2026-10-15T01:00:00+08:00'):
        self.write(path, text)
        self.git('add', '-A')
        self.git('commit', '-q', '-m', message, date=date)
        return self.git('rev-parse', '--short', 'HEAD')

    def info(self):
        result = subprocess.run(['bash', str(self.root / 'scripts/commit-info.sh')], env=self.env,
                                capture_output=True, text=True, check=True)
        return result.stdout.splitlines(), result.stderr

    def test_outside_repository_prints_nothing(self):
        lines, err = self.info()
        self.assertEqual(lines, [])
        self.assertIn('未找到 Git 仓库', err)

    def test_repository_without_commits_prints_nothing(self):
        self.git('init', '-q')
        lines, err = self.info()
        self.assertEqual(lines, [])
        self.assertIn('尚无提交', err)

    def test_commit_timezone_and_raw_subject(self):
        self.git('init', '-q')
        # UTC 为 2026-10-14 17:00，日期应按提交自身的 +08:00 时区取 2026-10-15。
        short = self.commit('a.tex', 'a', SUBJECT)
        self.assertEqual(self.info()[0], ['2026-10-15', short, SUBJECT, 'clean'])

    def test_build_only_commit_is_head(self):
        # 对应取消跟踪 PDF 的提交：只改 build/，扉页仍应显示这次最新提交。
        self.git('init', '-q')
        self.write('a.tex', 'a')
        self.commit('build/portrait/main-portrait.pdf', 'pdf', 'feat: 内容')
        self.commit('.gitignore', '/build/\n', 'chore: 忽略 build/')
        self.git('rm', '-q', '-r', '--cached', 'build')
        self.git('commit', '-q', '-m', 'refactor: 取消 PDF 跟踪', date='2026-10-15T01:00:00+08:00')
        short = self.git('rev-parse', '--short', 'HEAD')
        self.assertEqual(self.info()[0], ['2026-10-15', short, 'refactor: 取消 PDF 跟踪', 'clean'])

    def test_dirty_ignores_build_changes_only(self):
        self.git('init', '-q')
        self.commit('a.tex', 'a', 'feat: 内容')
        self.commit('build/portrait/main-portrait.pdf', 'pdf', 'build: 更新 PDF')
        self.write('build/portrait/main-portrait.pdf', 'rebuilt')
        self.write('build/portrait/main-portrait.commit', 'untracked')
        self.assertEqual(self.info()[0][-1], 'clean')
        self.write('contents/new.tex', 'untracked')
        self.assertEqual(self.info()[0][-1], 'dirty')
        (self.root / 'contents/new.tex').unlink()
        self.write('a.tex', 'changed')
        self.assertEqual(self.info()[0][-1], 'dirty')


if __name__ == '__main__':
    unittest.main()
