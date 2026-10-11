# LaTeX 导言区配置

本目录集中管理宏包、版式与自定义接口。主文件在 `\documentclass` 之后直接加载所需文件，不增加 `setup.tex`。

| 文件或目录 | 职责与当前状态 |
| --- | --- |
| `packages.tex` | 已加载中文、数学、图片、颜色、删除线、布局、minted、tcolorbox 与超链接支持。 |
| `layout-portrait.tex` | 已设置 A4 纵向及关闭标题自动编号；边距、页眉页脚与最终字体尚未实现。 |
| `mystyle.tex` | 已实现 `\Highlight`、`\InputCode`、`quoteblock` 与 `\Separator`。 |
| `tests/` | 四个自定义接口的独立效果检验。 |

入口仅保留文档类声明、下列三个导言区引用和标题／作者／日期等元信息；纸张、字体、字号、间距及编号等排版设置集中放在导言区文件中。ctex 加载前所需的临时字体选项由 `packages.tex` 管理。

`main-portrait.tex` 当前采用的加载顺序：

```latex
\input{preamble/packages.tex}
\input{preamble/layout-portrait.tex}
\input{preamble/mystyle.tex}
```

`\Highlight` 已按用户确认实现为 `#FFFF00` 背景、零内边距的不可拆分行内短语框。`\InputCode` 已实现浅灰标题栏、细黑边框、直角与跨页排版；代码区外观可通过各语言的 `\setminted[语言]{...}` 设置，续页不重复标题。`quoteblock` 已实现浅灰背景、左侧深灰竖线和跨页排版；标准 `quote` 不变，当前不要求嵌套。`\Separator{}` 已实现为适应所在容器宽度的浅灰细线，线上下有间距，不强制换页。接口要求见根目录及 `contents/` 下的 `AGENTS.md`；每个接口均配有效果检验。

所有路径相对于项目根目录，不能假定加载本目录文件会改变工作目录。建议 XeLaTeX；minted 依赖 `latexminted`。宏包已加载不等于自定义接口或整本文档已经可编译。

根目录 `run.sh` 至少编译两轮，并检查主文档目录、交叉引用和书签辅助记录是否稳定及是否仍有重编译提示，最多八轮。仅稳定后清理辅助文件与 minted 缓存；编译失败或达到上限仍未稳定时，返回失败并保留日志。
