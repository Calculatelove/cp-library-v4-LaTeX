# 项目协作约定

本文件每次会话自动载入，只放全局规则。子目录的规则与说明不会自动载入，按“任务导航”主动读取。

## 项目目标

C.L. 的算法竞赛第四版笔记，已由 Markdown 迁移为 LaTeX，内容侧重结论、Trick 与代码模板。正文与代码由用户撰写，agent 协助排版、构建与检查。同一套正文输出三版：竖版（A4 纵向单栏）、横版（A4 横向双栏）、代码版（只收录代码及其所属标题，版式同横版）。

## 操作边界

- 不改动正文表述：不润色、纠错、增删、概括、翻译或重排正文、公式、代码、注释与文件名；疑似错误单独报告。只在用户要求时修改正文。
- 根目录 `README.md` 由用户维护，不要修改。
- 不擅自提交或推送。
- 修改前查看实际文件与未提交的改动；不覆盖用户的整理或清空，不擅自恢复历史实现。
- 用户确认过的规则持续有效。有不确定之处一次只问一个问题；普通实现选择在授权范围内自主决定。
- 术语：印书名、作者的第一页称“扉页”（title page，文件与宏名用 `titlepage`）；“封面”专指外封，项目暂无外封。
- 不使用 superpowers 插件，不建 `docs/` 设计稿或实施计划。

## 关键结构

- 入口：`main-portrait.tex`、`main-landscape.tex` 手写，除布局一行外逐行相同；`main-code.tex` 由 `scripts/generate-code.py` 以横版入口为模板生成，不要手工编辑。
- 入口只含：不带排版选项的文档类声明；依次 `\input` 的 `preamble/packages.tex`、`preamble/layout-<版本>.tex`、`preamble/mystyle.tex`；标题、作者、日期、英文书名、扉页配图等元信息；`\maketitle`、`\tableofcontents` 与章节。某版确需不同的设置放进该版布局。
- 正文：19 篇章节在 `contents/0xP0 类名/`，代码在各大类的 `code/`，图片在 `figures/`；章节文件只含正文。
- 导言区：各版参数在 `layout-<版本>.tex`，三版共用的实现在 `preamble/shared/`，四个自定义接口在 `mystyle.tex`。
- 不创建 `setup.tex`、合并各版参数的 `layout-common.tex`、`contents/chapters.tex`、`contents/code-index.tex` 或顶层的 `tests/` 目录（工具测试在 `scripts/tests/`，样张在 `preamble/tests/`），也不加 `\InputChapter` 之类的封装；`contents/` 下不建 README 等说明文件。
- 从根目录编译，路径一律相对项目根目录；保留真实文件名，包括中文、空格与大小写。
- 产物在被 Git 忽略的 `build/<版本>/`；PDF 由用户提交后自行编译，发布到 GitHub Release。

## 任务导航

| 要改的内容 | 先读 |
| --- | --- |
| `contents/` 中的正文、代码或图片 | `WRITING.md` |
| `preamble/` 中的排版 | `preamble/AGENTS.md`、`preamble/README.md`；改 `shared/` 另读 `preamble/shared/README.md` |
| 样张与 PDF 检查 | `preamble/tests/README.md` 及对应组的 README |
| 构建、生成与检查脚本 | `scripts/README.md` |
| 扉页配图、项目内字体 | `assets/README.md`、`preamble/fonts/README.md` |

## 验证入口

- `scripts/check.sh`：单元测试、入口一致性、代码版入口是否最新、文档检查，约 1 秒；每次改动后运行。
- `scripts/check.sh --full`：另编译四组样张并运行全部样张 PDF 检查，约 2 分钟；不重建三版整书。
- `./run.sh [portrait|landscape|code|all]`：构建整书，默认竖版；结束时打印末轮警告汇总。判断排版改动的影响时，与同一提交上改动前的构建对照，见 `scripts/README.md`。
- `python3 scripts/check-full.py [PDF]`：检查横版、代码版整书的越栏；返回 0 也可能带有警告。
- 不用根目录单轮 XeLaTeX 代替脚本，以免污染根目录或留下未收敛的产物。依赖 XeLaTeX 与 `latexminted`，不开启不受限 shell escape。
- 用户的终端是 UTF-8 区域设置，脚本由 macOS 自带的 bash 3.2 执行；agent 的终端若是 C 区域设置，验证时加 `LC_ALL=zh_CN.UTF-8`。
- 编译通过不等于验收通过，还要检查 PDF 的标题、颜色范围、缺字、溢出、代码内容与跨页。汇报时分清已完成、未实现、未验证。

## 维护约定

- 归属：全局规则写在这里，排版规则写在 `preamble/AGENTS.md`，正文写法写在 `WRITING.md`；现状、用法、设计决定与理由写在对应目录的 README；只关乎某几行代码的原因写成注释；过程留给 Git 历史。其他地方只放链接，不复述。
- 原位更新：决定变了就改原句，删除失效的说法；不在文末追加“某某调整（日期）”。
- 按影响更新：接口、命令、目录职责或长期约束变化时才改文档；普通修复不留完成记录。
- 设计决定标明“用户确认”并附一句理由；有参考价值的否决方案写一句。精简文档时不得丢失用户的决定，也不得降低验收要求。
- 验证状态写在被验证对象的 README，只留最新一条：日期、基于的提交、工作区有无未提交修改、运行的命令、自动检查范围、人工查看范围、未验证的部分。此后相关文件再改动，即视为不覆盖新改动。
- 不用“本轮、本次、当时、仍为”等相对说法，需要时写绝对日期。
- 体量：本文件不超过 8 KiB；本文件加任一子目录的 AGENTS.md 不超过 32 KiB（Codex 默认只自动载入合计前 32 KiB）。由 `scripts/check.sh` 检查。
- 除 `contents/`、Git 元数据、缓存与构建目录外，每个子目录都有 README，说明用途、主要文件与约束。
