# 共用实现

本目录存放三版共用的排版实现，由各版布局文件 `preamble/layout-<版本>.tex` 按顺序 `\input`，入口不直接引用。

这里只放实现，不放各版参数。纸张、字号、间距、标题样式、栏距、扉页版面等参数写在各版布局文件中。修改约束、命名规则与验收范围见 `../AGENTS.md`：本目录的改动影响所有版本。

| 文件 | 内容 | 载入的版本 |
| --- | --- | --- |
| `fonts.tex` | 正文与导航字体，单色符号（⭐、🚩）映射，数学字体与 `\mathrm`，行内等宽与代码块字体（`fontfamily=bookcode`） | 三版 |
| `colors.tex` | 页眉页脚灰、目录点线、代码四色、扉页文字与细框 | 三版 |
| `toc.tex` | 关闭标题自动编号，目录深度与书签，目录条目排版（`\BookTOCEntry`） | 三版 |
| `twocolumn.tex` | 启动双栏、通栏目录标题、页顶所在章的页眉（`\BookChapterAnchor`）、图片按栏宽解释 `\textwidth` | 横版、代码版 |
| `code.tex` | Pygments 词法配色、minted 默认设置、代码卡片标题，以及代码卡片与引用块的前后距（`book-box-spacing`） | 三版 |
| `titlepage.tex` | 扉页与提交信息读取（`\TitlePageReadCommit`），元信息命令（`\EnglishTitle`、`\TitlePageImage`、`\EditionLabel`），版面参数接口（`\TitlePageSetup`） | 三版 |

## 载入顺序

布局文件中的顺序如下：

1. `\geometry`
2. `fonts.tex`、`colors.tex`
3. 字号、段落与标题样式（本版参数）
4. `toc.tex`
5. 竖版：目录标题与页眉；横版、代码版：`twocolumn.tex`
6. `code.tex`
7. `titlepage.tex` 与 `\TitlePageSetup{…}`

需要保持的依赖：

- `toc.tex` 在设置字号之后载入，目录缩进单位按载入时的字体测量。
- `code.tex` 和扉页使用 `colors.tex` 中的颜色；扉页的强调色由代码的灰蓝色派生。
- `begindocument/end` 钩子按以下先后执行：`\mathrm` 重定义（`fonts.tex`）、启动双栏、双栏目录重定义（`twocolumn.tex`）。

## 参数

- 扉页：`\TitlePageSetup{title=…, english=…, author=…, image=…, stamp=…, image-width=…, image-height=…}`。前五项是以纸张中心为原点的纵向位置（书名、英文书名、作者的基线，配图区中心，提交信息底边），后两项是配图区尺寸。7 项都必须给出，缺少时编译报错；数值按原文交给 TikZ，不预先换算。
- 代码字号默认 8/10.5 pt；某版要不同时，在载入 `code.tex` 之后用 `\setminted{fontsize=…}` 覆盖。
- 代码卡片与引用块的前后距：各版布局设定 `\BookBoxBeforeSkip`、`\BookBoxAfterSkip`，由 `code.tex` 的 `book-box-spacing` 样式使用。`mystyle.tex` 中两种盒子以 `book-box-spacing/.try` 引用，不载入布局的接口样张沿用 tcolorbox 的默认前后距。
- 双栏版本须在 `\titleformat{\section}` 的标题文字处调用 `\BookChapterAnchor`，页眉据此判断页顶所在的章。
- 目录字号与点线、代码配色、页眉字号等目前三版相同，直接共用。某版需要不同时，再增加参数或在该版布局中覆盖。
