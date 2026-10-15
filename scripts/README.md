# 脚本

本目录存放构建与检查用的工具脚本，从任意工作目录运行均以项目根目录解析路径。工具自身的单元测试在 `tests/`；导言区样张及其专用检查仍在 `preamble/tests/`。

| 文件 | 用途 |
| --- | --- |
| `check.sh` | 一键检查：默认快速检查，`--full` 另编译并检查全部导言区样张 |
| `generate-code.py` | 以横版入口为模板生成代码版入口 `main-code.tex` |
| `commit-info.sh` | 输出扉页使用的提交信息 |
| `xelatex-converge.sh` | 用 XeLaTeX 编译至目录与交叉引用稳定；根目录 `run.sh` 与 `preamble/tests` 各组运行脚本共用 |
| `check-full.py` | 先核对纸张与栏边几何，再检查完整横版、代码版 PDF 的两栏文字越界 |
| `tests/` | `generate-code.py`、`commit-info.sh`、`check-full.py` 的单元测试，以及竖版、横版入口的一致性检查 |

运行全部单元测试（Python 3 标准库与 git；`test_check_full.py` 另需 PyMuPDF，未安装时跳过）：

```sh
python3 -B -m unittest discover -s scripts/tests
```

## 一键检查

```sh
scripts/check.sh          # 快速检查，约 1 秒；建议每次提交前运行
scripts/check.sh --full   # 另编译四组导言区样张并运行全部样张 PDF 检查，约 1–2 分钟
```

- 快速检查包括：`tests/` 中的全部单元测试，以及 `generate-code.py --check`（代码版入口是否最新）。
- 单元测试里的 `test_entries.py` 检查竖版、横版两个手写入口除布局一行外逐行相同，章节清单、元信息、扉页与目录都包括在内；某版确需不同的设置应放进该版布局文件，而不是写在入口。代码版入口由生成器以横版入口为模板生成，变换规则由 `test_generate_code.py` 检查。
- `--full` 另外依次运行：`preamble/tests` 四组样张的 `run.sh`，以及竖版扉页、标题、配色，横版与代码版的布局、扉页，共七项 PDF 检查。`build/` 中已有完整横版、代码版 PDF 时，再运行 `check-full.py`，越栏只输出警告。完整三版 PDF 仍由 `./run.sh` 构建，`check.sh` 不调用它。
- 某一步失败不会中断后续步骤，最后汇总列出失败的步骤；有失败时返回 1，用法错误返回 2。PDF 检查需要 PyMuPDF，见 `preamble/tests/README.md`。

## 代码版生成

`generate-code.py` 使用 Python 3 标准库：

```sh
python3 scripts/generate-code.py
python3 scripts/generate-code.py --check
python3 -B scripts/tests/test_generate_code.py
./run.sh code
```

章节顺序取自 `main-landscape.tex` 的 contents 引用；章内按源码顺序保留 `InputCode` 与完整 minted 环境，只输出这些代码所属的原有标题及祖先标题。无代码分支不输出。未被入口引用的编号章节会警告，未引用的 code 文件会列出但不收录。不会创建 code-index.tex，不修改章节或代码文件。

生成 `main-code.tex`，不要手工编辑它；修改横版入口或章节后重新生成。代码版入口以横版入口为模板（2026-10-16 起），只做三处变换：

1. `\input{preamble/layout-landscape.tex}` 换成 `\input{preamble/layout-code.tex}`；
2. 在导言区末尾、`\begin{document}` 之前加 `\EditionLabel{代码版}`；
3. 把每个章节引用换成该章中的代码及其所属标题，没有代码的章节整章省略。

横版入口中的其他内容，包括书名等元信息、`\maketitle`、`\tableofcontents` 和注释，都原样沿用；生成器本身不写死任何书籍信息。横版入口须恰好有一行布局引用和一行 `\begin{document}`，章节引用须单独占一行，否则报错、不生成入口。连续空行合并为一行。

保留代码参数、语言、缩进、空行和注释，保留标题格式和可选短标题。生成入口逐项标记来源行号。`--check` 不写文件，入口过期返回非零。`run.sh code/all` 在入口预检前自动生成，失败则停止。

解析器针对当前项目的静态 LaTeX 写法，支持平衡花括号、注释和 minted 原样文本；不是 TeX 宏展开器。不支持宏动态生成标题/代码或条件分支选目。遇到已识别的其他代码环境、带星号标题、嵌套 input、缺失文件、参数未闭合时报告来源并停止。引入新内容语法时需扩展解析与测试，不应把复杂 TeX 当作已自动支持。

所有检查成功后才原子替换入口；失败不覆盖旧入口，相同内容不重复写入。首次核对为 79 处 InputCode、20 段 minted，数量不是永久限制。测试覆盖注释中的假命令、嵌套标题、代码内假标题、空分支裁剪、缺失文件、坏语法与真实内容顺序/逐段一致性；三处变换的完整输出（在临时模板上逐字比对）；模板结构错误（布局行缺失或重复、缺少 `\begin{document}`、章节引用不单独成行）；真实入口的代码版导言区等于横版导言区换布局一行再加版本标记。还检查竖版、横版入口与生成结果中的 `\TitlePageImage` 路径与 Git 中的文件名逐字一致，包括大小写（尚未加入 Git 的新文件也计入）。该项按 Git 记录比对，可以发现 macOS 上只改大小写、Git 未记录的改名；不在 Git 仓库中时跳过。

## 扉页提交信息

`commit-info.sh` 只依赖 Bash 与 git，结果输出到标准输出：

```sh
bash scripts/commit-info.sh
python3 -B scripts/tests/test_commit_info.py
```

输出四行：提交日期（按提交自身时区，`YYYY-MM-DD`）、短哈希、提交说明首行、`clean` 或 `dirty`。取最新提交（HEAD），只改 `build/` 的提交同样计入；`build/` 以外有未提交修改（含未跟踪文件）时为 `dirty`。不在 Git 仓库中、找不到 git 或尚无提交时不输出内容，在标准错误说明原因并返回 0，扉页随之省略提交信息。根目录 `run.sh` 在每个版本编译前调用它，写入 `build/<版本>/main-<版本>.commit`，成功后随辅助文件清理；读取与排版见 `preamble/shared/titlepage.tex`。

提交说明原样输出，不做 TeX 转义；扉页按原样逐行读取。测试在临时仓库中运行并屏蔽用户 Git 配置，覆盖非仓库、无提交、提交时区、特殊字符、只改 `build/` 的提交（如取消跟踪 PDF），以及 `build/` 内外的修改与未跟踪文件；改用本地时区、`log` 仍排除 `build/`、`status` 不排除 `build/`、忽略未跟踪文件四种错误实现均会被测试发现。

## 编译收敛

`xelatex-converge.sh` 是根目录 `run.sh` 与 `preamble/tests/*/run.sh` 共用的编译循环，只依赖 Bash 与 XeLaTeX（minted 另需 `latexminted`）：

```sh
bash scripts/xelatex-converge.sh [--quiet] [--strict] <tex 文件> <输出目录>
```

- 两个路径都相对于项目根目录；脚本先回到项目根目录再编译。
- 至少两轮、最多八轮：比较 aux/toc/out/lof/lot 的校验和，并检查日志中的重编译提示（Rerun to get、Rerun LaTeX、Please rerun LaTeX、Label(s) may have changed）；最后确认生成了非空 PDF。
- 默认把 XeLaTeX 输出直接打印到终端，并逐轮提示（根目录 `run.sh` 使用）。`--quiet` 把输出写入 `<输出目录>/<文件名>-console.txt`，失败时显示末尾 40 行（样张使用）。
- `--strict` 在收敛后检查日志，有缺字、Overfull、字体替换或页眉高度不足时失败（样张使用；完整笔记仍有已知的 Overfull，不用此项）。
- 收敛后汇总末轮日志中的警告（2026-10-16 起）：Overfull、Underfull、缺字、字体替换四类的数量，以及按来源统计的其他 LaTeX、宏包与文档类警告。
  - 默认模式逐项列出（含 0），例如：“末轮警告：Overfull 3，Underfull 0，缺字 0，字体替换 0；其他：amsmath 2，xeCJK 3”。
  - `--quiet` 只在“N 轮收敛”后列出不为零的项；`--strict` 失败时也附上汇总。
  - 根目录 `run.sh` 成功后会删除日志，因此构建结束时的这行汇总就是末轮警告的记录。
- 只编译、不清理：失败时辅助文件与日志都保留在输出目录。清理由调用方负责，根目录 `run.sh` 只在成功后清理本版已知辅助文件。
- 使用默认受限 shell escape；返回 0 表示成功，1 表示编译失败、八轮未收敛、PDF 为空或严格检查不通过，2 表示用法错误或源文件不存在。

## 完整 PDF 越栏检查

`check-full.py` 检查完整横版或代码版 PDF 中两栏文字是否越出所在栏，只需要 PyMuPDF（2026-10-16 起去掉了从未在本机运行过的 pdfplumber 备用分支）。2026-10-16 由 `preamble/tests/landscape/` 移入本目录：它检查的是整本笔记，不属于导言区检验。默认检查 `build/landscape/main-landscape.pdf`，也可传入其他 PDF：

```sh
python3 scripts/check-full.py
python3 scripts/check-full.py build/code/main-code.pdf
```

返回值：0 表示检查完成（越栏只输出警告）；1 表示几何自检不通过；2 表示找不到 PDF。

几何自检（2026-10-16）：12 mm 边距、132.5 mm 栏宽、8 mm 栏距写死在脚本里，与横版、代码版布局一致。布局改了而脚本没有同步时，越栏结果会悄悄出错，所以脚本先做两项核对：

- 每页都是 A4 横向；
- 左右两栏的左缘、右缘四条栏边，各至少有 20 行正文与之对齐（容差 0.2 mm）。

任一项不通过就报错并返回 1，不输出越栏结果。实测横版四条栏边分别有 811、259、854、257 行对齐，代码版各有 56–89 行；用竖版 PDF 试验时只有 0–7 行，会被拦下。布局参数改变时，同步修改脚本中的几何常量。

根目录 `run.sh` 构建结束时会打印末轮警告汇总；需要查看警告的具体内容时，再把控制台输出保存到已忽略的测试构建目录：

```sh
mkdir -p preamble/tests/build/landscape
./run.sh landscape > preamble/tests/build/landscape/full-build-console.txt 2>&1
```

中文全角标点按前进宽度会虚报约 6.7 pt，脚本跳过这些字符和页眉、页脚、目录通栏标题。扉页通栏居中、不分栏，以 44 pt 书名识别并整页跳过。读取、几何自检、越界判定分别是独立函数，由 `main()` 调用；`tests/test_check_full.py` 用构造的数据测试分栏、越界与几何自检，不依赖 `build/` 中的 PDF。

脚本以右栏左边界区分两栏，字框起点在右栏之前的字符都计入左栏。早先以左栏右边界分栏时，整个落在栏距内的越栏文字会被当作右栏、得到负溢出而漏报；2026-10-14 已修正，并以人工越栏样例确认可以报出。右栏行首的“等标点经 xeCJK 压缩后字框约提前 0.5 pt，留 1 pt 容差；居中的页脚页码位于栏距位置，跳过。左栏文字伸到右栏位置后，后续字符无法与右栏正文区分，此时报出的越界量只是下限，并附提示。

规则由用户于 2026-10-14 更新：左栏进入栏距、右栏进入外侧页边距均输出警告；超过纸边时附加提示。不维护“登记接受”的溢出清单，不设置 10 mm 上限，不要求为警告修改正文。警告包含页码、栏位、越界量和末字，每页每栏汇总最大越界量。无论是否存在溢出，正常完成检查均返回 0；几何自检不通过返回 1，PDF 不存在返回 2，无法读取等运行错误仍报错。
