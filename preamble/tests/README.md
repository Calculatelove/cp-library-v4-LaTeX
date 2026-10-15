# 导言区效果检验

本目录仅测试 `preamble/` 中的接口和布局，不放置或引用 `contents/` 的章节测试。

## 组织与状态

| 目录 | 职责 | 当前状态 |
| --- | --- | --- |
| `mystyle/` | 四个自定义接口的颜色、标题、路径、多语言及跨页行为 | 已搬迁五个检验文件；运行 `mystyle/run.sh`，见其 README。 |
| `portrait/` | 竖版扉页、字体、边距、标题、目录、页码及接口组合效果 | 已实现扉页、综合、分页、单色符号样张和两份数学字体对照；运行 `portrait/run.sh`，见其 README。 |
| `landscape/` | 横版扉页、分栏、连续章节、页眉、目录和接口跨栏 | 已实现八份样张，以及布局检查 `check-layout.py` 与扉页检查 `check-titlepage.py`（两者加参数 `code` 检查代码版）；运行 `landscape/run.sh`，见其 README。 |
| `code/` | 代码版扉页、标题层级、代码密度、长行与跨页效果 | 已实现五份样张，其中四份正文与横版共用；布局与扉页检查复用 `landscape/` 的脚本（参数 `code`），运行 `code/run.sh`，见其 README。 |
| `fixtures/` | 共用代码资源、扉页资源与多版共用的样张正文 | 保留现有五个资源；新增横版人工长代码资源检验连续跨栏、三版扉页样张共用的提交信息与配图资源，以及四份共用样张正文（`*-body.tex`）。 |
| `pdfcheck.py` | 各组 PDF 检查脚本共用的检查工具、单位与几何常量 | 2026-10-16 新增，见下文“PDF 检查脚本”。 |
| `build/` | 按 `mystyle/`、`portrait/`、`landscape/`、`code/` 隔离生成产物 | 已被 Git 忽略，不维护 README。 |

版式检验可引用 `fixtures/` 中的共同样张以比较效果，代码版可增加密集代码样例。接口检验不替代各版布局验收。暂不创建空布局测试。

## 路径与运行规则

所有检验均从项目根目录编译；章节、宏包配置和测试资源路径不随测试源码目录改变。源码位于对应类别目录，PDF、日志和 minted 缓存统一输出至 `preamble/tests/build/<类别>/`，不得在源码目录生成产物。

现有检验依赖 XeLaTeX、项目宏包、TeX Live Fandol 字体，代码检验另需可用的 `latexminted`。不默认开启不受限 shell escape；测试字体不决定最终字体。

四组样张各由所在目录的 `run.sh` 编译，可从任意目录调用；不带参数时编译本组全部样张，也可只传入样张名。四个脚本都调用 `scripts/xelatex-converge.sh`，即与根目录 `run.sh` 共用的编译循环：每份样张至少两轮、最多八轮直至收敛；日志出现缺字、Overfull、字体替换或页眉高度不足时失败，并保留产物。

```sh
bash preamble/tests/mystyle/run.sh
bash preamble/tests/portrait/run.sh
bash preamble/tests/landscape/run.sh
bash preamble/tests/code/run.sh
```

各组的 PDF 检查脚本（`check-*.py`）不由 `run.sh` 自动调用；编译后按下节单独运行，或用 `scripts/check.sh --full` 一并编译和检查。详细检查项见 `mystyle/README.md`。编译成功后仍需检查 PDF 的内容、颜色、缺字、溢出及跨页，历史结果不作为新实现的验证证据。旧 `build/` 顶层产物不代表新目录中的检验结果。

## PDF 检查脚本

各组的 `check-*.py` 读取 `preamble/tests/build/` 中的样张 PDF，需要 Python 3 与 PyMuPDF（`python3 -m pip install --user pymupdf`；本机为 Python 3.9.6、PyMuPDF 1.26.5）。它们共用本目录的 `pdfcheck.py`：

- 用 `Checker` 做显式检查，不用 `assert`，`python3 -O` 下照常生效。
- 每项失败只记录、不中断；按小节输出“通过”或“未通过”，最后列出全部未通过项，并以 1 退出。
- 统一单位：PDF 坐标的单位是 bp；`mm()`、`pt()` 把毫米、TeX pt 换算为 bp，`to_pt()` 反向换算。
- 提供横版与代码版共用的几何常量（页眉线、正文下缘、栏分界）和代码配色，以及读取文字行、代码文字、扉页信息的公共函数。

| 命令（从任意目录运行） | 检查的样张 |
| --- | --- |
| `python3 preamble/tests/portrait/check-titlepage.py` | 竖版扉页 |
| `python3 preamble/tests/portrait/check-headings.py` | 竖版四、五级标题 |
| `python3 preamble/tests/portrait/check-syntax-colors.py` | 竖版代码配色与卡片 |
| `python3 preamble/tests/landscape/check-layout.py [code]` | 横版（或代码版）的纸张、流向、页眉、代码配色与跨栏、引用、目录、图片 |
| `python3 preamble/tests/landscape/check-titlepage.py [code]` | 横版（或代码版）扉页 |

`scripts/check.sh --full` 会依次编译四组样张，并运行上表全部检查，见 `scripts/README.md`。

## 与三版构建的关系

根目录 `run.sh` 只构建三版主文档，不运行这些检验；主文档产物在根目录 `build/<版本>/`。本目录使用独立的 `preamble/tests/build/`，清理范围互不影响。完整横版、代码版 PDF 的越栏检查不属于导言区检验，在 `scripts/check-full.py`（2026-10-16 由 `landscape/` 移入）。

纵向版检验（2026-10-12）：三份样张编译收敛，综合样张 6 页、两份数学样张各 1 页；全部 8 页已渲染检查。既有五个接口检验重新两轮编译通过。完整笔记尚未验证。

InputCode 卡片样式与语言图标的纵向检验见 `portrait/code-cards.tex`，由 `portrait/run.sh` 一同编译。公共 `mystyle.tex` 使用 Maple Mono NF CN 的 Nerd Font 字形，因此独立接口检验也需要该字体。


代码版新增 `code/`：连续章节、代码卡片、配色和目录四份独立样张；运行方式见 `code/README.md`。
