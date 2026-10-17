# 导言区效果检验

本目录只检验 `preamble/` 中的接口与各版布局，不放置或引用 `contents/` 的章节。修改约束与各类改动的验收范围见 `../AGENTS.md`。

## 组织

| 目录或文件 | 内容 |
| --- | --- |
| `mystyle/` | 四个自定义接口的独立样张，不加载各版布局 |
| `portrait/` | 竖版：扉页、目录、标题层级、分页、单色符号、代码卡片与配色、数学字体对照与综合样张，以及三个 PDF 检查脚本 |
| `landscape/` | 横版：扉页、分栏与连续章节、页眉、目录、接口跨栏、图片，以及布局与扉页两个检查脚本（加参数 `code` 检查代码版） |
| `code/` | 代码版：扉页、连续章节、代码卡片、配色与目录；检查复用 `landscape/` 的脚本 |
| `fixtures/` | 共用的代码与扉页资源，以及几版共用的样张正文（`*-body.tex`） |
| `pdfcheck.py` | 各组 PDF 检查脚本共用的检查工具、单位与几何常量 |
| `build/` | 各组的 PDF、日志、缓存与渲染图，按组分目录；被 Git 忽略 |

## 编译

所有样张都从项目根目录编译，章节、宏包与测试资源的路径不随样张所在目录改变。PDF、日志与 minted 缓存输出到 `build/<组名>/`，不写入源码目录。

各组由所在目录的 `run.sh` 编译，可从任意目录调用；不带参数时编译本组全部样张，也可只传入样张名。四个脚本都调用 `scripts/xelatex-converge.sh --quiet --strict`：每份样张至少两轮、最多八轮，直到收敛；日志出现缺字、Overfull、字体替换或页眉高度不足时失败，并保留产物。

```sh
bash preamble/tests/mystyle/run.sh
bash preamble/tests/portrait/run.sh
bash preamble/tests/landscape/run.sh
bash preamble/tests/code/run.sh
```

依赖 XeLaTeX、`latexminted` 与 `packages.tex` 中的宏包。`mystyle/` 的样张使用 TeX Live 的 Fandol 字体，另需 Maple Mono NF CN 提供代码标题的图标。其余三组使用各版的设计字体：Songti SC、PingFang SC、Maple Mono NF CN，以及 TeX Live 的 Latin Modern 字体与项目内的 Noto Emoji。各组的其他依赖见其 README。

## PDF 检查

`check-*.py` 读取 `build/` 中的样张 PDF，需要 Python 3 与 PyMuPDF（`python3 -m pip install --user pymupdf`），不由 `run.sh` 自动调用。它们共用本目录的 `pdfcheck.py`：

- 用 `Checker` 做显式检查，不用 `assert`，`python3 -O` 下照常生效；
- 每项失败只记录、不中断，按小节输出“通过”或“未通过”，最后列出全部未通过项并以 1 退出；
- 统一单位：PDF 坐标的单位是 bp，`mm()`、`pt()` 把毫米、TeX pt 换算为 bp，`to_pt()` 反向换算；
- 提供横版与代码版共用的几何常量（页眉线、正文下缘、栏分界）与代码配色，以及读取文字行、代码文字、扉页信息的函数。

| 命令（从任意目录运行） | 检查的样张 |
| --- | --- |
| `python3 preamble/tests/portrait/check-titlepage.py` | 竖版扉页 |
| `python3 preamble/tests/portrait/check-headings.py` | 竖版四、五级标题 |
| `python3 preamble/tests/portrait/check-syntax-colors.py` | 竖版代码配色与卡片 |
| `python3 preamble/tests/landscape/check-layout.py [code]` | 横版（或代码版）的纸张、流向、页眉、代码配色与跨栏、引用、目录、图片 |
| `python3 preamble/tests/landscape/check-titlepage.py [code]` | 横版（或代码版）扉页 |

`scripts/check.sh --full` 依次编译四组样张并运行上表的全部检查。检查通过后，仍要渲染查看 PDF 的边框、字形、长标题，以及跨页、跨栏的连接处。苹方简体与香港字形共用 TTC 中的轮廓表，`pdffonts` 可能显示 `PingFangHK`，不能据此判断字体被替换。

根目录 `run.sh` 只构建三版整书，不运行这些检验；整书产物在根目录的 `build/<版本>/`，与本目录的 `build/` 互不影响。整书的越栏检查是 `scripts/check-full.py`。

## 验证状态

2026-10-17，基于提交 `c642108`；工作区另有文档整理的改动，以及 `packages.tex`、`shared/twocolumn.tex` 中只改注释的三行。在 `LC_ALL=zh_CN.UTF-8` 下运行 `scripts/check.sh --full`：四组共 28 份样张都两轮收敛，严格日志检查与七项 PDF 检查全部通过。与改注释前构建的样张逐页比较文字与位置、字体、颜色、矢量图形、图片与链接，完全一致。本次没有人工查看样张 PDF。
