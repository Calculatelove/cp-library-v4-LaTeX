# 导言区修改约定

适用于 `preamble/` 下的宏包、布局、共用实现、自定义接口与样张。结构、接口规格与设计决定见 `README.md`，共用实现的载入顺序与参数接口见 `shared/README.md`，样张与检查脚本见 `tests/README.md`。

## 分工

- `packages.tex`：只加载宏包并维护加载顺序；ctex 加载前所需的字体选项也放在这里。
- `layout-<版本>.tex`：只放本版参数（纸张、边距、栏距、字号、段落、标题样式、扉页版面）和本版专用的做法。三版各自维护；代码版取值目前与横版相同，但不引用横版布局。
- `shared/`：只放三版共用的实现，不放参数，由各版布局按顺序 `\input`，入口不直接引用。某版需要不同取值时，增加参数或在该版布局中覆盖，不在共用文件里按版本分支（用户确认）。
- `mystyle.tex`：只有 `\Highlight`、`\InputCode`、`quoteblock`、`\Separator` 四个自定义接口。新增接口或改变外观须经用户确认。
- 命名：共用实现的命令、颜色和计数器以 `Book` 开头，expl3 变量用 `book` 模块名；供入口或样张调用的命令（`\EnglishTitle`、`\TitlePageImage`、`\EditionLabel`、`\RepositoryURL`、`\TitlePageReadCommit`、`\TitlePageSetup`）不加前缀。

## 改动与验收范围

| 改动 | 至少要做 |
| --- | --- |
| 某一版的布局 | 编译该版全部样张并运行其 PDF 检查；`./run.sh <版本>` 重建该版整书 |
| `shared/`、`mystyle.tex`、`packages.tex` | `./run.sh all` 与 `scripts/check.sh --full`，并与修改前的三版 PDF 及全部样张逐页比较文字与位置、字体、颜色、矢量图形、书签和链接（用户确认） |
| 纸张、边距、栏距或扉页版面 | 同步 `scripts/check-full.py`、`tests/pdfcheck.py` 中的几何常量与各组 `check.py` 传入的版面参数 |
| `tests/fixtures/*-body.tex` | 重新编译并检查引用它的各版样张 |
| 升级 minted 或 Pygments | 运行 `scripts/check.sh --full`；代码配色依赖它们的内部 token 接口 |

## 样张与检查

- 每个自定义命令或环境在 `tests/` 都有可从根目录编译的效果检验；新增接口或改变外观时同步补充。
- 样张只检验 `preamble/`，不引用 `contents/` 章节；产物只写入 `tests/build/`。
- 样张应覆盖中文及带空格的路径、多语言代码、跨页或跨栏。编译通过后仍要检查 PDF；改动后重新验证，历史结果不能作为新实现的证据。
- 每组样张的 PDF 检查都写在本组的 `check.py`，几版共用的断言放进 `tests/pdfcheck.py`，由各版传入本版参数；检查整本笔记的脚本放在 `scripts/`。检查使用 `tests/pdfcheck.py` 的显式检查，不用裸 `assert`；几版内容相同的样张正文放在 `tests/fixtures/*-body.tex`。

## 字体与环境

- 字体缺失时报错，不静默替换；不复制字体、不改系统字体缓存、不硬编码用户字体路径。macOS 沙箱可能挡住字体服务，此时换到能访问系统字体的环境编译，不为此改用其他字体。
- `tests/mystyle/` 的样张使用 TeX Live 的 Fandol 字体；测试字体与检验用的默认值都不代表用户确认的设计。
- 不开启不受限 shell escape。
- 不恢复已撤下的实现，例如旧的 emoji 修复、各版独立的 `titlepage-<版本>.tex`。
