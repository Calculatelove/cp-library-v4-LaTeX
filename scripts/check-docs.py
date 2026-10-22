"""文档与脚本的静态检查，由 scripts/check.sh 在快速检查中调用；只需 Python 3 标准库与 git。

- AGENTS.md 体量：根文件不超过 8 KiB（项目自定的维护目标）；根文件加某个子目录 AGENTS.md
  路径上的全部 AGENTS.md 不超过 32 KiB（Codex 默认只自动载入合计前 32 KiB）。
- 文档中的项目路径：根目录与各子目录的 AGENTS.md、WRITING.md、各子目录的 README.md 中，
  行内代码与代码块里的文件路径，以及整段行内代码写成的目录路径，都须存在。先按文档所在目录、
  再按项目根目录解析；不带 ./ 或 ../ 时，项目中有以它结尾的路径也算存在（如 `code/`、`generate-code.py`）。
  根目录 README.md 由用户维护，不检查。含中文、空格或 <版本> 等占位符的写法跳过；PDF 都是构建产物，
  除 assets/、contents/ 下的素材外不检查。
- 目录说明：contents/ 及其子目录以外，目录有 README.md，或由直接上级 README.md 以名称加斜线说明。
- shell 变量展开：.sh 中 $变量名 后不得紧跟非 ASCII 字符。macOS 自带的 bash 3.2 在 UTF-8
  区域设置下会把多字节字符的前几个字节读进变量名，在 set -u 下报 unbound variable。

文件清单取自 git（已跟踪与未被忽略的文件）；不在 Git 仓库中时遍历目录，跳过 .git、build 与缓存。
用法（从任意目录）：python3 scripts/check-docs.py
返回值：0 全部通过；1 有问题。
"""
from pathlib import Path
import posixpath
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
ROOT_AGENTS_LIMIT = 8 * 1024
COMBINED_LIMIT = 32 * 1024
# 文档有意提到、但项目中没有的路径：规定不创建的文件，以及已删除、只留在 Git 历史中的文件。
ABSENT_ON_PURPOSE = {
    'setup.tex', 'layout-common.tex', 'contents/chapters.tex', 'contents/code-index.tex', 'docs',
    'contents/AGENTS.md',
}
# 构建产物与缓存，新克隆中没有。
GENERATED = ('build/', 'tests/build/', 'preamble/tests/build/')
SKIPPED_DIRS = {'.git', 'build', '__pycache__'}

EXTENSIONS = 'tex|md|py|sh|txt|cpp|png|pdf|ttf|otf|commit'
SEGMENT = r'[A-Za-z0-9_.+-]+'
# 前后须是行首行尾、空白或括号等分隔符，避免从“示例 文件_1.cpp”这类名称中截出半个文件名。
FILE_PATH = re.compile(
    rf'(?:^|(?<=[\s{{(\[=,]))((?:\.\.?/)*(?:{SEGMENT}/)*{SEGMENT}\.(?:{EXTENSIONS}))(?=$|[\s}})\],:;])')
DIR_PATH = re.compile(rf'^(?:\.\.?/)*(?:{SEGMENT}/)+$')
INLINE_CODE = re.compile(r'`([^`\n]+)`')
SHELL_VARIABLE = re.compile(r'\$([A-Za-z_][A-Za-z0-9_]*)(?=[^\x00-\x7f])')


def project_files(root, use_git=True):
    """项目文件的相对路径（POSIX 写法），只含磁盘上存在的文件。"""
    names = None
    if use_git:
        try:
            out = subprocess.run(
                ['git', '-C', str(root), 'ls-files', '-z', '--cached', '--others', '--exclude-standard'],
                capture_output=True, check=True).stdout
            names = [name for name in out.decode('utf-8').split('\0') if name]
        except (OSError, subprocess.CalledProcessError):
            names = None
    if names is None:
        names = [path.relative_to(root).as_posix() for path in root.rglob('*')
                 if path.is_file() and not SKIPPED_DIRS & set(path.relative_to(root).parts)]
    return sorted(name for name in names if (root / name).is_file())


def directories(files):
    """文件清单中出现的全部目录，不含项目根目录。"""
    found = set()
    for name in files:
        parent = posixpath.dirname(name)
        while parent:
            found.add(parent)
            parent = posixpath.dirname(parent)
    return found


def agents_sizes(root, files):
    if 'AGENTS.md' not in files:
        return [], '没有根目录 AGENTS.md'
    agents = {name: (root / name).stat().st_size for name in files if posixpath.basename(name) == 'AGENTS.md'}
    problems = []
    if agents['AGENTS.md'] > ROOT_AGENTS_LIMIT:
        problems.append(f'AGENTS.md 为 {agents["AGENTS.md"]:,} 字节，超过 {ROOT_AGENTS_LIMIT:,} 字节的维护目标')
    parts = [f'根 {agents["AGENTS.md"]:,} 字节']
    for name in sorted(agents):
        if name == 'AGENTS.md':
            continue
        # Codex 从根目录逐级载入到工作目录，路径上的 AGENTS.md 合并计算。
        chain = [other for other in agents if posixpath.dirname(other) == '' or
                 (posixpath.dirname(name) + '/').startswith(posixpath.dirname(other) + '/')]
        total = sum(agents[other] for other in chain)
        parts.append(f'连同 {name} 共 {total:,} 字节')
        if total > COMBINED_LIMIT:
            problems.append(f'从根目录到 {name} 的 AGENTS.md 共 {total:,} 字节，超过 {COMBINED_LIMIT:,} 字节')
    return problems, '，'.join(parts)


def doc_candidates(text):
    """逐行给出 (行号, 路径)：行内代码中的路径与整段目录路径，以及代码块各行中的路径。"""
    fenced = False
    for number, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith('```'):
            fenced = not fenced
            continue
        for span in [line] if fenced else INLINE_CODE.findall(line):
            if not fenced and DIR_PATH.match(span):
                if span.strip('./'):      # 单独的 ./ 或 ../ 只是在说写法
                    yield number, span
                continue
            for match in FILE_PATH.finditer(span):
                yield number, match.group(1)


def resolves(path, doc_dir, files, dirs):
    target = path.rstrip('/')
    for base in (doc_dir, ''):
        candidate = posixpath.normpath(posixpath.join(base, target))
        if candidate in files or candidate in dirs or candidate in ABSENT_ON_PURPOSE:
            return True
        if (candidate + '/').startswith(GENERATED):
            return True
    if target in ABSENT_ON_PURPOSE or '__pycache__' in target.split('/'):
        return True
    if target.endswith('.pdf') and not target.startswith(('assets/', 'contents/')):
        return True
    if not path.startswith(('./', '../')):
        return any(name == target or name.endswith('/' + target) for name in files | dirs)
    return False


def doc_paths(root, files):
    file_set, dirs = set(files), directories(files)
    docs = [name for name in files if posixpath.basename(name) == 'AGENTS.md' or name == 'WRITING.md' or
            (posixpath.basename(name) == 'README.md' and name != 'README.md')]
    problems, count = [], 0
    for doc in docs:
        for number, path in doc_candidates((root / doc).read_text(encoding='utf-8')):
            count += 1
            if not resolves(path, posixpath.dirname(doc), file_set, dirs):
                problems.append(f'{doc}:{number}：`{path}` 不存在')
    return problems, f'{len(docs)} 份文档、{count} 处路径'


def readmes(root, files):
    checked = sorted(d for d in directories(files) if d != 'contents' and not d.startswith('contents/'))
    problems = []
    for d in checked:
        if f'{d}/README.md' in files:
            continue
        parent_readme = root / posixpath.dirname(d) / 'README.md'
        # 匹配完整目录名，避免 tests/ 被 contest-tests/ 等名称误满足。
        name = re.escape(posixpath.basename(d))
        if parent_readme.is_file() and re.search(
                rf'(?<![\w./+-]){name}/(?![\w./+-])', parent_readme.read_text(encoding='utf-8')):
            continue
        problems.append(f'{d}/ 缺少 README.md，且直接上级 README.md 未说明该目录')
    return problems, f'{len(checked)} 个目录'


def shell_variables(root, files):
    scripts = [name for name in files if name.endswith('.sh')]
    problems = []
    for name in scripts:
        for number, line in enumerate((root / name).read_text(encoding='utf-8').splitlines(), 1):
            for match in SHELL_VARIABLE.finditer(line):
                variable = match.group(1)
                problems.append(f'{name}:{number}：${variable} 后紧跟非 ASCII 字符，请写成 ${{{variable}}}')
    return problems, f'{len(scripts)} 个 .sh 文件'


CHECKS = [
    ('AGENTS.md 体量', agents_sizes),
    ('文档中的项目路径', doc_paths),
    ('目录 README', readmes),
    ('shell 变量展开', shell_variables),
]


def main(argv=None):
    files = project_files(ROOT)
    failed = 0
    for name, check in CHECKS:
        problems, summary = check(ROOT, files)
        if problems:
            failed += 1
            print(f'未通过：{name}（{summary}）')
            for problem in problems:
                print('  - ' + problem)
        else:
            print(f'通过：{name}（{summary}）')
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
