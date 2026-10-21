# 共用测试资源

本目录存放导言区效果检验使用的资源，不属于算法笔记正文，也不要求代码片段能独立运行。所有引用使用项目根目录相对路径，例如 `preamble/tests/fixtures/示例 文件_1.cpp`。保留文件的真实名称与内容；不要在这里写入 PDF、日志或缓存。

## 代码资源

| 文件 | 用途 |
| --- | --- |
| `示例 文件_1.cpp` | 中文、空格、下划线路径，默认与显式代码标题，C++ 高亮 |
| `quotes.cpp` | 中文双引号在代码注释与字符串中的字体隔离 |
| `sample.py` | Python 高亮与按语言设置字号 |
| `sample.sh` | Bash 高亮 |
| `Makefile test` | 含空格的路径与 Makefile 高亮 |
| `long-code.cpp` | 长代码跨页，确认续页不重复标题 |
| `line-number-wrap.cpp` | 四行人工代码，覆盖长行折行、空行编号、源文件行号及新卡片重新从 1 开始 |
| `landscape-long.cpp` | 横版的人工长代码：100 个编号不同的声明，用于核对单个卡片跨栏、跨页的顺序与完整性；不是算法模板 |

`示例 文件_1.cpp`、`sample.py`、`sample.sh`、`Makefile test` 与 `long-code.cpp` 由 `mystyle/` 的样张引用，布局样张也可以复用。

## 扉页资源

三版的扉页样张（`portrait/`、`landscape/`、`code/` 中的 `titlepage.tex`）共用：

| 文件 | 用途 |
| --- | --- |
| `titlepage-special.commit` | 模拟 `scripts/commit-info.sh` 的四行输出；提交说明含 `\ { } $ & # ^ _ % ~`、`^^41`、`--` 及中文引号、破折号，状态为 clean |
| `titlepage-long-dirty.commit` | 中西文混排的超长提交说明，检验居中换行与底边对齐；状态为 dirty |
| `titlepage-wide.png`、`titlepage-tall.png` | 800 × 300 与 300 × 800 像素的人工配图（ImageMagick 生成），分别检验配图区域的宽度与高度约束 |

配图区尺寸以各版布局的 `\TitlePageSetup` 为准。`.commit` 文件逐行原样读取，修改时保持四行结构，不要加入 TeX 转义。

## 共用样张正文

几版内容相同、只是载入的布局不同的样张，正文放在这里；各版目录中的同名样张只保留载入本版布局的几行包装，样张文件名与 PDF 产物路径不变。正文由包装文件在 `\begin{document}` 之后 `\input`，不能单独编译。`twocolumn-*-body.tex` 只有横版引用，单独存放是为了两版布局取值分开时，代码版加回包装即可恢复样张，见 `../code/README.md`。

| 文件 | 引用它的样张 |
| --- | --- |
| `quotes-body.tex` | `portrait/`、`landscape/` 的 `quotes.tex` |
| `syntax-colors-body.tex` | `portrait/`、`landscape/` 的 `syntax-colors.tex` |
| `twocolumn-flow-body.tex` | `landscape/` 的 `flow.tex` |
| `twocolumn-code-cards-body.tex` | `landscape/` 的 `code-cards.tex` |
| `twocolumn-toc-layout-body.tex` | `landscape/` 的 `toc-layout.tex` |
| `block-spacing-body.tex` | `portrait/`、`landscape/` 的 `block-spacing.tex` |

包装文件中 `\input{…}` 行末的 `%` 用于去掉换行产生的空格，使排版结果与正文直接写在样张里时相同。修改这些正文后，引用它的各版样张都要重新编译并检查。
