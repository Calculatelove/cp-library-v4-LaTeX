# 竖版布局检验

本目录检验 `preamble/layout-portrait.tex` 及其与共用实现、自定义接口的组合。全部为独立样例，不引用章节；PDF 在 `../build/portrait/`。

## 样张

| 样张 | 检验内容 |
| --- | --- |
| `quotes.tex` | 中文双引号随字体族切换：正文、粗斜体、嵌套恢复、三级目录、页眉、行内代码、minted、卡片标题与代码、其他标点、窄行禁则及 Unicode 书签；与双反引号写法比较字形与相对位置 |
| `titlepage.tex` | 扉页的书名区、配图区域、仓库地址行、眉题式提交信息、哈希链接、底部信息区间距、页眉页码与 PDF 文档属性。各页依次为：横向配图，含 `~`、`_`、`%` 的仓库地址与含全部 TeX 特殊字符的提交说明（clean）；纵向配图与超长提交说明（dirty），清空仓库地址；无配图且提交信息文件不存在，只有地址行；扉页后的正文页。用 `\TitlePageReadCommit{<文件>}` 改读 `../fixtures/` 中的提交信息，不依赖本仓库的 Git 状态 |
| `toc-layout.tex` | 单栏三级目录、各级长标题续行与页码对齐；页底空间不足时，三级标题组整体移到下一页（特意留白以构造边界） |
| `code-cards.tex` | 语言图标与通用图标、长标题换行、短代码与跨页卡片、代码配色、框外行号、折行与空行编号 |
| `symbols.tex` | ⭐、🚩 在标题、目录、页眉、正文、引用块中的字号与字重，文字提取与书签，以及汉字与符号之间的间距 |
| `preview.tex` | 综合样张：扉页、目录、正文宽度、标题层级、页眉页码、脚注、嵌套的无序与有序列表、高亮、代码与引用跨页，以及 Maple 行内代码（中文、易混淆字符、运算符与转义符号） |
| `section-breaks.tex` | 一级标题前的分页：目录、空小标题、空一级标题、普通正文、显式分页与星号标题之后各章的起页，不多出空白页 |
| `heading-levels.tex` | 四、五级标题的独立成行与后文同页；字体和上下间距供目视查看；与三级标题、正文、公式、引用块、高亮、列表的衔接；长标题换行；页底空间不足时的分页；书签层级 |
| `math-latin-modern.tex`、`math-stix.tex` | 默认数学字体 Latin Modern Math 与 STIX Two Math 的对照，正文相同（`math-content.tex`，不能单独编译）：行内公式、黑板粗体、花体、粗体希腊字母、求和、积分、分式、矩阵与引用块；`\boldsymbol` 作用于含分式、定界符与 min 算子的表达式；递推式中的 log 与粗体 log；普通、上下标与粗体的 `\mathrm{base}`，以及 `\text{base}` |
| `syntax-colors.tex` | 代码配色与常规直立字形 |
| `block-spacing.tex` | 代码卡片与引用块前后、二级列表、分隔线的竖向间距 |

`quotes`、`syntax-colors`、`block-spacing` 的正文与横版共用，见 `../fixtures/README.md`；本目录的这三份只是载入竖版布局的包装。

## 检查

`check.py` 检查扉页的内容、可选分支与链接，代码跨页后的完整性与行号，引号对照写法及作用域，四、五级标题独立成行并与后文同页，以及目录父子条目保护。章节另起页由 `section-breaks` 的编译期断言检查。边界按可用空间构造，不复制设计字号、栏宽或间距。

默认运行不含 `syntax-colors`、`block-spacing` 与两份数学字体对照，需查看时按样张名编译。这些样张与综合预览负责外观验收；自动检查不锁定精确视觉参数。共同流程见 `../README.md`。

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
