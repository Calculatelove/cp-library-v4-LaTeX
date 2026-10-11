# 自定义接口效果检验

本目录用于 `preamble/mystyle.tex` 各接口的效果检验。当前已有 `highlight.tex`、`input-code.tex`、`input-code-pages.tex`、`quoteblock.tex` 和 `separator.tex`，覆盖四个自定义接口。

历史实现曾有高亮、代码插入、引用块、分隔线四类检验，但旧源码及产物当前不在工作区，不能引用旧结果作为新实现的验证证据。

每个接口至少提供一个可独立编译的 `.tex` 检验文件：

| 接口 | 需要展示的效果 |
| --- | --- |
| `\Highlight` | 中文短语、粗体、行内公式；无额外内边距，且颜色不影响后文。 |
| `\InputCode` | 默认文件名、显式标题、中文与带空格路径、多语言高亮、长代码跨页。 |
| `quoteblock` | 多段正文、列表、公式、跨页；标准 `quote` 保持不变。当前不要求嵌套。 |
| `\Separator{}` | 普通正文、列表及引用块中的宽度和间距，不强制分页。 |

统一从项目根目录编译，资源路径也从项目根目录解析。可以共享测试导言区，但每个接口须有明确可查看的示例。

`highlight.tex` 需要 XeLaTeX、项目 `packages.tex` 中列出的宏包，以及 TeX Live 的 Fandol 字体。从项目根目录运行：

```sh
mkdir -p preamble/tests/build
xelatex -interaction=nonstopmode -halt-on-error -output-directory=preamble/tests/build preamble/tests/highlight.tex
```

源码为 `preamble/tests/highlight.tex`，PDF 与日志位于 `preamble/tests/build/`。此检验包含中文、粗体、行内公式，以及高亮前后的正文；编译时还比较高亮内容与原内容的宽度、高度和深度，确认没有额外内边距。测试字体不决定项目最终字体。

`\InputCode` 的两个检验还需要 `minted`、可执行的 `latexminted` 和 TeX Live Fandol 字体。从项目根目录运行，每个文件编译两次；本机 `minted` 首轮可能只输出 `<MINTED>` 占位内容，第二轮才载入生成的代码高亮文件：

```sh
xelatex -interaction=nonstopmode -halt-on-error -output-directory=preamble/tests/build preamble/tests/input-code.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=preamble/tests/build preamble/tests/input-code.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=preamble/tests/build preamble/tests/input-code-pages.tex
xelatex -interaction=nonstopmode -halt-on-error -output-directory=preamble/tests/build preamble/tests/input-code-pages.tex
```

源码为 `preamble/tests/input-code.tex`、`preamble/tests/input-code-pages.tex`，代码资源为同目录中的 `示例 文件_1.cpp`、`sample.py`、`sample.sh`、`Makefile test` 和 `long-code.cpp`。前者检验默认与显式文件名、中文和带空格路径、C++ / Python / Bash / Makefile，以及各语言的 `\setminted` 设置；后者检验长代码跨页及续页不重复标题。PDF、日志及 minted 缓存都位于 `preamble/tests/build/`。测试从项目根目录编译，不需要开放不受限的 shell escape。

`quoteblock.tex` 需要 XeLaTeX、项目宏包及 TeX Live Fandol 字体。从项目根目录运行：

```sh
xelatex -interaction=nonstopmode -halt-on-error -output-directory=preamble/tests/build preamble/tests/quoteblock.tex
```

源码为 `preamble/tests/quoteblock.tex`，PDF 与日志位于 `preamble/tests/build/`。检验包含多段中文正文、列表、展示公式、标准 `quote` 和跨页引用块；应检查每页的浅灰背景及左侧竖线。引用块嵌套当前不在要求内。

`separator.tex` 需要 XeLaTeX、项目宏包及 TeX Live Fandol 字体。从项目根目录运行：

```sh
xelatex -interaction=nonstopmode -halt-on-error -output-directory=preamble/tests/build preamble/tests/separator.tex
```

源码为 `preamble/tests/separator.tex`，PDF 与日志位于 `preamble/tests/build/`。检验普通正文、列表和 `quoteblock` 中的横线宽度及上下间距，产物应为单页。测试字体不决定项目最终字体。

生成的 PDF、日志和缓存集中放在本目录的 `build/`，该目录已加入忽略规则；测试源码与资源保留。编译成功后仍需检查实际 PDF，不能只检查进程退出码。
