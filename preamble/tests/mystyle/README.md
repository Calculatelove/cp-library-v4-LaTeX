# 自定义接口效果检验

本目录为 `preamble/mystyle.tex` 的四个自定义接口提供独立样张，不加载各版布局，也不引用章节。接口的外观规格见 `../../README.md`。

## 样张

| 样张 | 检验内容 |
| --- | --- |
| `highlight.tex` | 中文短语、粗体、行内公式，以及高亮前后的正文。编译时比较高亮内容与原内容的宽度、高度和深度，确认没有额外内边距；颜色不影响后文 |
| `input-code.tex` | 默认与显式文件名、中文和带空格的路径、C++ / Python / Bash / Makefile 高亮、各语言的 `\setminted` 设置；编译时断言卡片内部没有额外的列表间距 |
| `input-code-pages.tex` | 长代码跨页，续页不重复标题 |
| `quoteblock.tex` | 多段正文、列表、行间公式、标准 `quote` 与跨页引用块；编译时断言引用块内与块后的段间距没有被重置；跨页时每页都应有浅灰背景与左侧竖线。不检验嵌套 |
| `separator.tex` | 普通正文、列表与 `quoteblock` 中横线的宽度与上下间距；不分页 |

代码卡片与引用块的前后距由各版布局设定（`book-box-spacing`，见 `../../shared/README.md`）；本目录不载入布局，沿用 tcolorbox 的默认前后距，前后距在各版的 `block-spacing` 样张中检验。

代码资源在 `../fixtures/`：`示例 文件_1.cpp`、`sample.py`、`sample.sh`、`Makefile test` 与 `long-code.cpp`。

## 运行

```sh
bash preamble/tests/mystyle/run.sh
bash preamble/tests/mystyle/run.sh input-code input-code-pages
```

编译方式与产物位置见 `../README.md`。依赖 XeLaTeX、`packages.tex` 中的宏包与 TeX Live 的 Fandol 字体；`mystyle.tex` 用 Maple Mono NF CN 提供代码标题的 Nerd Font 图标，所以也需要这款字体。两份代码样张还需要可执行的 `latexminted`：minted 首轮可能只输出 `<MINTED>` 占位，第二轮才载入高亮结果。

这里用 Fandol 只为检验接口，不代表各版的字体。编译通过后仍要查看 PDF，不能只看退出码。新增接口的样张放在本目录，版式样张放在对应版本的目录。
