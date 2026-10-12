# LaTeX 导言区配置

本目录集中管理宏包、版式与自定义接口。主文件在 `\documentclass` 之后直接加载所需文件，不增加 `setup.tex` 或 `layout-common.tex`。

| 文件或目录 | 职责与当前状态 |
| --- | --- |
| `packages.tex` | 已加载中文、数学、图片、颜色、删除线、布局、minted、tcolorbox 与超链接支持。 |
| `layout-portrait.tex` | 已设置 A4 纵向及关闭标题自动编号；边距、页眉页脚与最终字体尚未实现。 |
| `layout-landscape.tex` | 横版独立布局，目前为空占位文件。 |
| `layout-code.tex` | 仅代码版独立布局，目前为空占位文件；纸张方向、栏数等尚未确定。 |
| `mystyle.tex` | 已实现 `\Highlight`、`\InputCode`、`quoteblock` 与 `\Separator`。 |
| `tests/` | 按 mystyle、portrait、landscape、code 分类检验；当前已建立 `mystyle/` 与共用资源 `fixtures/`，三版布局检验待实现。 |

入口仅保留文档类声明、下列三个导言区引用和标题／作者／日期等元信息；纸张、字体、字号、间距及编号等排版设置集中放在导言区文件中。ctex 加载前所需的临时字体选项由 `packages.tex` 管理。

三个入口共用 `packages.tex` 和 `mystyle.tex`，中间加载本版的 `layout-<版本>.tex`；所有字体、纸张、间距等设置在各版布局文件中独立维护，不设置公共布局文件。横版与仅代码版入口目前同样为空占位文件。

`main-portrait.tex` 当前采用的加载顺序：

```latex
\input{preamble/packages.tex}
\input{preamble/layout-portrait.tex}
\input{preamble/mystyle.tex}
```

`\Highlight` 已按用户确认实现为 `#FFFF00` 背景、零内边距的不可拆分行内短语框。`\InputCode` 已实现浅灰标题栏、细黑边框、直角与跨页排版；代码区外观可通过各语言的 `\setminted[语言]{...}` 设置，续页不重复标题。`quoteblock` 已实现浅灰背景、左侧深灰竖线和跨页排版；标准 `quote` 不变，当前不要求嵌套。`\Separator{}` 已实现为适应所在容器宽度的浅灰细线，线上下有间距，不强制换页。接口要求见根目录及 `contents/` 下的 `AGENTS.md`；每个接口均配有效果检验。

所有路径相对于项目根目录，不能假定加载本目录文件会改变工作目录。建议 XeLaTeX；minted 依赖 `latexminted`。宏包已加载不等于自定义接口或整本文档已经可编译。

完整版计划共用 `contents/chapters.tex`，代码版计划使用 `contents/code-index.tex`；内容清单不放在导言区。两个清单尚未创建，竖版仍直接引入 19 篇章节。

从任意工作目录调用根目录脚本均会切换到项目根目录：

```sh
./run.sh             # 默认 portrait
./run.sh portrait
./run.sh landscape
./run.sh code
./run.sh all
./run.sh --help
```

产物分别为 `build/portrait/main-portrait.pdf`、`build/landscape/main-landscape.pdf`、`build/code/main-code.pdf`，辅助文件与 minted 缓存也按版本隔离。空入口提前报错；`all` 先检查三个入口，再按上述顺序构建，遇到失败停止。目前横版、代码版尚不可构建，脚本支持目标不代表该版内容已实现。

根目录 `run.sh` 至少编译两轮，并检查主文档目录、交叉引用和书签辅助记录是否稳定及是否仍有重编译提示，最多八轮。仅稳定且生成非空 PDF 后清理本版已知辅助文件与 minted 缓存，不清理其他版本或测试目录；编译失败或达到上限仍未稳定时，返回失败并保留日志。

构建脚本验证（2026-10-12）：Bash 语法检查通过；临时环境验证了默认目标、全部目标、从其他目录调用、非法参数、空入口预检、至少两轮收敛、八轮上限、失败保留和跨版本清理隔离；三个最小入口均通过真实 XeLaTeX + minted 编译，成功后各目录只保留对应 PDF。这些检查不代表完整笔记或尚未实现的横版、代码版已通过内容与视觉验收。
