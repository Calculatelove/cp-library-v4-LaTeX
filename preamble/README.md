# LaTeX 导言区配置

本目录集中管理宏包、版式与自定义接口。主文件在 `\documentclass` 之后直接加载所需文件，不增加 `setup.tex`。

| 文件或目录 | 职责与当前状态 |
| --- | --- |
| `packages.tex` | 已加载中文、数学、图片、颜色、删除线、布局、minted、tcolorbox 与超链接支持。 |
| `layout-wide.tex` | 横向版本布局；目前为空。 |
| `mystyle.tex` | 已实现 `\Highlight`、`\InputCode`、`quoteblock` 与 `\Separator`。 |
| `tests/` | 四个自定义接口的独立效果检验。 |

计划加载顺序：

```latex
\input{preamble/packages.tex}
\input{preamble/layout-wide.tex}
\input{preamble/mystyle.tex}
```

`\Highlight` 已按用户确认实现为 `#FFFF00` 背景、零内边距的不可拆分行内短语框。`\InputCode` 已实现浅灰标题栏、细黑边框、直角与跨页排版；代码区外观可通过各语言的 `\setminted[语言]{...}` 设置，续页不重复标题。`quoteblock` 已实现浅灰背景、左侧深灰竖线和跨页排版；标准 `quote` 不变，当前不要求嵌套。`\Separator{}` 已实现为适应所在容器宽度的浅灰细线，线上下有间距，不强制换页。接口要求见根目录及 `contents/` 下的 `AGENTS.md`；每个接口均配有效果检验。

所有路径相对于项目根目录，不能假定加载本目录文件会改变工作目录。建议 XeLaTeX；minted 依赖 `latexminted`。宏包已加载不等于自定义接口或整本文档已经可编译。
