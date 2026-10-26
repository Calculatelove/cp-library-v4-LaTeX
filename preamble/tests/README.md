# 排版样张操作指南

样张使用人工示例检验实际竖版、横版和代码版，不引用 `contents/` 正文。改动与验收范围以 `../AGENTS.md` 的分级表为准；本指南用于选择和运行样张。

## 选择样张

| 改了什么 | 看哪些样张 |
| --- | --- |
| 扉页、配图、提交信息 | 各版本的 `titlepage` |
| 代码卡片、行号 | 竖版和横版的 `code-cards` |
| 引用块、分隔线、高亮 | 横版 `interfaces`、竖版 `preview` |
| 代码配色 | `syntax-colors` |
| 卡片、列表与分隔线间距 | `block-spacing` |
| 目录与导航 | `toc-layout` |
| 章节分页、标题层级 | 竖版 `section-breaks`、`heading-levels`；横版 `flow` |
| 引号与字体局部作用域 | `quotes` |
| 单色符号、数学字体 | 竖版 `symbols`、`math-latin-modern` |
| 双栏图片宽度 | 横版 `images` |
| 字体、正文密度与整体版式 | 竖版和横版的 `preview` |

未标版本的样张在竖版、横版均有。代码版复用横版布局，只保留独立的扉页样张；代码版专用覆盖的验收要求见 `../AGENTS.md`。

## 编译与检查

依赖 XeLaTeX、`latexminted`、导言区宏包，以及 Songti SC、PingFang SC、Maple Mono NF CN（常规、粗体、斜体、粗斜体）。Latin Modern、空集符号所用的 New Computer Modern Math 与 mwe 示例图片由 TeX Live 提供；符号字体来自项目 `../fonts/`。PDF 功能检查另需 Python 的 PyMuPDF。

从项目根目录运行以下命令，也可从其他目录使用脚本的完整路径。不带样张名时编译该组默认回归，带名字时只编译指定样张：

```sh
bash preamble/tests/portrait/run.sh
bash preamble/tests/landscape/run.sh code-cards interfaces
bash preamble/tests/code/run.sh

python3 preamble/tests/portrait/check.py
python3 preamble/tests/landscape/check.py
python3 preamble/tests/landscape/check.py code
```

各组 `check.py` 检查该组默认回归产物；执行前应编译该组完整默认回归，避免缺少 PDF 或读到旧产物。`scripts/check.sh --full` 会完成默认回归编译与功能检查，不构建整书。

综合预览、配色和间距按需编译（用户确认：避免与专项回归重复编译）：

```sh
bash preamble/tests/portrait/run.sh preview syntax-colors block-spacing
bash preamble/tests/landscape/run.sh preview syntax-colors block-spacing
```

编译调用 `scripts/xelatex-converge.sh --quiet --strict`；缺字、Overfull、字体替换或页眉高度不足会导致失败。PDF、日志和缓存写入 `preamble/tests/build/<组名>/`，失败时也保留，排查方法见 `scripts/README.md`。

## 查看效果

自动检查保护内容完整性、顺序、行号、链接、书签、作用域与分页关系；具体外观不锁定数值，通过 PDF 目视确认（用户确认）。严格日志与功能检查不能代替查看页面。

- 检查字形、颜色作用范围、缺字、重叠、溢出、长标题、图片和边框。
- 代码中的运算符及 `fi`、`fl`、`ffi`、`ffl` 不应连字；中文注释与 ASCII 对齐，代码标题栏不用 Maple。
- 跨页、跨栏的代码与引用块内容连续，连接处正常，不侵入页眉页脚。
- 目录页码与标题起页一致；书签包含全部标题层级，初始只显示一级。
- xeCJK 字体族重定义提示是预期的；不应出现缺字或字体替换。PDF 中的 `PingFangHK` 名称不能单独证明用了哪个字面；需要精查时比较 CID 与 SC 字面的 cmap。

可用 Poppler 渲染已编译样张：

```sh
mkdir -p preamble/tests/build/portrait/render
pdftoppm -scale-to 1600 -png preamble/tests/build/portrait/preview.pdf preamble/tests/build/portrait/render/preview
```

边界样张的刻意留白用于触发分页分栏，不代表整书效果。整书与实物打印的验收不能由样张代替。

## 修改样张

`portrait/`、`landscape/`、`code/` 存放各版样张和运行入口，PDF 检查的共用实现放在 `pdfcheck.py`。各版共用的样张正文、代码和配图放在 `fixtures/`；共用正文不能单独编译，修改后检查实际引用它的版本。不要为单处使用的正文增加包装文件。

`fixtures/` 中的 `.commit` 资源模拟提交信息，保持四行：日期、短哈希、提交说明、`clean` 或 `dirty`。内容原样读取，不做 TeX 转义。资源路径相对项目根目录，保留中文、空格与大小写；产物只写入 `build/`。
