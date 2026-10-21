# 导言区效果检验

本目录只检验 `preamble/` 中的接口与各版布局，不放置或引用 `contents/` 的章节。修改约束与各类改动的验收范围见 `../AGENTS.md`。

## 组织

| 目录或文件 | 内容 |
| --- | --- |
| `mystyle/` | 四个自定义接口的独立样张，不加载各版布局 |
| `portrait/` | 竖版：扉页、目录、标题层级、分页、单色符号、代码卡片与配色、块间距、引号字体切换、数学字体对照与综合样张，以及 PDF 检查脚本 `check.py` |
| `landscape/` | 横版：扉页、分栏与连续章节、页眉、目录、接口跨栏、块间距、引号字体切换、图片，以及 PDF 检查脚本 `check.py`（加参数 `code` 检查代码版） |
| `code/` | 代码版：扉页、连续章节、代码卡片、配色、块间距、引号字体切换与目录；检查复用 `landscape/check.py` |
| `fixtures/` | 共用的代码与扉页资源，以及几版共用的样张正文（`*-body.tex`） |
| `pdfcheck.py` | 各组 `check.py` 共用的检查工具、单位、几何常量，以及几版共用的断言 |
| `build/` | 各组的 PDF、日志、缓存与渲染图，按组分目录；被 Git 忽略 |

## 编译

所有样张都从项目根目录编译，章节、宏包与测试资源的路径不随样张所在目录改变。PDF、日志与 minted 缓存输出到 `build/<组名>/`，不写入源码目录。

各组由所在目录的 `run.sh` 编译，可从任意目录调用；不带参数时编译本组全部样张，也可只传入样张名。四个脚本都调用 `scripts/xelatex-converge.sh --quiet --strict`：每份样张至少两轮、最多八轮，直到收敛；日志出现缺字、Overfull、字体替换或页眉高度不足时失败，并保留产物。

```sh
bash preamble/tests/mystyle/run.sh
bash preamble/tests/portrait/run.sh
bash preamble/tests/landscape/run.sh
bash preamble/tests/code/run.sh
```

四个 `run.sh` 只差组名与样张列表，但仍各组一份，不合并成一个带参数的脚本：每份只有十余行，合并后各 README 与检查提示中的命令都要改。

依赖 XeLaTeX、`latexminted` 与 `packages.tex` 中的宏包。`mystyle/` 的样张使用 TeX Live 的 Fandol 字体，另需 Maple Mono NF CN 提供代码标题的图标。其余三组使用各版的设计字体：Songti SC、PingFang SC、Maple Mono NF CN，以及 TeX Live 的 Latin Modern 字体与项目内的 Noto Emoji。各组的其他依赖见其 README。

## PDF 检查

每组的 PDF 检查都在本组目录的 `check.py` 中，按样张分小节；代码版复用 `landscape/check.py`，加参数 `code`。几版共用的断言写成 `pdfcheck.py` 中的函数，由各版传入与本版布局一致的参数（用户确认）：按样张拆分时，竖版、横版各写一份扉页检查，断言容易走样。

`check.py` 读取 `build/` 中的样张 PDF，需要 Python 3 与 PyMuPDF（`python3 -m pip install --user pymupdf`），不由 `run.sh` 自动调用。`pdfcheck.py` 提供：

- 用 `Checker` 做显式检查，不用 `assert`，`python3 -O` 下照常生效；
- 每项失败只记录、不中断，按小节输出“通过”或“未通过”，最后列出全部未通过项并以 1 退出；
- 统一单位：PDF 坐标的单位是 bp，`mm()`、`pt()` 把毫米、TeX pt 换算为 bp，`to_pt()` 反向换算；
- 几何常量：竖版的页眉线，横版与代码版共用的页眉线、正文下缘与栏分界；代码配色；读取文字行与代码文字的函数；
- 几版共用的断言：扉页 `check_titlepage`、代码配色 `check_code_palette`、框外行号 `check_code_line_numbers`、块间距 `check_block_spacing`、引号字体与断行 `check_quotes`。

| 命令（从任意目录运行） | 检查的样张 |
| --- | --- |
| `python3 preamble/tests/portrait/check.py` | 竖版：扉页、代码配色与卡片、块间距、引号字体切换、四五级标题 |
| `python3 preamble/tests/landscape/check.py [code]` | 横版（或代码版）：扉页、纸张、流向、页眉、代码配色与跨栏、引用、列表符号、块间距、引号字体切换、目录、图片 |

`scripts/check.sh --full` 依次编译四组样张并运行上表的全部检查。检查通过后，仍要渲染查看 PDF 的边框、字形、长标题，以及跨页、跨栏的连接处。苹方同一字重的 HK、MO、TC、SC 四个字面共用 TTC 中的一份 CFF 轮廓表，表内字体名为 `PingFangHK-<字重>`；xdvipdfmx 按它命名嵌入字体，所以 `pdffonts` 与 PyMuPDF 总显示 `PingFangHK`，不能据此判断用了哪个字面。字形由 XeTeX 选中的字面决定；要核对，就比较 PDF 中各字的 CID 与 SC 字面 cmap 的映射。

根目录 `run.sh` 只构建三版整书，不运行这些检验；整书产物在根目录的 `build/<版本>/`，与本目录的 `build/` 互不影响。整书的越栏检查是 `scripts/check-full.py`。

## 验证状态

2026-10-21，基于提交 `0e11e26`；工作区有双引号字体分类、引号样张、PDF 检查与说明文档的未提交修改。修改前在该提交的干净工作区运行 `./run.sh all` 与 `scripts/check.sh --full` 并保存三版整书和全部样张作为基线；修改后在 `LC_ALL=zh_CN.UTF-8` 下运行 `scripts/check.sh`、`./run.sh all` 与 `scripts/check.sh --full`，三版整书和四组样张均收敛，严格日志检查与全部 PDF 检查通过。引号样张的窄行对照有预期的 Underfull 提示，无 Overfull、缺字或字体替换；新增检查在旧字体实现上能识别正文引号与双反引号写法不一致。

自动检查：逐页比较三版整书和全部既有样张的文字与位置、字体、字号、颜色、图片、矢量图形、书签和链接。既有样张无差异；整书页数、书签及正文逐页文字内容一致，字体变化仅为宋体正文双引号改用 Latin Modern Roman，其他字符的字体、字号和颜色不变；引号所在段落的文字与公式位置随字宽变化，目录链接目标坐标随目标位置调整。代码文字及各行字内间距保持一致，代码版除扉页增加未提交修改标记外无差异。三版整书末轮警告汇总与基线相同，横版、代码版整书越栏检查完成，既有警告不变。新增三版样张检验正文、粗斜体、列表、引用、高亮、标题、目录、页眉、行内代码、minted 与卡片的引号字体及嵌套恢复；正文与双反引号写法的字形和相对位置相同，苹方与 Maple 与原分类对照相同，单引号与 Unicode 书签保留，开引号不落在行尾、闭引号不落在行首。

人工查看：三版引号样张全部页面，以及竖版、横版整书中主定理的引号与相邻公式、粗体和代码卡片，未见重叠或裁切。未验证：未逐页人工查看整书与其他既有样张，未在阅读器中实际点击链接，未做实物打印验收。
