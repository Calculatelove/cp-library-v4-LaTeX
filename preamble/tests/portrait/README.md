# 竖版布局检验

本目录检验 `preamble/layout-portrait.tex` 及其与共用实现、自定义接口的组合。全部为独立样例，不引用章节。

## 样张

| 源码 | 检验内容 | PDF（在 `../build/portrait/`） |
| --- | --- | --- |
| `titlepage.tex` | 扉页：横、竖两种配图与无配图；提交说明含全部 TeX 特殊字符、超长换行、dirty 标签，以及提交信息文件不存在；扉页后的正文页码。用 `\TitlePageReadCommit{<文件>}` 改读 `../fixtures/` 中的提交信息，不依赖本仓库的 Git 状态 | `titlepage.pdf` |
| `toc-layout.tex` | 单栏三级目录、各级长标题续行与页码对齐；页底空间不足时，三级标题组整体移到下一页（第 2 页特意留白以构造边界） | `toc-layout.pdf` |
| `code-cards.tex` | 语言图标与通用图标、长标题换行、短代码与跨页卡片 | `code-cards.pdf` |
| `symbols.tex` | ⭐、🚩 在标题、目录、页眉、正文、引用块中的字号与字重，文字提取与书签；断言正文与 22 pt 粗体标题中两个符号的宽度 | `symbols.pdf` |
| `preview.tex` | 综合样张：扉页、目录、正文、标题层级、页眉页码、脚注、嵌套列表、高亮、代码与引用跨页，以及 Maple 行内代码（中文、易混淆字符、运算符与转义符号） | `preview.pdf` |
| `section-breaks.tex` | 一级标题前分页：以页码断言检查空小标题、空一级标题、普通正文、目录、显式分页与星号标题；应为 7 页，目录后 A—F 各占一页 | `section-breaks.pdf` |
| `heading-levels.tex` | 四、五级标题与三级标题、正文、公式、引用块、高亮、列表的衔接，以及长标题换行；第 2—5 页把正文推到页底，断言剩余空间介于标题本身与标题加首行之间，否则编译报错 | `heading-levels.pdf` |
| `math-latin-modern.tex`、`math-stix.tex` | 默认数学字体 Latin Modern Math 与 STIX Two Math 的对照，正文相同（`math-content.tex`，不能单独编译）：行内公式、黑板粗体、花体、粗体希腊字母、求和、积分、分式、矩阵与引用块；`\boldsymbol` 作用于含分式、定界符与 min 算子的表达式；递推式中的 log 与粗体 log；普通、上下标与粗体的 `\mathrm{base}`，以及 `\text{base}` | `math-latin-modern.pdf`、`math-stix.pdf` |
| `syntax-colors.tex` | 四色配色与常规直立字形；正文在 `../fixtures/syntax-colors-body.tex`，与横版、代码版共用 | `syntax-colors.pdf` |

## PDF 检查

| 脚本 | 断言 |
| --- | --- |
| `check-titlepage.py` | PDF 标题与作者取自入口元信息；书名、英文书名、作者的字体、字号与基线位置，水平居中，各页一致；配图在 130 × 110 mm 区域内等比缩放，不与文字重叠；提交信息为眉题式三行：眉题“LAST COMMIT”，日期与哈希（Maple Mono，哈希为 `506B82`），提交说明与资源逐字一致（`--` 不被替换为连接号）；各行不含“·”；dirty 时第二行末尾有带唯一细框的标签；相邻汉字的步进等于字号（TikZ 的 `align=center` 会拉开字距）；超长说明居中换行、向上增长，不进入下边距；提交信息缺失时只显示标题区；扉页无页码，其后正文照常编号 |
| `check-headings.py` | 四、五级标题为苹方 Semibold 10.5 pt，独立成行，与其后第一行同页；四级标题上下的基线距为 24/20 pt（容差 1 pt），三级更大，三级紧接四级时介于正文行距与 24 pt 之间；页底的标题移到下一页页首；书签层级为 4、5 |
| `check-syntax-colors.py` | `syntax-colors.pdf` 与 `code-cards.pdf` 中的代码只用四种颜色，没有粗体或斜体；跨页卡片的续页颜色不变 |

## 运行

```sh
bash preamble/tests/portrait/run.sh
bash preamble/tests/portrait/run.sh titlepage symbols
python3 preamble/tests/portrait/check-titlepage.py
python3 preamble/tests/portrait/check-headings.py
python3 preamble/tests/portrait/check-syntax-colors.py
```

编译方式、产物位置与 PDF 检查的共同约定见 `../README.md`。字体需要 Songti SC、PingFang SC 与 Maple Mono NF CN（常规、粗体、斜体、粗斜体）；Latin Modern Roman、Latin Modern Math 与 STIX Two Math 使用 TeX Live 提供的字体文件。

## 人工检查要点

- 代码中的运算符与 `fi`、`fl`、`ffi`、`ffl` 没有连字；中文注释与 ASCII 对齐；代码标题栏没有用 Maple。
- 跨页的代码卡片与引用块不侵入页眉页脚。
- 目录页码与标题的起页一致；书签包含全部标题层级，并默认展开。
- 日志中 xeCJK 的字体族重定义提示是预期的；不应出现缺字或字体替换。

可以用 Poppler 渲染页面、查看嵌入的字体：

```sh
mkdir -p preamble/tests/build/portrait/render
pdftoppm -scale-to 1600 -png preamble/tests/build/portrait/preview.pdf preamble/tests/build/portrait/render/preview
pdffonts preamble/tests/build/portrait/preview.pdf
```
