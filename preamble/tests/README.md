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

自动测试保留内容完整性、顺序、行号、条件分支、链接、书签、字体局部作用域与标题跟随正文的关系（用户确认：视觉调整通常不应要求改测试）。不再逐项断言字体名、字号、色值、基线位置、精确间距与自然分页的固定页码；具体视觉参数以 `.tex` 为准，行为与设计理由见 `../README.md`，通过渲染样张查看效果。

各组功能检查在 `check.py`，共享断言在 `pdfcheck.py`，代码版复用横版检查（用户确认：避免同一功能的断言在几版中走样）。使用显式检查，不用裸 `assert`；按小节记录失败并统一返回非零。README 只说明覆盖范围，不复制断言数值（用户确认：减少重复维护）。

检查直接读取样张的可见文字、图片、链接与书签，不要求额外 PDF 元数据。双栏样张按纸张中线区分阅读顺序，行号按人工代码标记定位；这里只检查已知样张，不推断通用版心或扫描整书越界。

| 命令（从任意目录运行） | 功能检查 |
| --- | --- |
| `python3 preamble/tests/portrait/check.py` | 扉页分支与链接、代码内容与行号、引号作用域、标题与后文同页、目录父子条目保护 |
| `python3 preamble/tests/landscape/check.py [code]` | 横版另查章节流向、页眉、跨栏跨页的代码与引用、目录条目与链接；`code` 只查扉页 |

`scripts/check.sh --full` 编译默认回归样张并运行上述检查。默认回归包含竖版 `math-latin-modern`，保留常用数学命令的严格日志检查；综合预览、配色、块间距与 STIX 数学字体对照按需编译（用户确认：减少综合样张与专项回归的重复维护）：

```sh
bash preamble/tests/portrait/run.sh preview syntax-colors block-spacing math-stix
bash preamble/tests/landscape/run.sh preview syntax-colors block-spacing
```

修改视觉设计后，按 `../AGENTS.md` 的分级范围查看相关样张，必要时构建和抽查受影响版本整书。重点检查颜色作用范围、字形、缺字、重叠、长标题、代码连字、图片与卡片边框，以及跨页跨栏连接处。严格日志与功能检查不能替代这些目视检查。

苹方的 HK、MO、TC、SC 字面共用 TTC 内的 CFF 轮廓，PDF 中显示 `PingFangHK` 不能证明用了哪个字面；需要核对字形时比较 CID 与 SC 字面的 cmap。

根目录 `run.sh` 只构建三版整书，不运行这些检验；整书产物在根目录的 `build/<版本>/`，与本目录的 `build/` 互不影响。整书通过编译警告与页面抽查验收。
