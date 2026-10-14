# Landscape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 实现兼顾打印与屏幕阅读的 A4 横向双栏笔记，章节连续，页眉和目录参考竖版，暂不制作封面。

**Architecture:** 横版入口直接按用户指定顺序引入 19 篇正文；独立横版布局设置纸张、字体、标准双栏输出、页眉及目录。复用公共接口与已有测试资源，以横版样张先验证跨栏，再构建全文。

**Tech Stack:** XeLaTeX、geometry、titlesec、fancyhdr、tocloft、hyperref、minted 3.x、tcolorbox、Bash；PDF 检查使用 PyMuPDF 与现有渲染工具。

**Spec:** `docs/superpowers/specs/2026-10-14-landscape-design.md`（已批准，2026-10-14 更新为直接引入章节）。

## Global Constraints

- A4 横向，297 × 210 mm；四边 12 mm，上下包含页眉页脚；栏间距 8 mm，每栏 132.5 mm，无分隔线。
- 正文 10/14 pt；代码 9/11.5 pt；一、二、三级标题 16/21、12/17、10.5/15 pt；字体及颜色按设计稿。
- 不创建 `contents/chapters.tex`，不提取公共章节清单；`main-portrait.tex` 保持不变。
- 不修改算法正文、公式、原图片文件、代码原文件或仅代码版；用户已另行批准横版图片按栏宽显示；不新增公共布局文件和章节引入封装。
- 封面暂不设计；首轮从目录开始，目录后正文另起页，正文各章连续。
- 使用已有 `run.sh landscape` 构建全文；样张位于 `preamble/tests/landscape/`，产物位于已忽略的 `preamble/tests/build/landscape/`。
- 遵守根 AGENTS：不修改根 README、不提交或推送，不默认启用不受限 shell escape。

## Review Focus

- 从左栏底开始的长代码及引用块必须依次续入右栏、下一页，无丢行重复（任务 2）。
- 同页左右栏跨章、以及下一页开头的新章不能导致页眉提前显示下一页章节（任务 1）。
- 空标题与栏底标题后接公式或代码时，标题不能独留栏底（任务 1、2）。
- 长目录条目的链接区域及父子条目在换栏后仍有效，三级标题进入目录而四、五级只进入书签（任务 3）。
- 真实宽公式、原尺寸图片及长代码标识符在窄栏中不可裁切或侵入邻栏；不能通过改写正文掩盖问题（任务 4）。

---

## Task 1: 页面、字体、连续标题和页眉

**Files:** 修改 `preamble/layout-landscape.tex`；新增 `preamble/tests/landscape/{preview.tex,flow.tex,run.sh,README.md,check-layout.py}`；更新 `preamble/tests/README.md`。

**Interfaces:** 消费现有 `packages.tex`、`mystyle.tex`；提供可由 article 文档直接加载的横版布局。测试脚本从任何目录启动都回到根目录，至少两轮、最多八轮；PDF 检查入口为 `python3 preamble/tests/landscape/check-layout.py`，异常退出非零。

- [x] 编写独立样张：连续短章同栏、左栏旧章与右栏新章、下一页新章、连续空标题、栏底标题后接段落／公式。用虚构内容与唯一文本标记定位，不引入章节正文。
- [x] 编写几何与标题检查：PDF 宽高分别为 `297*72/25.4`、`210*72/25.4`（容差 0.1 pt）；TeX 中断言 `columnsep=8mm`、`columnwidth=132.5mm`（容差 0.01 pt）；通过 PDF 标记位置断言短章未强制换页，标题与后续首段同栏，跨章页页眉为本页最后章名（试排后用户改为页顶所在的章，断言已同步为 Alpha、Delta、Epsilon、Boundary-title）。首次运行记录空布局尚不满足的检查项。
- [x] 实现横版字体及初始化：参考当前竖版的数学兼容、Unicode 符号、Maple 字形和高亮，使用独立 `Landscape` 前缀，勿引入竖版布局文件。设置标准双栏与自然栏底，移除章前清页及章首 plain 页式逻辑；主入口文档类不增加排版选项。
- [x] 实现段落与标题：段间距 `2pt plus 1pt minus 1pt`；一级前后 10/5 pt、二级 8/4 pt、三级 6/3 pt；四、五级采用 10/14 pt 黑体加粗。保留标题后不换栏的约束；页眉沿用竖版 8/10 pt、666666，无横线，页码居中。
- [x] 建立样张运行脚本与目录说明，运行 `bash preamble/tests/landscape/run.sh` 和 PDF 检查；要求无缺字、Overfull、字体替换或页眉高度不足。逐页渲染检查样张，记录通过范围。

## Task 2: 公共接口的跨栏和代码呈现

**Files:** 新增 `preamble/tests/landscape/{code-cards.tex,syntax-colors.tex,interfaces.tex}`；扩展任务 1 的检查与运行脚本；必要的横版局部修正在 `preamble/layout-landscape.tex`。

**Interfaces:** 使用原有 `\InputCode[标题]{语言}{路径}`、`quoteblock`、`\Highlight`、`\Separator` 和直接 minted；复用 `preamble/tests/fixtures/`，不改接口参数。

- [x] 编写代码卡片样张，覆盖长标题、中文和空格路径、左栏底开始的长卡片、跨右栏到下一页、长行折行及直接 minted。用已有多语言资源；至少一次单独调用必须实际跨越左栏→右栏→下一页三个栏片，可将已有长代码资源的起点安排在左栏底部，不以多个短调用替代、不修改既有资源；新增人工长代码 `fixtures/landscape-long.cpp` 保证单次调用足够长。
- [x] 编写引用块和其他接口样张，覆盖列表、数学、多段落、跨栏、颜色作用范围和分隔线宽度；至少一个引用块用足量人工段落连续跨越三个栏片；加入标题后立即接代码卡片的场景。
- [x] 扩展 PDF 检查：按页、左栏、右栏顺序提取测试代码，与资源逐行核对（仅忽略显示折行引入的断行）；标题出现次数等于调用次数。代码排除图标后颜色仅为 `{0x30343B,0x506B82,0x58715D,0x70757D}`，无 Bold/Italic，配色样张四种颜色均出现。
- [x] 运行样张并据实际失败修复横版设置。卡片保持 2.5 mm 左右及 2 mm 上下内距、续段不重复标题、连接处直边；引用块继承 2 pt 段间距。仅在证实公共接口本身需改动时修改 `mystyle.tex`，并纳入任务 4 回归。
- [x] 重新运行横版样张与检查，渲染全部新增页，确认跨栏连接处、长行、图标、首末行和框内留白。

## Task 3: 双栏目录与书签

**Files:** 修改 `preamble/layout-landscape.tex`；新增 `preamble/tests/landscape/toc-layout.tex`；扩展运行脚本和 `check-layout.py`。

**Interfaces:** 入口仍只调用标准 `\tableofcontents`；目录居中标题跨整页，下方双栏条目，结束后正文另起页。内部目录命令采用 `Landscape` 前缀，参数结构可参考竖版 `PortraitTOCEntry`。

- [x] 编写真实目录样张：至少覆盖两页目录、三级条目、三个层级的长标题、栏底父子条目、三级组跨页边界，以及四、五级正文标题和 Unicode 标题。虚构标题与正文锚点一一对应。
- [x] 实现目录：字体 12/10.5/10 pt，行距 15 pt，缩进 0/1/2 个 10 pt 中文字宽；一级页码 11 pt，其余 10 pt；点色 888888、点距 9 pt、两端 3 pt。一级前 12 pt、后 5 pt；条目整盒、父子条目分页惩罚沿用竖版思路，宽度按当前栏计算。通栏标题的封装须在 tocloft 的文档起始初始化后生效，避免被其重定义覆盖。
- [x] 设置 `tocdepth=3`、`bookmarksdepth=5` 和全部书签展开；目录页清空章名标记，正文恢复本页最后生效的一级章名（试排后用户改为页顶所在的章，见文末）。
- [x] 扩展检查：目录标题中心等于纸张中心（容差 1 pt），长条目不越栏；父子标记在空间允许时同栏；每个内部链接目标页有效且对应标题在目标页；四、五级标题不出现在目录中但在书签中，书签默认展开。首张目录前无空白页，正文从目录之后紧接的新页左栏开始，无多余空白页。
- [x] 运行全部横版样张与 PDF 检查，逐页渲染目录样张，确认页码、长标题、点线及两栏阅读顺序。

## Task 4: 入口、全文试排与交付记录

**Files:** 修改 `main-landscape.tex`、`preamble/README.md`、`preamble/tests/README.md` 和 `preamble/tests/landscape/README.md`；更新根 `AGENTS.md` 及设计／计划状态。若任务 2 需要公共修复，只修改实际涉及的公共文件。

**Interfaces:** `./run.sh landscape` 输出 `build/landscape/main-landscape.pdf`；保留运行控制台到 `preamble/tests/build/landscape/full-build-console.txt`，因为构建脚本成功后清理日志。

- [x] 填写横版入口：`article` 无排版选项，按序加载 packages、layout-landscape、mystyle，保留书名／作者元信息，调用目录后按用户提供顺序直接写入 19 条 `\input`。无 `\maketitle`，无 `contents/chapters.tex`。
- [x] 核对章节路径列表恰为用户指定的 `0x11,0x12,0x21,0x22,0x31,0x32,0x33,0x34,0x35,0x36,0x37,0x38,0x41,0x42,0x51,0x52,0x65,0x71,0x72`，真实文件全部存在；确认竖版入口与正文／代码资源无改动。
- [x] 运行 `./run.sh landscape > preamble/tests/build/landscape/full-build-console.txt 2>&1`；验证辅助记录收敛，逐项记录最后一轮缺字、溢出、字体替换及其他警告。涉及内容保真约束的超宽项记录章节、页码和溢出量，提出具体局部方案，勿静默改写或缩放。
- [x] 检查完整 PDF 全部目录、书签及链接，定位并渲染全部新增溢出位置、跨章页、长公式／原图、代表性代码跨栏页；不将样张验证代替全文检查。另以整页适配与 100% 显示观察字号；实物打印留给实际打印验收。
- [x] 若公共文件有修改，运行 `bash preamble/tests/portrait/run.sh`、`python3 preamble/tests/portrait/check-syntax-colors.py`，按 mystyle README 编译五份独立样张，并用 `./run.sh portrait` 重建竖版；渲染受影响的对应页面。公共文件无改动时，不重复无关回归。
- [ ] 更新目录文档及 AGENTS：具体实现、构建轮数、页数、警告、已检查页面和未验收范围。运行 `git diff --check`，审查 diff 与用户改动隔离；不提交或推送。（文档已更新；`git diff --check` 待 shell 可用后运行）

## 执行方式建议与当前状态

建议在当前对话顺序实施：四项任务共同依赖同一横版布局，先稳定分栏再完成目录和全文集成，避免多人同时编辑布局。最终进行一次独立审查，重点核对跨栏、页眉及内容保真。

本计划已在当前对话顺序实施；执行记录位于 `preamble/tests/build/landscape/progress.md`（已忽略的构建目录，非长期记录）。

实施结果（2026-10-14）：任务 1—4 完成。横版样张由 `preamble/tests/landscape/run.sh` 编译，`check-layout.py` 检查通过；完整横版经 `./run.sh landscape` 三轮收敛，101 页（目录 4 页），197 个目录链接目标有效，208 个书签（一级 19、二级 90、三级 88、四级 11）默认展开。公共宏包与接口未修改，竖版入口及布局未改动，因此未重复竖版回归。

全文试排的调整：窄栏 `emergencystretch` 由 1em 增至 6em（3em 时仍有 6 条 Overfull，6em 降为 3 条），用户讨论后决定保持 6em；用户批准横版图片按栏宽解释 `textwidth`。第 96 页 exBSGS 高亮越过纸边，由用户缩短 `0x34` 两处高亮的括号说明解决；第 13、76 页右栏公式少量溢出经用户确认接受，登记于 `preamble/tests/landscape/README.md`，并新增 `check-full.py` 检查完整 PDF 的越栏。

后续调整（用户决定）：第 77 页 ρ 图改为 0.6 倍宽度，第 47 页栏底空白经用户确认不再处理；页眉改为显示页顶所在的章。用户 17:54 重建完整横版（101 页），逐页核对出现新章的页面，页眉均为页顶所在的章，目录页无页眉；`check-full.py`（pdfplumber）仅列出已接受的第 13、76 页。修改后的 `flow.tex` 与 `check-layout.py` 尚未重新运行。另删去从竖版沿用、在横版重写 `\tableofcontents` 后已不生效的 tocloft 目录标题设置，输出应不变，待下次构建确认。

尚未完成：最终独立审查、`git diff --check`、实物打印验收。
