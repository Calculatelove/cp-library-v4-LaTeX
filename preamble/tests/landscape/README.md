# 横版布局检验

本目录检验 `preamble/layout-landscape.tex` 及其与共用实现、自定义接口的组合，不引用章节；版式见 `../../README.md` 的“三个版本”。PDF 在 `../build/landscape/`。

## 样张

| 样张 | 检验内容 |
| --- | --- |
| `quotes.tex` | 中文双引号随字体族切换：正文、粗斜体、嵌套恢复、三级目录、页眉、行内代码、minted、卡片标题与代码、其他标点、窄行禁则及 Unicode 书签；与双反引号写法比较字形与相对位置 |
| `titlepage.tex` | 扉页的书名区、配图区域、仓库地址行、眉题式提交信息、哈希链接、底部信息区间距、页眉页码与 PDF 文档属性。各页依次为：横向配图，含 `~`、`_`、`%` 的仓库地址与含 TeX 特殊字符的提交说明（clean）；纵向配图与超长提交说明（dirty），清空仓库地址；无配图且提交信息文件不存在，只有地址行；扉页后的双栏正文页。资源取自 `../fixtures/` |
| `flow.tex` | 纸张与栏宽，同栏连续章节、左右栏跨章、连续空标题、栏底标题跟随正文或公式，以及页眉取页顶所在的章 |
| `preview.tex` | 中西文、粗体与斜体、数学算子与未分组的直立上下标、Unicode 符号、五级标题、嵌套列表、多语言代码、Maple 行内代码及各接口 |
| `code-cards.tex` | 单个人工长代码卡片从左栏底跨到右栏与下一页，代码完整、按序，标题不重复；长文件名、显示折行与内嵌 minted；代码配色；框外行号跨栏跨页连续，覆盖三位数、空行编号和新卡片重置 |
| `syntax-colors.tex` | 代码配色，C++ 类型与注释的常规直立字体 |
| `interfaces.tex` | 多段人工引用跨栏跨页，段落完整、按序；引用中的嵌套列表及其符号，公式、分隔线、高亮的范围 |
| `block-spacing.tex` | 代码卡片与引用块前后、二级列表、分隔线的竖向间距 |
| `toc-layout.tex` | 跨页的真实目录、三级长标题、父子条目保护、通栏居中的目录标题、条目链接与各级书签 |
| `images.tex` | 图片按局部栏宽解释 `\textwidth`：按栏宽比例设宽的图与整栏图，分组结束后整页宽度不变 |

`quotes`、`syntax-colors`、`block-spacing` 的正文与竖版共用，`flow`、`code-cards`、`toc-layout` 的正文也放在 `../fixtures/`，见其 README；本目录的这六份只是载入横版布局的包装。人工长代码在 `../fixtures/landscape-long.cpp`。

## 检查

`check.py` 检查扉页分支与链接、章节连续排版及页眉、标题跟随正文、代码与引用跨栏跨页的完整性、行号、引号作用域、目录内容与导航。加 `code` 只查代码版扉页。图片按局部栏宽解释及分组恢复由 `images` 的编译期断言检查，比较实际长度，不写死毫米数。

默认运行不含 `preview`、`syntax-colors` 与 `block-spacing`，需查看整体效果、配色或间距时按样张名编译。综合预览用于按需目视验收，不承担默认回归；自动检查不锁定精确视觉参数。共同流程见 `../README.md`。

## 运行

```sh
bash preamble/tests/landscape/run.sh
bash preamble/tests/landscape/run.sh flow toc-layout
python3 preamble/tests/landscape/check.py
pdftoppm -scale-to 1600 -png preamble/tests/build/landscape/toc-layout.pdf preamble/tests/build/landscape/toc-layout
```

编译方式、产物位置与 PDF 检查的共同约定见 `../README.md`；本组另需 TeX Live 的 mwe 示例图片。

样张中特意构造的大块留白用于触发边界，不代表正文的版式效果。本目录不代替整书与实物打印验收；整书按 `../../AGENTS.md` 的分级范围构建并抽查。
