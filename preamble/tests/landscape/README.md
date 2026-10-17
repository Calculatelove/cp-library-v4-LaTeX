# 横版布局检验

本目录检验 `preamble/layout-landscape.tex` 及其与共用实现、自定义接口的组合，不引用章节。版式为 A4 横向双栏，四边 12 mm（含页眉页脚），栏距 8 mm，栏宽 132.5 mm。

## 样张与检查

| 文件 | 检验内容 |
| --- | --- |
| `titlepage.tex` | 4 页：横向配图与含 TeX 特殊字符的提交说明（clean）；纵向配图与超长提交说明（dirty）；无配图且提交信息文件不存在；扉页后的双栏正文页。资源取自 `../fixtures/` |
| `flow.tex` | 同栏连续章节、左右栏跨章、连续空标题、栏底标题跟随正文或公式；页眉显示页顶所在的章（左栏顶端恰为新章时取该章，否则取页首延续的章）；含栏宽断言 |
| `preview.tex` | 中西文、粗体与斜体、数学算子与未分组的直立上下标、Unicode 符号、五级标题、嵌套列表、多语言代码、Maple 行内代码及各接口 |
| `code-cards.tex` | 单个 100 行的人工代码卡片从左栏底跨到右栏与下一页，标题不重复；长文件名、显示折行与内嵌 minted |
| `syntax-colors.tex` | 四色高亮、C++ 类型与注释的常规直立字体 |
| `interfaces.tex` | 65 段人工引用跨栏跨页；嵌套列表、公式、分隔线、高亮的范围 |
| `toc-layout.tex` | 两页真实目录、三级长标题、父子条目保护、通栏居中的目录标题、88 个条目与 90 个五层书签 |
| `images.tex` | 图片按局部栏宽解释 `\textwidth`：106 mm 的图与整栏图，分组结束后整页宽度不变 |
| `check-layout.py` | 从 PDF 检查纸张、阅读流向、章名、代码完整性、引用段落顺序、配色与字重、目录分栏、链接目标与书签；加参数 `code` 检查代码版样张 |
| `check-titlepage.py` | 书名区的位置与居中、110 × 70 mm 配图区域、眉题式提交信息、未提交修改标签、原样输出、换行与底边、页眉页码及 PDF 文档属性；加参数 `code` 检查代码版，另查书名后悬挂的“（代码版）” |

`flow`、`code-cards`、`toc-layout` 的正文在 `../fixtures/twocolumn-*-body.tex`，与代码版共用；`syntax-colors` 的正文在 `../fixtures/syntax-colors-body.tex`，与竖版、代码版共用。本目录的这四份样张只保留载入横版布局的包装。人工长代码在 `../fixtures/landscape-long.cpp`。

## 运行

```sh
bash preamble/tests/landscape/run.sh
bash preamble/tests/landscape/run.sh flow toc-layout
python3 preamble/tests/landscape/check-layout.py
python3 preamble/tests/landscape/check-titlepage.py
pdftoppm -scale-to 1600 -png preamble/tests/build/landscape/toc-layout.pdf preamble/tests/build/landscape/toc-layout
```

编译方式、产物位置与 PDF 检查的共同约定见 `../README.md`；本组另需 TeX Live 的 mwe 示例图片。

样张中特意构造的大块留白用于触发边界，不代表正文的版式效果。本目录不代替整书与实物打印验收；整书的越栏检查见 `scripts/README.md`。
