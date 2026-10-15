# 自定义接口效果检验

本目录用于 `preamble/mystyle.tex` 四个自定义接口的独立效果检验，不加载三版布局或实际章节。公共 `mystyle.tex` 现在还需要 Maple Mono NF CN 字体，以提供代码标题的 Nerd Font 图标。当前已有 `highlight.tex`、`input-code.tex`、`input-code-pages.tex`、`quoteblock.tex` 和 `separator.tex`，覆盖四个自定义接口。

历史实现曾有高亮、代码插入、引用块、分隔线四类检验，但旧源码及产物当前不在工作区，不能引用旧结果作为新实现的验证证据。

每个接口至少提供一个可独立编译的 `.tex` 检验文件：

| 接口 | 需要展示的效果 |
| --- | --- |
| `\Highlight` | 中文短语、粗体、行内公式；无额外内边距，且颜色不影响后文。 |
| `\InputCode` | 默认文件名、显式标题、中文与带空格路径、多语言高亮、长代码跨页。 |
| `quoteblock` | 多段正文、列表、公式、跨页；标准 `quote` 保持不变。当前不要求嵌套。 |
| `\Separator{}` | 普通正文、列表及引用块中的宽度和间距，不强制分页。 |

统一从项目根目录编译，资源路径也从项目根目录解析。可以共享测试导言区，但每个接口须有明确可查看的示例。

全部样张由 `run.sh` 编译，可从任意目录调用；不带参数时编译五份样张，也可只传入样张名。脚本调用 `scripts/xelatex-converge.sh`（与根目录 `run.sh` 共用的编译循环），每份至少两轮、最多八轮直至收敛；日志出现缺字、Overfull、字体替换或页眉高度不足时失败，并保留产物：

```sh
bash preamble/tests/mystyle/run.sh
bash preamble/tests/mystyle/run.sh input-code input-code-pages
```

`highlight.tex` 需要 XeLaTeX、项目 `packages.tex` 中列出的宏包，以及 TeX Live 的 Fandol 字体。

源码为 `preamble/tests/mystyle/highlight.tex`，PDF 与日志位于 `preamble/tests/build/mystyle/`。此检验包含中文、粗体、行内公式，以及高亮前后的正文；编译时还比较高亮内容与原内容的宽度、高度和深度，确认没有额外内边距。测试字体不决定项目最终字体。

`\InputCode` 的两个检验还需要 `minted`、可执行的 `latexminted` 和 TeX Live Fandol 字体。本机 `minted` 首轮可能只输出 `<MINTED>` 占位内容，第二轮才载入生成的代码高亮文件；`run.sh` 至少编译两轮。

源码为 `preamble/tests/mystyle/input-code.tex`、`preamble/tests/mystyle/input-code-pages.tex`，代码资源位于 `preamble/tests/fixtures/`，包括 `示例 文件_1.cpp`、`sample.py`、`sample.sh`、`Makefile test` 和 `long-code.cpp`。前者检验默认与显式文件名、中文和带空格路径、C++ / Python / Bash / Makefile，以及各语言的 `\setminted` 设置；后者检验长代码跨页及续页不重复标题。PDF、日志及 minted 缓存都位于 `preamble/tests/build/mystyle/`。测试从项目根目录编译，不需要开放不受限的 shell escape。

`quoteblock.tex` 需要 XeLaTeX、项目宏包及 TeX Live Fandol 字体。

源码为 `preamble/tests/mystyle/quoteblock.tex`，PDF 与日志位于 `preamble/tests/build/mystyle/`。检验包含多段中文正文、列表、展示公式、标准 `quote` 和跨页引用块；应检查每页的浅灰背景及左侧竖线，竖线外侧至文字约一个中文字宽，续页间距保持一致。引用块嵌套当前不在要求内。

`separator.tex` 需要 XeLaTeX、项目宏包及 TeX Live Fandol 字体。

源码为 `preamble/tests/mystyle/separator.tex`，PDF 与日志位于 `preamble/tests/build/mystyle/`。检验普通正文、列表和 `quoteblock` 中的横线宽度及上下间距，产物应为单页。测试字体不决定项目最终字体。

生成的 PDF、日志和缓存集中放在 `preamble/tests/build/mystyle/`，该目录已加入忽略规则；测试源码与资源保留。编译成功后仍需检查实际 PDF，不能只检查进程退出码。


共用测试资源说明见 `preamble/tests/fixtures/README.md`；目录分工见 `preamble/tests/README.md`。新增接口样例放在本目录，新增版式样例放在对应版本目录。

## 本次搬迁验证（2026-10-12）

五个样例均从项目根目录完成两轮 XeLaTeX 编译；资源文件 SHA-256 与搬迁前一致。日志未出现缺字、Overfull 或 LaTeX 错误，PDF 文本未包含 `<MINTED>` 占位。highlight、input-code、separator 各一页，input-code-pages、quoteblock 各两页；长代码标题仅出现一次。本轮为路径搬迁与编译回归检查，未重新进行逐页视觉验收。

## 引用块段落修复（2026-10-12）

`quoteblock.tex` 显式使用无首行缩进、`3pt plus 1pt minus 1pt` 段间距，并在两个引用块内及块后检查段间距。修复前检查报错，实际为 `0pt`；`mystyle.tex` 设置 `parbox=false` 后保留正文段落参数。按上述命令编译两轮，引用块 2 页、分隔线 1 页；日志无缺字、Overfull 或字体替换，全部 3 页已渲染检查，多段、列表、公式和跨页装饰正常。标准 `quote` 定义不变。

引用块左侧间距调整（2026-10-12）：公共 `quoteblock` 左内边距由 2 mm 改为 `\dimexpr\ccwd+2pt\relax`，使竖线内侧至正文约为一个中文字宽，并随字号变化；其余三侧仍为 2 mm。引用块与分隔线独立样张各两轮通过，全部 3 页已渲染检查；五份纵向样张各两轮收敛，日志无缺字、Overfull 或字体替换，已检查综合样张第 3、5、6 页。完整竖版通过 `./run.sh portrait` 三轮收敛，仍为 151 页，末轮无缺字，保留原有 4 条 Overfull 与 amsmath 警告；已渲染检查完整 PDF 第 105 页的实际引用块，未逐页验收完整 PDF。

引用块间距基准更正（2026-10-12）：按用户确认，以竖线外侧为基准，将左内边距改为 `left=\ccwd`，一个中文字宽包含竖线自身厚度。引用块、分隔线独立样张各两轮通过，全部 3 页已渲染检查；五份纵向样张各两轮收敛，日志无缺字、Overfull 或字体替换，已检查综合样张第 3、5、6 页。完整竖版三轮收敛，仍为 151 页，末轮无缺字，原有 4 条 Overfull 与 amsmath 警告不变；已检查第 105 页实际引用块，未逐页验收全文。


InputCode 卡片改版（2026-10-12）：五份独立接口样张各两轮编译通过，无缺字、Overfull 或字体替换；代码样张 1 页和跨页样张 2 页已全部渲染检查，图标、行号、标题、续页与圆角无裁切遮挡。其余独立样张本轮未重新逐页视觉验收。样式参数与完整竖版验证范围见 `../../README.md`。


## InputCode 多余上下间距修复（2026-10-13）

公共 `mystyle.tex` 在 `InputCode` 内的 `inputminted` 调用中设置 `vspace=0pt`，并通过 `listparameters` 将 `topsep`、`partopsep` 清零，消除 FancyVerb 额外的列表间距。卡片的上下 2 mm 内边距及卡片外间距不变；独立 minted 环境、原始代码中的空行不受影响。

`preamble/tests/mystyle/input-code.tex` 新增实际列表间距断言：修改前以 `10pt plus 3pt minus 5pt` 失败，修改后通过。五份公共接口样张各两轮通过，七份纵向样张各两轮收敛，日志无缺字、Overfull 或字体替换；配色 PDF 检查仍通过。已渲染检查纵向代码卡片 2 页、独立代码样张 1 页及独立跨页样张 2 页，其余样张仅编译回归。

完整竖版通过 `./run.sh portrait` 三轮收敛，由本次修复前的 153 页变为 151 页；末轮无缺字或字体替换，仍有原有 4 条 Overfull 与 2 条 amsmath 警告。已渲染检查第 20、21 页实际 KMP 跨页，未逐页验收全文。未修改正文、未提交或推送。
