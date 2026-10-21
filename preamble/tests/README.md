# 导言区效果检验

本目录只检验 `preamble/` 中的接口与各版布局，不放置或引用 `contents/` 的章节。修改约束与各类改动的验收范围见 `../AGENTS.md`。

## 组织

| 目录或文件 | 内容 |
| --- | --- |
| `mystyle/` | 四个自定义接口的独立样张，不加载各版布局 |
| `portrait/` | 竖版：扉页、目录、标题层级、分页、单色符号、代码卡片、引号作用域与综合回归样张；另有配色、块间距与数学字体视觉对照，以及 PDF 检查脚本 `check.py` |
| `landscape/` | 横版：扉页、分栏与连续章节、页眉、目录、接口跨栏、引号作用域、图片；另有配色与块间距视觉对照，以及 PDF 检查脚本 `check.py`（加参数 `code` 检查代码版） |
| `code/` | 代码版：只有扉页样张，其余版式由横版样张检验；检查复用 `landscape/check.py` |
| `fixtures/` | 共用的代码与扉页资源，以及几版共用的样张正文（`*-body.tex`） |
| `pdfcheck.py` | 各组 `check.py` 共用的功能检查与 PDF 读取工具 |
| `build/` | 各组的 PDF、日志、缓存与渲染图，按组分目录；被 Git 忽略 |

## 编译

所有样张都从项目根目录编译，章节、宏包与测试资源的路径不随样张所在目录改变。PDF、日志与 minted 缓存输出到 `build/<组名>/`，不写入源码目录。

各组由所在目录的 `run.sh` 编译，可从任意目录调用；不带参数时编译本组回归样张，也可只传入样张名。四个脚本都调用 `scripts/xelatex-converge.sh --quiet --strict`，把每份样张编译到收敛；日志出现缺字、Overfull、字体替换或页眉高度不足时失败，并保留产物。收敛规则见 `scripts/README.md`。

```sh
bash preamble/tests/mystyle/run.sh
bash preamble/tests/portrait/run.sh
bash preamble/tests/landscape/run.sh
bash preamble/tests/code/run.sh
```

四个 `run.sh` 只差组名与样张列表，但仍各组一份，不合并成一个带参数的脚本：每份只有十余行，合并后各 README 与检查提示中的命令都要改。

依赖 XeLaTeX、`latexminted` 与 `packages.tex` 中的宏包。`mystyle/` 的样张使用 TeX Live 的 Fandol 字体，另需 Maple Mono NF CN 提供代码标题的图标。其余三组使用各版的设计字体：Songti SC、PingFang SC、Maple Mono NF CN，以及 TeX Live 的 Latin Modern 字体与项目内的 Noto Emoji。各组的其他依赖见其 README。

## 自动回归与视觉验收

自动测试保留内容完整性、顺序、行号、条件分支、链接、书签、字体局部作用域与标题跟随正文的关系（用户确认：视觉调整通常不应要求改测试）。不再逐项断言字体名、字号、色值、基线位置、精确间距与自然分页的固定页码；这些设计决定仍由 `../README.md` 维护，通过渲染样张查看。

各组功能检查在 `check.py`，共享断言在 `pdfcheck.py`，代码版复用横版检查（用户确认：避免同一功能的断言在几版中走样）。使用显式检查，不用裸 `assert`；按小节记录失败并统一返回非零。README 只说明覆盖范围，不复制断言数值（用户确认：减少重复维护）。

PDF 的实际版心与扉页标记由构建脚本记录，读取工具见 `scripts/README.md`。不把布局参数再抄到 Python；旧 PDF 缺少记录时明确要求重建。检查不会用当前源码的版心套用旧 PDF。

| 命令（从任意目录运行） | 功能检查 |
| --- | --- |
| `python3 preamble/tests/portrait/check.py` | 扉页分支与链接、代码内容与行号、引号作用域、标题与后文同页、目录父子条目保护 |
| `python3 preamble/tests/landscape/check.py [code]` | 横版另查章节流向、页眉、跨栏跨页的代码与引用、目录条目与链接；`code` 只查扉页 |

`scripts/check.sh --full` 编译默认回归样张并运行上述检查。配色、块间距、数学字体对照保留为按需编译的视觉样张，不进入默认回归：

```sh
bash preamble/tests/portrait/run.sh syntax-colors block-spacing math-latin-modern math-stix
bash preamble/tests/landscape/run.sh syntax-colors block-spacing
```

修改视觉设计后，查看受影响版本的综合样张、相关专项样张和整书。重点检查颜色作用范围、字形、缺字、重叠、长标题、代码连字、图片与卡片边框，以及跨页跨栏连接处。严格日志与功能检查不能替代这些目视检查。

`compare-pdf.py` 逐页报告差异，用于审阅影响范围；有意改变的外观不要求与旧 PDF 相同（用户确认）。默认基线收录回归样张；按需视觉样张用两个 PDF 路径单独比较。

苹方的 HK、MO、TC、SC 字面共用 TTC 内的 CFF 轮廓，PDF 中显示 `PingFangHK` 不能证明用了哪个字面；需要核对字形时比较 CID 与 SC 字面的 cmap。

根目录 `run.sh` 只构建三版整书，不运行这些检验；整书产物在根目录的 `build/<版本>/`，与本目录的 `build/` 互不影响。整书的越栏检查是 `scripts/check-full.py`。

## 验证状态

2026-10-22，基于提交 `b7e65e0`，工作区有未提交修改（测试、检查与构建脚本、相关文档，以及用户的正文修改）。在 `LC_ALL=zh_CN.UTF-8` 下运行 `scripts/check.sh --full`、`./run.sh all`，并在最终脚本上复跑各版 PDF 功能检查与 `scripts/check.sh`，均通过。字体编译在可访问 macOS 字体服务的环境进行。

自动检查：三版整书与修改前同一工作区的基线用 `scripts/compare-pdf.py` 逐页比较，文字、位置、字体、颜色、图形、链接与书签均相同，末轮警告汇总一致。回归样张的差异仅出现在重新构造的边界与说明文字。隔离副本同时修改配色、正文字号、扉页字号、行号样式、边距与栏距，未改测试即通过回归；向副本 PDF 注入缺失代码行、错误目录目标页和错误提交链接，均被检查拦截。

人工查看：渲染检查竖版长提交信息扉页、代码版扉页、横版代码卡片的跨栏跨页连接、横版引用跨栏，以及竖版页底标题后接正文和公式的页面。未逐页人工查看整书，未做实物打印；按需视觉对照样张未重新编译。
