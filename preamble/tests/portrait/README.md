# 竖版布局检验

本目录检验 `preamble/layout-portrait.tex` 及其与共用实现、自定义接口的组合。全部为独立样例，不引用章节。

## 样张

| 源码 | 检验内容 | PDF（在 `../build/portrait/`） |
| --- | --- | --- |
| `quotes.tex` | 中文双引号随字体族切换：正文、粗斜体、嵌套恢复、三级目录、页眉、行内代码、minted、卡片标题与代码、其他标点、窄行禁则及 Unicode 书签；与双反引号写法比较字形与相对位置；正文在 `../fixtures/quotes-body.tex`，PDF 断言复用 `../pdfcheck.py` 的 `check_quotes` | `quotes.pdf` |
| `titlepage.tex` | 扉页：横、竖两种配图与无配图；提交说明含全部 TeX 特殊字符、超长换行、dirty 标签，以及提交信息文件不存在；仓库地址含 `~`、`_`、`%`，第 1 页有地址行与提交信息，第 2 页清空地址，第 3 页只有地址行；扉页后的正文页码。用 `\TitlePageReadCommit{<文件>}` 改读 `../fixtures/` 中的提交信息，不依赖本仓库的 Git 状态 | `titlepage.pdf` |
| `toc-layout.tex` | 单栏三级目录、各级长标题续行与页码对齐；页底空间不足时，三级标题组整体移到下一页（第 2 页特意留白以构造边界） | `toc-layout.pdf` |
| `code-cards.tex` | 语言图标与通用图标、长标题换行、短代码与跨页卡片、框外行号、折行与空行编号 | `code-cards.pdf` |
| `symbols.tex` | ⭐、🚩 在标题、目录、页眉、正文、引用块中的字号与字重，文字提取与书签；断言正文与 22 pt 粗体标题中两个符号的宽度 | `symbols.pdf` |
| `preview.tex` | 综合样张：扉页、目录、正文、标题层级、页眉页码、脚注、嵌套的无序与有序列表、高亮、代码与引用跨页，以及 Maple 行内代码（中文、易混淆字符、运算符与转义符号） | `preview.pdf` |
| `section-breaks.tex` | 一级标题前分页：以页码断言检查空小标题、空一级标题、普通正文、目录、显式分页与星号标题；应为 7 页，目录后 A—F 各占一页 | `section-breaks.pdf` |
| `heading-levels.tex` | 四、五级标题与三级标题、正文、公式、引用块、高亮、列表的衔接，以及长标题换行；第 2—5 页把正文推到页底，断言剩余空间介于标题本身与标题加首行之间，否则编译报错 | `heading-levels.pdf` |
| `math-latin-modern.tex`、`math-stix.tex` | 默认数学字体 Latin Modern Math 与 STIX Two Math 的对照，正文相同（`math-content.tex`，不能单独编译）：行内公式、黑板粗体、花体、粗体希腊字母、求和、积分、分式、矩阵与引用块；`\boldsymbol` 作用于含分式、定界符与 min 算子的表达式；递推式中的 log 与粗体 log；普通、上下标与粗体的 `\mathrm{base}`，以及 `\text{base}` | `math-latin-modern.pdf`、`math-stix.pdf` |
| `syntax-colors.tex` | 四色配色与常规直立字形；正文在 `../fixtures/syntax-colors-body.tex`，与横版、代码版共用 | `syntax-colors.pdf` |
| `block-spacing.tex` | 代码卡片与引用块前后、二级列表、分隔线的竖向间距；正文在 `../fixtures/block-spacing-body.tex`，与横版、代码版共用 | `block-spacing.pdf` |

## PDF 检查

`check.py` 按样张分小节检查，小节名以样张名开头：

| 样张 | 断言 |
| --- | --- |
| `titlepage` | PDF 标题与作者取自入口元信息；纸张为 A4 纵向；书名、英文书名、作者的字体、字号与基线位置，以页面中轴居中，各页一致，书名行没有版本标记；配图在 80 × 80 mm 区域内等比缩放，不与文字重叠，区域本身也不与标题区、底部信息区相交；设了仓库地址时底部信息区首行为 GitHub 标志加去掉 `https://` 的地址（8 pt Maple Mono、次要灰，地址在标志起点后 1.45 em，整体居中），整行链接到仓库、无边框；提交信息为眉题式三行：眉题“LAST COMMIT”，日期与哈希（8 pt Maple Mono，日期为次要灰，哈希为 `506B82`），提交说明与资源逐字一致（`--` 不被替换为连接号）；各行不含“·”；dirty 时第二行末尾有带唯一细框的标签；基线间距为地址行到眉题 16.5 pt、眉题到日期与日期到说明各 11 pt，dirty 时为 12 与 13 pt；设了仓库地址时哈希链接到“<仓库地址>/commit/<短哈希>”，无边框，区域与哈希字框一致，清空地址的页没有链接，只有地址行的页只有仓库链接；相邻汉字的步进等于字号（TikZ 的 `align=center` 会拉开字距）；超长说明居中换行、向上增长，不进入下边距；提交信息缺失时标题区之外只有地址行，同样贴近底边；扉页无页眉页码，其后正文照常编号。第 4 页以一级标题开头，按 plain 样式不显示页眉，所以不查它的页眉。断言由 `../pdfcheck.py` 的 `check_titlepage` 与横版、代码版共用 |
| `syntax-colors`、`code-cards` | 代码只用四种颜色，没有粗体或斜体；跨页卡片的续页颜色不变；`code-cards` 的行号单独检查字体、4 pt 字号、灰色、框外 1 mm 位置及折行、空行编号 |
| `block-spacing` | 正文、卡片、引用块之间的盒前距为 9.5 pt，盒后下一行基线距盒底为段距加行距；盒后的标题与正文后的标题基线距相同；二级列表父项到首个子项为行距加 1 pt，同级条目为行距加 2 pt；分隔线顶边距上一行基线为段距加行距减线宽，下一行基线距线底为 0.4 倍行距加段距与行距。断言由 `../pdfcheck.py` 的 `check_block_spacing` 与横版、代码版共用 |
| `heading-levels` | 四、五级标题为苹方 Semibold 10.5 pt，独立成行，与其后第一行同页；四级标题上下的基线距为 24/20 pt（容差 1 pt），三级更大，三级紧接四级时介于正文行距与 24 pt 之间；页底的标题移到下一页页首；书签层级为 4、5 |

## 运行

```sh
bash preamble/tests/portrait/run.sh
bash preamble/tests/portrait/run.sh titlepage symbols
python3 preamble/tests/portrait/check.py
```

编译方式、产物位置与 PDF 检查的共同约定见 `../README.md`。字体需要 Songti SC、PingFang SC 与 Maple Mono NF CN（常规、粗体、斜体、粗斜体）；Latin Modern Roman、Latin Modern Math 与 STIX Two Math 使用 TeX Live 提供的字体文件。

## 人工检查要点

- 代码中的运算符与 `fi`、`fl`、`ffi`、`ffl` 没有连字；中文注释与 ASCII 对齐；代码标题栏没有用 Maple。
- 跨页的代码卡片与引用块不侵入页眉页脚。
- 目录页码与标题的起页一致；书签包含全部标题层级，初始只显示一级。
- 日志中 xeCJK 的字体族重定义提示是预期的；不应出现缺字或字体替换。

可以用 Poppler 渲染页面、查看嵌入的字体：

```sh
mkdir -p preamble/tests/build/portrait/render
pdftoppm -scale-to 1600 -png preamble/tests/build/portrait/preview.pdf preamble/tests/build/portrait/render/preview
pdffonts preamble/tests/build/portrait/preview.pdf
```
