# cp-library-v4-LaTeX

C.L. 的算法竞赛第四版笔记 LaTeX 版本。旨在分享本人整理的算法竞赛知识体系与模版，发挥一点余热。

- **[在线阅读](https://calculatelove.github.io/cp-library-v4-LaTeX/) · [下载 PDF](https://github.com/Calculatelove/cp-library-v4-LaTeX/releases/latest)**
- **以 “结论” 与 “Trick” 为主**。笔记中的内容经过了一定程度的抽象化：
  - 适合✅：给读者一个知识体系与代码模版的参考。
  - 适合✅：让读者简单检索知识点，了解算法竞赛中出现过某些技术。
  - 不适合❌：让读者从 0 开始学习一个知识点。
- 本人 ACM 时期在队内负责 **“0x40 数据结构”、“0x20 字符串”、“0x30 数学”**，这三部分的知识点会比其他部分更有价值。
- 本笔记的知识体系与代码模板 99.9% 由本人生成或者由本人蒸馏生成，排版部分与 AI 协作完成。
- 本笔记由 markdown 版本迁移而来，因而有部分 markdown 的习惯残留。
- ~~本笔记还有很多部分没有写完~~。

## PDF 版本说明

本项目的 PDF 有三个版本：

| 版本                                                         | 版式                       | 适用     | 打印          |
| ------------------------------------------------------------ | -------------------------- | -------- | ------------- |
| 竖版（[main-portrait.pdf](https://calculatelove.github.io/cp-library-v4-LaTeX/main-portrait.pdf)） | 完整正文，A4 纵向单栏      | 日常阅读 | 装订成册      |
| 横版（[main-landscape.pdf](https://calculatelove.github.io/cp-library-v4-LaTeX/main-landscape.pdf)） | 完整正文，A4 横向双栏      | 快速查阅 | 轻量化打印    |
| 代码版（[main-code.pdf](https://calculatelove.github.io/cp-library-v4-LaTeX/main-code.pdf)） | 仅收录代码模版，版式同横版 |          | XCPC 赛前应急 |

- 在线阅读与下载链接都对应最新的 Release，**可能晚于仓库中的源码**；历史版本见 [Releases](https://github.com/Calculatelove/cp-library-v4-LaTeX/releases)。PDF 扉页底部印有这份 PDF 所基于的 commit 信息，点击其中的哈希值可以在 GitHub 上查看该提交，据此判断手中的 PDF 是否最新。
- 在线阅读在电脑浏览器中内嵌浏览器自带的 PDF 阅读器，可在顶栏切换三个版本；在手机、平板等触屏设备上改为直接打开 PDF。
- **横版打印的时候请留意一下打印选项，确认正反面朝向符合阅读习惯**，建议先打印 1~2 页核对一下。

## 正文结构

正文位于目录 `contents/` 之中。

[0x10 基础](/contents/0x10%20基础/) · [0x20 字符串](/contents/0x20%20字符串/) · [0x30 数学](/contents/0x30%20数学/) · [0x40 数据结构](/contents/0x40%20数据结构/) · [0x50 动态规划](/contents/0x50%20动态规划/) · [0x60 图论](/contents/0x60%20图论/) · [0x70 计算几何](/contents/0x70%20计算几何/)

章节按 `0xPQ` 编号，其中 `0xP0` 是大类，`0xPQ` 是对应大类之下的章节。只有 `0x34` 内容较多，继续细分了四章。

章节文件保存知识点讲解与代码引用。独立的代码文件放在所属大类的 `code/` 中，图片放在所属大类的 `figures/` 中，需要时再引用。部分代码片段直接写在章节文件里。代码是笔记的一部分，不一定能单独编译，使用时需要结合上下文。

## 项目本地构建

如果想阅读本项目最新源码对应的 PDF，或者修改后自行生成 PDF，可以在本地构建。需要准备：

- **TeX Live**（macOS 上即 [MacTeX](https://www.tug.org/mactex/)）。代码高亮由 minted 宏包自带的 `latexminted` 完成，构建时不开启 `-shell-escape`，TeX Live 2025 起默认允许 `latexminted` 在受限模式下运行，更早的版本可能需要先升级。
- **Python 3.8 及以上**：`latexminted` 本身是 Python 程序。
- **字体**：
  - 中文：宋体 Songti SC 与苹方 PingFang SC。
  - 代码字体：[Maple Mono NF CN](https://github.com/subframe7536/maple-font/releases)。
  - 其余字体随 TeX Live 或本仓库提供。

请确保终端中能运行 `xelatex`、`latexminted`、`python3`，然后在项目根目录运行：

```sh
./run.sh             # 构建竖版（默认）
./run.sh landscape   # 构建横版
./run.sh code        # 生成 main-code.tex 并构建代码版
./run.sh all         # 依次构建三个版本
```

生成的 PDF 位于 `build/` 顶层，文件名为 `main-portrait.pdf`、`main-landscape.pdf`、`main-code.pdf`。

- 整书存在已知的 Overfull、Underfull 等排版警告，不影响生成 PDF。
- 扉页的 commit 信息取自本地 Git 仓库。若 `build/` 以外有未提交的修改时，扉页会标注 “含未提交修改”。不在 Git 仓库中（如直接下载 ZIP）时不显示。

## 项目复用建议

本项目个人 DIY 程度较高。所以本项目更多的是提供了一个排版的思路，然后让用户自家的大模型进行制作。

如果想要沿用本项目的排版，可以从以下位置开始修改：

| 修改内容                       | 修改入口                                  |
| ------------------------------ | ----------------------------------------- |
| 书名、作者、仓库地址、扉页插图 | `main-portrait.tex`、`main-landscape.tex` |
| 正文、代码、图片               | `contents/`                               |
| 正文章节编排顺序               | `main-portrait.tex`、`main-landscape.tex` |

如果想要修改本项目的排版，可以从以下位置开始修改：

| 修改内容       | 修改入口                                                     |
| -------------- | ------------------------------------------------------------ |
| 各版的页面布局 | `preamble/layout-<版本>.tex`，用法见[排版指南](preamble/README.md) |
| 三版的共用实现 | `preamble/shared/`，见[共用实现说明](preamble/shared/README.md) |

## 致谢

本项目参考 [fstqwq/Nemesis](https://github.com/fstqwq/Nemesis) 与 [skip2004/ICPC-Templates](https://github.com/skip2004/ICPC-Templates)，同时也是我们队正式参赛使用的两份模版。

章节编号参考《算法竞赛进阶指南》，同时也是带我入门的经典好书。

在此向前辈们的付出表示感谢！
