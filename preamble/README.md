# 导言区

本目录集中管理宏包、各版版式与自定义接口。修改约束与验收范围见 `AGENTS.md`，正文中的写法见根目录的 `WRITING.md`。

## 文件

| 文件或目录 | 职责 |
| --- | --- |
| `packages.tex` | 加载宏包并维护加载顺序：中文、OpenType 数学、图片、颜色、删除线、页面与分栏、标题、页眉、列表、目录、minted、tcolorbox 与超链接 |
| `layout-portrait.tex` | 竖版参数，以及一级标题前分页、页眉取当前一级标题、目录标题居中等竖版专用的做法 |
| `layout-landscape.tex` | 横版参数；双栏机制由 `shared/twocolumn.tex` 提供 |
| `layout-code.tex` | 代码版参数，目前取值与横版相同，单独维护 |
| `shared/` | 三版共用的实现：字体、配色、目录条目、双栏机制、代码样式与扉页，见其 README |
| `mystyle.tex` | 四个自定义接口，见下文 |
| `fonts/` | 项目内的单色符号字体及其许可，见其 README |
| `tests/` | 接口与各版版式的样张及 PDF 检查，见其 README |

## 载入方式

三个入口依次加载：

```latex
\input{preamble/packages.tex}
\input{preamble/layout-portrait.tex}
\input{preamble/mystyle.tex}
```

横版、代码版把第二行换成 `layout-landscape.tex`、`layout-code.tex`。各版布局再按 `shared/README.md` 列出的顺序载入共用实现。入口中与排版有关的只有这三行。所有路径相对项目根目录，加载本目录的文件不会切换工作目录。宏包能加载，不等于接口或整本笔记能编译。

## 三个版本

参数数值以布局文件为准，这里只概括结构。

- 竖版：A4 纵向单栏，左右 20 mm、上下 15 mm（含页眉页脚），正文 10.5/15 pt。一级标题另起页；章首页无页眉，其他页的页眉为当前一级标题；页码居中。目录单栏，标题居中。
- 横版：A4 横向双栏，四边 12 mm（含页眉页脚），栏距 8 mm，正文 10/14 pt。章节在栏内连续排版，章末不平衡两栏；页眉为页顶所在的一级标题。目录单独起页，标题通栏居中，条目分两栏。
- 代码版：版式同横版，只收录代码及其所属标题；入口由 `scripts/generate-code.py` 生成，见 `scripts/README.md`。
- 三版都有扉页：书名、英文书名、作者、配图与最新一次提交的信息。外观在 `shared/titlepage.tex`，各版用 `\TitlePageSetup` 给出版面参数；书名等元信息写在入口。

## 自定义接口

正文中的用法见 `WRITING.md`。外观与行为如下（用户确认）：

| 接口 | 外观与行为 |
| --- | --- |
| `\Highlight{内容}` | 接近 HTML `<mark>`：`FFFF00` 背景，零内边距。不可拆分的行内短语框，可含粗体与行内公式 |
| `\InputCode[标题]{语言}{路径}` | minted 代码卡片：`F5F5F7` 标题栏、0.4 pt `D1D1D6` 边框、2 mm 圆角，文件名为 `1D1D1F`。左侧按语言显示单色 Nerd Font 图标（`6E6E73`，占 4 mm），不显示语言标签。默认取路径中的文件名作标题，给出标题时以标题为准。代码区左右 2.5 mm、上下 2 mm，不随文件名缩进。跨页时续页不重复标题，只在首尾保留圆角。左边框外显示 4 pt、`808080` 的等宽行号，数字右缘距边框 1 mm，不占代码区宽度。前后距由各版设定，见“设计决定” |
| `quoteblock` 环境 | `F7F7F7` 背景、左侧 2 pt `777777` 竖线、直角。左内距为一个中文字宽（`\ccwd`，从竖线外侧算，含竖线厚度），其余三侧 2 mm。可跨页，保留所在版式的段间距与首行缩进；前后距与代码卡片相同。不要求嵌套，标准 `quote` 不变 |
| `\Separator{}` | 相当于 HTML `<hr>`：0.4 pt `A0A0A0` 横线，与上下两行文字的字面各隔约一行，宽度随所在容器，不分页 |

图标目前覆盖 C、C++、Python、Bash、Makefile 及其别名，其余语言用通用的代码文件图标；码位依据 [Nerd Fonts 的 glyphnames.json](https://github.com/ryanoasis/nerd-fonts/blob/master/glyphnames.json)。各语言的代码外观可以用 `\setminted[语言]{…}` 调整。

## 设计决定

以下由用户确认或批准。数值与实现见括号中的文件，代码注释写明了原因。

- 字体：中文正文用宋体 Songti SC，标题与导航用苹方 PingFang SC，粗体为 Semibold；西文正文用 Latin Modern Roman 的静态字形；数学用 Latin Modern Math，STIX Two Math 只用于对照样张（`shared/fonts.tex`）。
- 代码字体：代码块与行内代码都用 Maple Mono NF CN，关闭连字，启用 cv01 与 cv32–cv37。代码正文 8/10.5 pt，三版统一；普通 minted 片段默认不显示行号，长行折行；标题栏为苹方 Medium 9/12 pt（`shared/fonts.tex`、`shared/code.tex`）。
- 行号（用户确认）：仅 `\InputCode` 在卡片左边框外悬挂行号，沿用代码字体，4 pt、正体、`808080`，右对齐，距边框 1 mm；不压缩代码宽度，便于双栏查阅。每个文件从 1 开始，空行也显示编号，折行只在首个视觉行显示编号，跨页与跨栏连续（`mystyle.tex`）。
- 代码配色：四色。名称与标点 `30343B`，关键字、类型、数字与预处理 `506B82`，字符串 `58715D`，注释 `70757D`。不用斜体，也不用粗体区分 token；C++ 另把 `vector`、`string`、`pair` 当作类型名（`shared/colors.tex`、`shared/code.tex`）。
- 标题：竖版的四、五级标题与正文同字号，用苹方 Semibold 独立成行（`layout-portrait.tex`）。
- 列表（用户确认）：二级无序列表用空心圆点 `\textopenbullet`（U+25E6）；Latin Modern 中它与一级的实心圆点 `\textbullet` 外框相同，两级只差填充。二级列表不加上下间距，子项紧随父项：原先沿用一级的 3 pt，父项到首个子项反比同级条目之间还远（`layout-<版本>.tex`）。
- 卡片与引用块的前后距（用户确认）：盒顶距上一行文字的底为盒前距（竖版 9.5 pt，横版与代码版 9 pt），盒与盒之间也是这个距离；盒后把 `\prevdepth` 归零，下一行按段距与行距接排，另加盒后距（竖版 0 pt，横版与代码版 1.5 pt），后接标题时盒底相当于上一行的基线。紧跟标题的盒仍由 tcolorbox 处理。原先沿用 tcolorbox 默认的 `beforeafter skip balanced=0.5\baselineskip plus 2pt`：盒与盒之间只有半行，比正文与盒之间少约 2 pt，盒后的标题也比正文后的标题近（`layout-<版本>.tex`、`shared/code.tex`）。
- 分隔线（用户确认）：横线按正常行距排在上一行之后，下方另加 0.4 倍行距，与上下两行文字的字面各隔约一行。原先上下各加一整行，实际留白约一行半到两行，比二级标题上方的留白还大（`mystyle.tex`）。
- 目录：显示到三级；书签到五级，初始只显示一级（二至五级闭合）。条目采用方案 A：一级用苹方 Semibold；二、三级用宋体配 Latin Modern Roman，带点线；每级多缩进两个“中”的字宽；父条目不与首个子条目分开（`shared/toc.tex`）。
- 双栏：`emergencystretch` 为 6em，试过 3em 后撤回；页眉显示页顶所在的章；`\textwidth` 按当前栏宽解释（`layout-landscape.tex`、`shared/twocolumn.tex`）。
- 扉页：提交信息为眉题式三行，不用“·”串联；横版、代码版居中竖排；代码版书名后悬挂“（代码版）”，不参与居中（`shared/titlepage.tex`）。
- 结构：三版共用的实现放在 `shared/`，各版布局只放参数；代码版布局取值同横版，但单独维护。

另有两项实现选择：算子与 `\mathrm` 使用数学字体、`\text` 使用正文字体，以统一公式字形；⭐、🚩 映射到项目内的单色 Noto Emoji 字体，旧的 emoji 处理方式不再恢复。原因见 `shared/fonts.tex` 的注释与 `fonts/README.md`。

## 已知限制

- 未做实物打印验收；完整 PDF 没有逐页做视觉检查。
- 五级标题只完成了配置，正文尚未使用。
- 双栏版中，推导用的 `aligned` 整组不可拆分，可能在栏底留下空白；用户确认不处理。
- 分隔线恰在分页处时会排到下一页（栏）的顶端、紧贴页眉，像一条页眉线；用户确认暂不处理。
- 双栏栏宽较窄，较长的行内公式可能越出所在栏，由 `scripts/check-full.py` 报出；整书末轮日志中的 Overfull、Underfull 与 amsmath 等警告随正文变化，见 `scripts/README.md` 的“整书警告”。

验证状态见 `tests/README.md`（样张）。
