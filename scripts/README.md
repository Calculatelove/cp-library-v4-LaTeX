# 脚本

本目录存放构建与检查用的工具脚本，从任意工作目录运行都以项目根目录解析路径。工具的单元测试在 `tests/`；导言区样张及其专用检查在 `preamble/tests/`。根目录 `run.sh` 的说明也写在本文件。

| 文件 | 用途 |
| --- | --- |
| `check.sh` | 一键检查：默认快速检查，`--full` 另编译并检查导言区回归样张 |
| `check-docs.py` | 文档与脚本的静态检查：AGENTS.md 体量、文档中提到的项目路径、目录 README、shell 变量展开 |
| `generate-code.py` | 以横版入口为模板生成代码版入口 `main-code.tex` |
| `commit-info.sh` | 输出扉页使用的提交信息 |
| `xelatex-converge.sh` | 用 XeLaTeX 编译到目录与交叉引用稳定；根目录 `run.sh` 与 `preamble/tests` 各组的 `run.sh` 共用 |
| `check-full.py` | 读取 PDF 自带的版心与扉页标记，检查横版、代码版的两栏文字越界 |
| `pdf-metadata.tex`、`pdf_geometry.py` | 构建时记录 PDF 版心与扉页标记；供整书和样张检查读取 |
| `compare-pdf.py` | 逐页比较改动前后的整书与样张 PDF |
| `tests/` | 上述工具的单元测试，以及入口与布局的一致性检查，见其 README |

## 一键检查

```sh
scripts/check.sh          # 快速检查，约 1 秒；建议每次提交前运行
scripts/check.sh --full   # 另编译四组导言区样张并运行回归样张 PDF 功能检查，约 2 分钟
```

- 快速检查：`tests/` 中的全部单元测试（含入口与布局的一致性）、`generate-code.py --check`（代码版入口是否最新）与 `check-docs.py`。
- `--full` 另外依次运行 `preamble/tests` 四组样张的 `run.sh`，以及竖版、横版、代码版的样张 PDF 检查（各组的 `check.py`）。`build/` 中已有完整横版、代码版 PDF 时，再运行 `check-full.py`，越栏只输出警告。`check.sh` 不构建整书，所以这些 PDF 可能落后于源码，可对照输出中的扉页提交。
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
- 编译由 `xelatex-converge.sh` 完成，结束时打印末轮警告汇总。成功后日志会被删除，所以这行汇总就是末轮警告的记录。
- 只有收敛并生成非空 PDF 后，才清理本版已知的辅助文件、提交信息文件与 minted 缓存，不动其他版本或测试目录；失败时返回非零，保留辅助文件与日志。
- 全部目标成功后，在输出末尾以列表集中显示各版耗时和 PDF 绝对路径，并显示从脚本启动计算的总耗时（用户确认：避免信息被后续编译输出顶掉）。各版耗时包含该版准备、编译和清理，总耗时另含代码版入口生成与公共检查；使用 Bash 内置 `SECONDS` 按秒计时，以时、分、秒显示，省略高位零单位，零秒显示“不足 1 秒”。失败、帮助与用法错误不输出完成汇总。
- 不要用根目录的单轮 XeLaTeX 代替这个脚本，以免污染根目录或留下未收敛的产物。

需要查看警告的具体内容时，把控制台输出保存到被忽略的测试构建目录：

```sh
mkdir -p preamble/tests/build/landscape
./run.sh landscape > preamble/tests/build/landscape/full-build-console.txt 2>&1
```

### 整书警告

整书有已知的 Overfull、Underfull 等警告。页数以及警告的数量和位置都随正文变化，正文几乎每次提交都会改变它们，所以不写进文档（用户确认）。

- 判断排版或脚本改动的影响时，在同一提交上分别构建改动前、后的版本（改动前用该提交的干净副本），对比末轮警告汇总，并用 `compare-pdf.py` 逐页比较 PDF（见“逐页比较”），结果在汇报中说明。导言区改动的比较范围见 `preamble/AGENTS.md`。
- 日志中 xeCJK 的字体族重定义提示是预期的；不应出现缺字或字体替换。

## 文档与脚本检查

`check-docs.py` 只需 Python 3 标准库与 git：

```sh
python3 scripts/check-docs.py
```

- AGENTS.md 体量：根文件不超过 8 KiB；从根目录到任一子目录 AGENTS.md 一路上的 AGENTS.md 合计不超过 32 KiB（Codex 默认只自动载入合计前 32 KiB）。
- 文档中的项目路径：检查各 AGENTS.md、`WRITING.md` 与各子目录 README 中，行内代码与代码块里的路径。先按文档所在目录、再按项目根目录解析；不带 `./`、`../` 时，项目中有以它结尾的路径也算存在。根目录 `README.md` 由用户维护，不检查。含中文、空格或 `<版本>` 等占位符的写法跳过；PDF 是构建产物，`assets/`、`contents/` 下的除外。
- 文档有意提到、但项目中没有的路径列在脚本的 `ABSENT_ON_PURPOSE` 中，如规定不创建的 `setup.tex`、已删除的 `contents/AGENTS.md`；`build/` 等生成目录不检查。
- 目录 README：`contents/` 及其子目录以外，每个目录都有 README.md。
- shell 变量展开：`.sh` 中 `$变量名` 后不得紧跟非 ASCII 字符，原因见“修改须知”。
- 文件清单取自 git（已跟踪与未被忽略的文件）；不在 Git 仓库中时遍历目录。返回 0 表示全部通过，1 表示有问题，问题逐条带文件与行号列出。

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

输出四行：提交日期（按提交自身的时区，`YYYY-MM-DD`）、短哈希、提交说明首行、`clean` 或 `dirty`。取最新提交（HEAD），只改 `build/` 的提交同样计入；`build/` 以外有未提交修改（含未跟踪文件）时为 `dirty`（用户要求）。不在 Git 仓库中、找不到 git 或尚无提交时不输出内容，在标准错误说明原因并返回 0，扉页随之省略提交信息。根目录 `run.sh` 在每个版本编译前调用它，写入 `build/<版本>/main-<版本>.commit`，成功后随辅助文件清理；读取与排版见 `preamble/shared/titlepage.tex`。

提交说明原样输出，不做 TeX 转义；扉页按原样逐行读取。

## 编译收敛

`xelatex-converge.sh` 是根目录 `run.sh` 与 `preamble/tests/*/run.sh` 共用的编译循环，只依赖 Bash 与 XeLaTeX（minted 另需 `latexminted`）：

```sh
bash scripts/xelatex-converge.sh [--quiet] [--strict] <tex 文件> <输出目录>
```

- 两个路径都相对于项目根目录；脚本先回到项目根目录再编译。
- 至少两轮、最多八轮：比较 aux/toc/out/lof/lot 的校验和，并检查日志中的重编译提示（Rerun to get、Rerun LaTeX、Please rerun LaTeX、Label(s) may have changed）；最后确认生成了非空 PDF。
- 默认把 XeLaTeX 输出直接打印到终端，并逐轮提示（根目录 `run.sh` 使用）。`--quiet` 把输出写入 `<输出目录>/<文件名>-console.txt`，失败时显示末尾 40 行（样张使用）。
- `--strict` 在收敛后检查日志，有缺字、Overfull、字体替换或页眉高度不足时失败（样张使用；整书有已知的 Overfull，不用此项）。
- 收敛后汇总末轮日志中的警告：Overfull、Underfull、缺字、字体替换四类的数量，以及按来源统计的其他 LaTeX、宏包与文档类警告。
  - 默认模式逐项列出（含 0），例如“末轮警告：Overfull 3，Underfull 0，缺字 0，字体替换 0；其他：amsmath 2，xeCJK 3”。
  - `--quiet` 只在“N 轮收敛”之后列出不为零的项；`--strict` 失败时也附上汇总。
- 只编译、不清理：失败时辅助文件与日志都保留在输出目录。清理由调用方负责。
- 在源文件前载入 `pdf-metadata.tex`，记录 PDF 检查所需的实际版心与扉页标记，保持源文件的 jobname；记录说明见“完整 PDF 越栏检查”。
- 使用默认的受限 shell escape；返回 0 表示成功，1 表示编译失败、八轮未收敛、PDF 为空或严格检查不通过，2 表示用法错误或源文件不存在。

## 完整 PDF 越栏检查

`check-full.py` 检查完整横版或代码版 PDF 中两栏文字是否越出所在栏，只需要 PyMuPDF。它检查的是整本笔记，不属于导言区检验，所以放在本目录。默认检查 `build/landscape/main-landscape.pdf`，也可以传入其他 PDF：

```sh
python3 scripts/check-full.py
python3 scripts/check-full.py build/code/main-code.pdf
```

输出先列出扉页上的提交（短哈希、日期，含未提交修改时注明），找不到时也注明（用户确认）：被检查的是现有 PDF，不一定构建自当前源码。

返回值：0 表示检查完成（越栏只输出警告）；1 表示版心记录缺失、无效或不是双栏；2 表示找不到 PDF。

版心尺寸来自被检查 PDF 的 `BookGeometry` 页属性，扉页由 `BookTitlePage` 页属性标记，不依赖书名字号。`xelatex-converge.sh` 在源文件前载入 `pdf-metadata.tex`，随每页写入实际纸张、版心起点、栏宽、栏距、正文高度与栏数；不产生可见内容，不修改入口或正文。`pdf_geometry.py` 换算单位并核对记录与纸张一致。旧 PDF 缺少记录时需重建，不猜测旧布局。

判定规则（用户确认）：

- 左栏进入栏距、右栏进入外侧页边距，均输出警告；越过纸边时附加提示。不维护接受清单或上限，不要求为警告修改正文。
- 以右栏左边界区分两栏，完整落在栏距内的文字也报出。左栏文字伸到右栏后无法与右栏正文区分，报出的越界量只是下限，并附提示。
- 卡片框外行号按实际边框、同行代码及右对齐关系识别，不依赖字体名、字号或色值；栏距中的孤立数字不会笼统跳过。
- 跳过扉页、版心以外的页眉页脚与通栏“目录”标题。中文全角标点的前进宽度容易虚报，继续跳过；保留右栏行首标点与越界计算的容差。
- 输出被检查 PDF 的扉页提交信息；现有 PDF 不一定对应当前源码。

`tests/test_check_full.py` 用构造的 PDF 与数据检验不同版心、缺少记录、损坏记录、行号识别和越界规则，不依赖整书产物。

## 逐页比较

`compare-pdf.py` 逐页比较改动前、后的 PDF，只需要 PyMuPDF：

```sh
python3 scripts/compare-pdf.py --save <基线目录>   # 改动前：保存已构建的三版整书与回归样张
python3 scripts/compare-pdf.py <基线目录>          # 改动后重新构建，再与基线比较
python3 scripts/compare-pdf.py <旧> <新>           # 两个 PDF，或两个目录中相对路径相同的 PDF
```

- 基线包含 `build/<版本>/main-<版本>.pdf` 与 `preamble/tests` 各组 `run.sh` 列出的样张，只保存已构建的；基线目录须是新目录或空目录，以免混入旧基线。
- 比较纸张、文字及其字体、字号、颜色与位置，以及矢量图形、图片、链接（含目标位置）和书签；坐标与字号取到 0.01 bp。文字不同时先按字符对齐，再比较对上的字。
- 差异用于审阅影响范围，有意的视觉变化不要求与基线相同（用户确认）。有差异的 PDF 按类别各输出一行：字体、字号、颜色按“旧 → 新”汇总次数与涉及的字符，位置给出移动的字数与最大位移，并附页码；最后汇总相同、有差异与缺少对应 PDF 的份数。
- 只有一边的工作区有未提交修改时，整书扉页会因“含未提交修改”标签报出差异，属于预期。
- 返回值：0 表示全部相同；1 表示有差异或缺少对应的 PDF；2 表示用法错误或找不到输入。
- 读取与差异判定是独立的函数；`tests/test_compare_pdf.py` 用构造的数据测试差异判定。

## 修改须知

以下行为是约定，修改脚本时须保持。有单元测试的部分见 `tests/README.md`；`run.sh` 与 `xelatex-converge.sh` 没有单元测试，改动后要手工验证相应分支。

- `run.sh`、`xelatex-converge.sh`：至少两轮、最多八轮；失败时保留辅助文件与日志；成功后只清理本版的已知文件；各版本与测试目录的产物互相隔离；使用默认的受限 shell escape。
- `generate-code.py`：所有检查通过后才原子替换入口，失败不覆盖旧入口；`--check` 不写文件；不写死书籍信息。
- `commit-info.sh`：取 HEAD；dirty 判定排除 `build/`；不在 Git 仓库中、没有 git 或尚无提交时不输出内容，返回 0。
- `check-full.py`：从被检查 PDF 读取版心，记录缺失或无效时明确失败；越栏只输出警告。
- `compare-pdf.py`：只读比较，不改动构建产物；`--save` 只写入新目录或空目录，不覆盖、不删除已有文件。
- 脚本由 macOS 自带的 bash 3.2 执行。`$变量名` 后紧跟中文等非 ASCII 字符时写成 `${变量名}`，否则在 UTF-8 区域设置下，bash 会把多字节字符的前几个字节读进变量名，在 `set -u` 下报 unbound variable（`check-docs.py` 会检查）。也不要用关联数组、`${var,,}`、`mapfile` 等 bash 4 才有的写法。
- 用户的终端是 UTF-8 区域设置；agent 的终端若是 C 区域设置，验证时加 `LC_ALL=zh_CN.UTF-8`。

## 验证状态

2026-10-22，基于提交 `b7e65e0`，工作区有未提交修改。运行 `LC_ALL=zh_CN.UTF-8 scripts/check.sh --full`、`LC_ALL=zh_CN.UTF-8 ./run.sh all`、`python3 scripts/compare-pdf.py <基线整书目录> build` 与最终快速检查，均通过；三版整书与修改前同一工作区的 PDF 逐页相同，末轮警告汇总一致。新版越栏检查读取重建的整书，保留原有警告规则。

自动检查覆盖版心记录的读取与无效记录拒绝、不同版心的越界判定、不依赖字体和颜色的行号识别；手工命令验证了构建的安静与普通输出、带空格源路径、编译失败返回非零并保留日志。样张渲染抽查与隔离副本的设计变更、故障注入范围见 `preamble/tests/README.md`。未逐页人工查看整书，未做实物打印。
