# LaTeX 导言区配置

本目录集中管理宏包、版式与自定义接口。主文件在 `\documentclass` 之后直接加载所需文件，不增加 `setup.tex` 或 `layout-common.tex`。

| 文件或目录 | 职责与当前状态 |
| --- | --- |
| `packages.tex` | 已加载中文、OpenType 数学、图片、颜色、删除线、布局、标题、页眉、列表、目录、minted、tcolorbox 与超链接支持。 |
| `layout-portrait.tex` | 已实现首轮纵向布局：左右 20 mm、上下 15 mm（包含页眉页脚），宋体正文、苹方标题、Latin Modern 数学、Maple 代码；待用户审阅样张。 |
| `layout-landscape.tex` | 横版独立布局，目前为空占位文件。 |
| `layout-code.tex` | 仅代码版独立布局，目前为空占位文件；纸张方向、栏数等尚未确定。 |
| `mystyle.tex` | 已实现 `\Highlight`、`\InputCode`、`quoteblock` 与 `\Separator`。 |
| `fonts/` | 随项目保存的单色 Noto Emoji 静态字体与 OFL 许可，供纵向版两个 Unicode 符号映射使用。 |
| `tests/` | 当前已建立 `mystyle/`、`portrait/` 与共用资源 `fixtures/`；横版及代码版检验待实现。 |

入口仅保留文档类声明、下列三个导言区引用和标题／作者／日期等元信息；纸张、字体、字号、间距及编号等排版设置集中放在导言区文件中。ctex 加载前所需的临时字体选项由 `packages.tex` 管理。

三个入口共用 `packages.tex` 和 `mystyle.tex`，中间加载本版的 `layout-<版本>.tex`；所有字体、纸张、间距等设置在各版布局文件中独立维护，不设置公共布局文件。横版与仅代码版入口目前同样为空占位文件。

`main-portrait.tex` 当前采用的加载顺序：

```latex
\input{preamble/packages.tex}
\input{preamble/layout-portrait.tex}
\input{preamble/mystyle.tex}
```

`\Highlight` 已按用户确认实现为 `#FFFF00` 背景、零内边距的不可拆分行内短语框。`\InputCode` 已实现浅灰标题栏、细灰边框、2 mm 圆角与跨页排版，左侧按语言显示单色 Nerd Font 图标，不显示右侧语言标签；代码区外观可通过各语言的 `\setminted[语言]{...}` 设置，续页不重复标题。`quoteblock` 已实现浅灰背景、左侧深灰竖线和跨页排版，竖线外侧至正文约一个中文字宽（`left=\ccwd`），其余三侧内边距 2 mm，并通过 `parbox=false` 保留所在版式的段间距与首行缩进；标准 `quote` 不变，当前不要求嵌套。`\Separator{}` 已实现为适应所在容器宽度的浅灰细线，线上下有间距，不强制换页。接口要求见根目录及 `contents/` 下的 `AGENTS.md`；每个接口均配有效果检验。

所有路径相对于项目根目录，不能假定加载本目录文件会改变工作目录。建议 XeLaTeX；minted 依赖 `latexminted`。宏包已加载不等于自定义接口或整本文档已经可编译。

完整版计划共用 `contents/chapters.tex`，代码版计划使用 `contents/code-index.tex`；内容清单不放在导言区。两个清单尚未创建，竖版仍直接引入 19 篇章节。

从任意工作目录调用根目录脚本均会切换到项目根目录：

```sh
./run.sh             # 默认 portrait
./run.sh portrait
./run.sh landscape
./run.sh code
./run.sh all
./run.sh --help
```

产物分别为 `build/portrait/main-portrait.pdf`、`build/landscape/main-landscape.pdf`、`build/code/main-code.pdf`，辅助文件与 minted 缓存也按版本隔离。空入口提前报错；`all` 先检查三个入口，再按上述顺序构建，遇到失败停止。目前横版、代码版尚不可构建，脚本支持目标不代表该版内容已实现。

根目录 `run.sh` 至少编译两轮，并检查主文档目录、交叉引用和书签辅助记录是否稳定及是否仍有重编译提示，最多八轮。仅稳定且生成非空 PDF 后清理本版已知辅助文件与 minted 缓存，不清理其他版本或测试目录；编译失败或达到上限仍未稳定时，返回失败并保留日志。

构建脚本验证（2026-10-12）：Bash 语法检查通过；临时环境验证了默认目标、全部目标、从其他目录调用、非法参数、空入口预检、至少两轮收敛、八轮上限、失败保留和跨版本清理隔离；三个最小入口均通过真实 XeLaTeX + minted 编译，成功后各目录只保留对应 PDF。这些检查不代表完整笔记或尚未实现的横版、代码版已通过内容与视觉验收。

## 纵向版首轮实现与验证（2026-10-12）

正文 10.5/15 pt，章节、二级、三级标题分别为 22/28、14/19、11.5/16 pt；段首不缩进，列表适度紧凑。章节另起页，章首页隐藏页眉，其他正文页统一显示当前一级标题，页码居中；目录展开到三级，采用单栏书籍目录：一级苹方 Semibold 12/15 pt，二级宋体 Songti SC Regular 10.5/15 pt、三级宋体 Songti SC Regular 10/15 pt，二三级西文使用 Latin Modern Roman；以目录 Regular 字体 10 pt 的“中”实测宽度缩进 0、2、4 倍，一级无点线、二三级中灰点线的点中心间距为 9 pt；一级页码 11 pt Regular，二三级页码 10 pt Regular；二三级不加额外条目前留白，行距统一 15 pt。PDF 书签包含全部标题层级并默认全部展开。标题页外观也由纵向布局定义，入口只提供元信息。

代码正文（含内嵌 minted 和中文注释）使用 Maple Mono NF CN，9/12 pt，禁用字体连字；启用 cv01 去除符号间隙，启用 cv32—cv37 将手写斜体切换为常规斜体；行内代码不随之改变。`mystyle.tex` 的 `input-code-title/.try` 是可选 tcolorbox 外观设置，纵向布局将其定义为苹方 Medium 9/12 pt；其他检验未定义时仍保留原默认标题字体。

西文正文使用 Latin Modern Roman 的 TeX Live 静态字形（lmroman10），包含原生粗体、斜体和粗斜体；数学按用户确认使用 Latin Modern Math。保留原有 `\boldsymbol` 语义，显式配置 bold 数学版本：数学符号采用 `FakeBold=1.2` 轻度合成加粗，算子通过 `\setoperatorfont{\symup}` 使用所选数学字体的直立字形，粗体版本随数学字体合成加粗；显式 `\mathrm` 通过在 `begindocument/end` 钩子中定义的、带外层分组的 `\symup` 使用所选数学字体，兼容 `^\mathrm{mid}`、`_\mathrm{mid}` 的原有写法，粗体版本随数学字体合成加粗；`\text` 保持正文字体。STIX Two Math 对照使用相同策略，仅替换数学字体。具体依赖与运行方式见 `tests/portrait/README.md`。

三份纵向样张编译收敛，综合样张 6 页、数学对照各 1 页，全部逐页渲染检查；无缺字、Overfull 或字体字形替换。既有五个接口检验也重新两轮编译通过，日志无缺字／Overfull。本轮未编译或视觉验收完整笔记。


## InputCode 卡片设计（2026-10-12）

按批准方案实现浅灰标题栏（F5F5F7）、白色代码区、0.4 pt 灰色边框（D1D1D6）、2 mm 圆角，无黑色标题分隔线。文件名颜色 1D1D1F；纵向标题使用苹方 Medium 9/12 pt。左侧 Nerd Font 图标为单色灰黑（6E6E73），复用已安装的 Maple Mono NF CN，不新增字体文件，不显示右侧语言或版本。图标由现有语言参数选择，当前覆盖 C、C++、Python、Bash、Makefile 及相应别名；其余语言使用通用代码文件图标。映射依据 [Nerd Fonts 官方 glyphnames.json](https://github.com/ryanoasis/nerd-fonts/blob/master/glyphnames.json)。

设置 boxsep=0pt，标题左右内距 2.5 mm、上下 1.5 mm；图标占 4 mm；代码区不随文件名缩进，左右内距均为 2.5 mm、上下 2 mm。长标题完整换行且续行与文件名对齐；续页不重复标题与图标，分页连接处直边，只在代码块首尾保留圆角。接口参数、正文、代码字体与高亮不变。

新增 `preamble/tests/portrait/code-cards.tex`（2 页）并纳入纵向检验脚本；修改前复现长标题 147.52 pt 溢出，修改后无溢出。六份纵向样张与五份独立接口样张各两轮编译通过，日志无缺字、Overfull 或字体替换。已逐页渲染检查代码卡片样张 2 页、独立代码样张 1 页及独立跨页样张 2 页，并检查综合样张第 4、5 页；文字提取确认图标码位、长标题完整、跨页标题只出现一次及 36 行代码无遗漏。其余独立接口与纵向样张本轮仅编译回归，未重新逐页视觉验收。

完整竖版通过 `./run.sh portrait` 三轮收敛，仍为 151 页；末轮无缺字，原有 4 条 Overfull 与 2 条 amsmath 警告仍在。已渲染检查完整 PDF 第 20、21 页 KMP 跨页及第 110 页长文件名，未逐页验收全文。横版与代码版仍为空占位；本次未修改正文、未提交或推送。


InputCode 代码区缩进调整（2026-10-12）：按用户要求，代码区左内距由 6.5 mm 改为 2.5 mm，与右内距一致，不再与标题文件名对齐；标题图标及长标题续行对齐保留。六份纵向样张和两份独立代码样张各两轮通过，日志无缺字、Overfull 或字体替换；已检查代码卡片两页及独立代码样张，独立样张显式开启的行号使用 minted 默认外侧位置。完整竖版三轮收敛，151 页，无缺字，仍有原有 4 条 Overfull 与 2 条 amsmath 警告；已检查完整 PDF 第 20、21 页，未逐页验收全文。


纵向代码配色（2026-10-12）：`layout-portrait.tex` 使用用户指定的深灰 `30343B`、灰蓝 `506B82`、灰绿 `58715D` 与注释灰 `70757D`；注释斜体，其余 Regular。minted 的 bw 样式加载后应用有限 token 映射，并为 C++ 补充 vector/string/pair 类型名称；卡片续页正文也保持深灰。适配 minted 3.x / Pygments 2.x，升级后运行 `tests/portrait/run.sh` 和 `python3 preamble/tests/portrait/check-syntax-colors.py`（从根目录，后者需要 PyMuPDF）。验证范围见 `tests/portrait/README.md`。


InputCode 间距修复（2026-10-13）：内部 minted 的 vspace、topsep、partopsep 清零，只由卡片的上下 2 mm 内边距管理内部留白；独立 minted 与卡片外间距不变。间距断言及编译、视觉检查范围见 tests/mystyle/README.md。


西文正文调整（2026-10-13）：按用户确认改为 Latin Modern Roman（lmroman10），正文大小仍为 10.5/15 pt；同步更新文本类数学字母的粗体映射。目录中继承正文的西文和页码随之更新，中文、标题、数学与代码字体配置不变。八份纵向样张各两轮收敛、代码配色检查通过，完整竖版三轮收敛，153 页；末轮无缺字或字体替换，仍有 3 条 Overfull 与 2 条 amsmath 警告。检查了目录、数学样张及完整 PDF 第 2、21、23、69 页；未逐页验收全文，未重编译公共接口独立样张。


目录字体方案 A（2026-10-13）：一级苹方 Semibold 12/15 pt，二三级宋体 Songti SC Regular 配 Latin Modern Roman，分别为 10.5/15 pt 与 10/15 pt；取消目录专用思源字体选择，其他目录参数保持不变。目录样张两轮通过、三页均已渲染；完整竖版三轮收敛，153 页，全部五页目录已检查，197 个链接目标有效、208 个书签保留。末轮无缺字或字体替换，仍有 3 条 Overfull 与 2 条 amsmath 警告。其余独立样张未重编译、正文未逐页视觉验收。


目录标题居中（2026-10-13）：按用户要求，仅为“目录”标题添加左右对称伸缩间距，字体、字号及上下间距不变，条目继续左对齐。目录样张同步使用标题后置设置，并保留末端对齐胶。样张两轮通过，无缺字、Overfull 或字体替换，已渲染检查第一页；完整竖版三轮收敛，仍为 153 页，已渲染检查第 2 页。PDF 坐标核对确认标题水平中心与纸张中心一致，纵向位置不变；除该标题外，全书文字位置、字体、字号与修改前一致。末轮仍有 3 条 Overfull 与 2 条 amsmath 警告，无缺字或字体替换。未重新逐页视觉验收正文或重编译其他样张；未修改正文，未提交或推送。
