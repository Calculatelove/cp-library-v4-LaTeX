# 脚本

本目录存放构建与检查用的工具脚本，从任意工作目录运行都以项目根目录解析路径。工具的单元测试在 `tests/`；导言区样张及其专用检查在 `preamble/tests/`。根目录 `run.sh` 的说明也写在本文件。

| 文件 | 用途 |
| --- | --- |
| `check.sh` | 一键检查：默认快速检查，`--full` 另编译并检查导言区回归样张 |
| `generate-code.py` | 以横版入口为模板生成代码版入口 `main-code.tex` |
| `commit-info.sh` | 输出扉页使用的提交信息 |
| `xelatex-converge.sh` | 用 XeLaTeX 编译到目录与交叉引用稳定；根目录 `run.sh` 与 `preamble/tests` 各组的 `run.sh` 共用 |
| `tests/` | 上述工具的单元测试，以及入口一致性检查，见其 README |

保留现有简短脚本的分工，不继续合并入口，也不添加自动判断改动影响范围的工具（用户确认：避免为简化操作引入新的维护机制）；验证范围按 `preamble/AGENTS.md` 选择。

## 一键检查

```sh
scripts/check.sh          # 快速检查；建议每次提交前运行
scripts/check.sh --full   # 编译默认回归样张并检查 PDF 功能
```

- 快速检查：`tests/` 中的全部单元测试（含入口一致性）、`generate-code.py --check`（代码版入口是否最新）。
- `--full` 另外依次运行 `preamble/tests` 各版的 `run.sh`，以及竖版、横版、代码版的样张 PDF 检查（代码版复用横版检查）。此命令不构建或扫描整书；日常修改按 `preamble/AGENTS.md` 的分级范围选择验证。
- 某一步失败不会中断后续步骤，最后汇总列出失败的步骤；有失败时返回 1，用法错误返回 2。PDF 检查需要 PyMuPDF，见 `preamble/tests/README.md`。

## 整书构建

```sh
./run.sh             # 默认 portrait
./run.sh landscape
./run.sh code
./run.sh all
./run.sh --help
```

- 产物为 `build/<版本>/main-<版本>.pdf`，辅助文件与 minted 缓存也按版本隔离。根目录 `build/` 被 Git 忽略；PDF 由用户在提交后编译，发布到 GitHub Release。
- 先检查 `xelatex`、`latexminted` 是否可用；空入口提前报错。`code` 与 `all` 先运行 `generate-code.py` 生成代码版入口，生成失败则不启动编译。`all` 先检查全部入口，再按竖版、横版、代码版依次构建，遇到失败停止。
- 每个版本编译前调用 `commit-info.sh`，把提交信息写入 `build/<版本>/main-<版本>.commit` 供扉页读取；不在 Git 仓库中时不生成，`build/` 以外有未提交修改时在终端提示。
- 编译由 `xelatex-converge.sh` 完成，结束时打印末轮警告汇总；完整日志保留在各版本输出目录的 `.log` 文件中。
- 收敛并生成非空 PDF 后，保留本版辅助文件、日志、提交信息文件与 minted 缓存（用户确认：减少重复构建耗时并方便排查警告）；失败时返回非零，也保留这些文件。产物均被 Git 忽略。
- 旧的 `.aux`、`.toc` 可能引用已删除或改名的宏，导致首轮编译报错；遇到这种情况，删除受影响的 `build/<版本>/` 后重新构建。升级 minted、Pygments 或 TeX Live 后的缓存清理见 `preamble/AGENTS.md`。
- 全部目标成功后，在输出末尾集中显示各版耗时、PDF 路径与总耗时；失败、帮助与用法错误不输出这份汇总（用户确认：避免信息被后续编译输出顶掉）。
- 不要用根目录的单轮 XeLaTeX 代替这个脚本，以免污染根目录或留下未收敛的产物。

### 整书警告

整书有已知的 Overfull、Underfull 等警告。页数以及警告的数量和位置都随正文变化，正文几乎每次提交都会改变它们，所以不写进文档（用户确认）。

- 按 `preamble/AGENTS.md` 选择需要构建的版本，查看末轮警告并抽查受影响页面。整书不做自动逐页精细比较或 PDF 越栏扫描（用户确认：避免为日常视觉调整维护额外工具链）。
- 日志中 xeCJK 的字体族重定义提示是预期的；不应出现缺字或字体替换。

## 代码版生成

`generate-code.py` 使用 Python 3 标准库：

```sh
python3 scripts/generate-code.py
python3 scripts/generate-code.py --check
python3 -B scripts/tests/test_generate_code.py
./run.sh code
```

章节顺序取自 `main-landscape.tex` 的 contents 引用；章内按源码顺序保留 `\InputCode` 与完整的 minted 环境，只输出这些代码所属的原有标题及其祖先标题，没有代码的分支不输出。未被入口引用的编号章节会警告，未被引用的代码文件会列出但不收录。不修改章节或代码文件。收录范围由用户批准。

生成 `main-code.tex`，不要手工编辑它；修改横版入口或章节后重新生成。代码版入口以横版入口为模板（用户批准），只做三处变换：

1. `\input{preamble/layout-landscape.tex}` 换成 `\input{preamble/layout-code.tex}`；
2. 在导言区末尾、`\begin{document}` 之前加 `\EditionLabel{代码版}`；
3. 把每个章节引用换成该章中的代码及其所属标题，没有代码的章节整章省略。

横版入口中的其他内容，包括书名等元信息、`\maketitle`、`\tableofcontents` 和注释，都原样沿用；生成器本身不写死任何书籍信息。横版入口须恰好有一行布局引用和一行 `\begin{document}`，章节引用须单独占一行，否则报错、不生成入口。连续空行合并为一行。

保留代码参数、语言、缩进、空行和注释，保留标题格式和可选短标题。生成的入口不标注来源文件或行号（用户确认）：每章的一级标题与章节文件同名，已能看出出处；行号随正文增删而变，写进入口会让只改正文的提交也要重新生成入口。`--check` 不写文件，入口过期时返回非零。

解析器针对当前项目的静态 LaTeX 写法，支持平衡花括号、注释和 minted 原样文本；不是 TeX 宏展开器，不支持用宏动态生成标题或代码，也不支持条件分支选目。遇到其他代码环境、带星号的标题、嵌套 `\input`、缺失文件或未闭合的参数时，报告来源并停止。正文中可用的写法见 `WRITING.md`；引入新的内容语法时，需要扩展解析与测试。

所有检查通过后才原子替换入口；失败时不覆盖旧入口，内容相同时不重复写入。测试内容见 `tests/README.md`。

## 扉页提交信息

`commit-info.sh` 只依赖 Bash 与 git，结果输出到标准输出：

```sh
bash scripts/commit-info.sh
python3 -B scripts/tests/test_commit_info.py
```

输出四行：提交日期（按提交自身的时区，`YYYY-MM-DD`）、短哈希、提交说明首行、`clean` 或 `dirty`。取最新提交（HEAD），只改 `build/` 的提交同样计入；`build/` 以外有未提交修改（含未跟踪文件）时为 `dirty`（用户要求）。不在 Git 仓库中、找不到 git 或尚无提交时不输出内容，在标准错误说明原因并返回 0，扉页随之省略提交信息。根目录 `run.sh` 在每个版本编译前调用它，写入 `build/<版本>/main-<版本>.commit`，每次构建时重新生成，成功后随辅助文件保留；读取与排版见 `preamble/shared/titlepage.tex`。

提交说明原样输出，不做 TeX 转义；扉页按原样逐行读取。

## 编译收敛

`xelatex-converge.sh` 是根目录 `run.sh` 与 `preamble/tests/*/run.sh` 共用的编译循环，只依赖 Bash 与 XeLaTeX（minted 另需 `latexminted`）：

```sh
bash scripts/xelatex-converge.sh [--quiet] [--strict] <tex 文件> <输出目录>
```

- 两个路径都相对于项目根目录；脚本先回到项目根目录再编译。
- 自动重复编译直到目录与交叉引用稳定；未能收敛或没有生成有效 PDF 时失败。
- 默认把 XeLaTeX 输出直接打印到终端，并逐轮提示（根目录 `run.sh` 使用）。`--quiet` 把输出写入 `<输出目录>/<文件名>-console.txt`，失败时显示日志末尾（样张使用）。
- `--strict` 在收敛后检查日志，有缺字、Overfull、字体替换或页眉高度不足时失败（样张使用；整书有已知的 Overfull，不用此项）。
- 收敛后汇总末轮日志的警告；`--quiet` 只显示非零项。
- 只编译、不清理：失败时辅助文件与日志都保留在输出目录。需要清理时手动删除对应输出目录。
- 使用默认的受限 shell escape；返回 0 表示成功，1 表示编译失败、达到编译轮数上限仍未收敛、PDF 为空或严格检查不通过，2 表示用法错误或源文件不存在。

## 修改须知

以下行为是约定，修改脚本时须保持。有单元测试的部分见 `tests/README.md`；`run.sh` 与 `xelatex-converge.sh` 没有单元测试，改动后要手工验证相应分支。

- `run.sh`、`xelatex-converge.sh`：至少两轮、最多八轮；失败时保留辅助文件与日志；成功后保留辅助文件、日志与缓存；各版本与测试目录的产物互相隔离；使用默认的受限 shell escape。
- `generate-code.py`：所有检查通过后才原子替换入口，失败不覆盖旧入口；`--check` 不写文件；不写死书籍信息。
- `commit-info.sh`：取 HEAD；dirty 判定排除 `build/`；不在 Git 仓库中、没有 git 或尚无提交时不输出内容，返回 0。
- 脚本由 macOS 自带的 bash 3.2 执行。`$变量名` 后紧跟中文等非 ASCII 字符时写成 `${变量名}`，否则在 UTF-8 区域设置下，bash 会把多字节字符的前几个字节读进变量名，在 `set -u` 下报 unbound variable。也不要用关联数组、`${var,,}`、`mapfile` 等 bash 4 才有的写法。
- 用户的终端是 UTF-8 区域设置；agent 的终端若是 C 区域设置，验证时加 `LC_ALL=zh_CN.UTF-8`。
