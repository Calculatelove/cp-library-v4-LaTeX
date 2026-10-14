# 导言区效果检验

本目录仅测试 `preamble/` 中的接口和布局，不放置或引用 `contents/` 的章节测试。

## 组织与状态

| 目录 | 职责 | 当前状态 |
| --- | --- | --- |
| `mystyle/` | 四个自定义接口的颜色、标题、路径、多语言及跨页行为 | 已搬迁五个检验文件，运行方法见其 README。 |
| `portrait/` | 竖版字体、边距、标题、目录、页码及接口组合效果 | 已实现综合、分页、单色符号样张和两份数学字体对照；运行 `portrait/run.sh`，见其 README。 |
| `landscape/` | 横版分栏、连续章节、页眉、目录和接口跨栏 | 已实现七份样张、样张 PDF 检查与完整横版越栏检查 `check-full.py`；运行 `landscape/run.sh`，见其 README。 |
| `code/` | 代码版标题层级、代码密度、长行与跨页效果 | 规划中，布局实现时再创建目录、README 和样张。 |
| `fixtures/` | 共用代码资源；以后可放共用样张内容 | 保留现有五个资源；新增横版人工长代码资源检验连续跨栏。 |
| `build/` | 按 `mystyle/`、`portrait/`、`landscape/`、`code/` 隔离生成产物 | 已被 Git 忽略，不维护 README。 |

版式检验可引用 `fixtures/` 中的共同样张以比较效果，代码版可增加密集代码样例。接口检验不替代各版布局验收。暂不创建空布局测试。

## 路径与运行规则

所有检验均从项目根目录编译；章节、宏包配置和测试资源路径不随测试源码目录改变。源码位于对应类别目录，PDF、日志和 minted 缓存统一输出至 `preamble/tests/build/<类别>/`，不得在源码目录生成产物。

现有检验依赖 XeLaTeX、项目宏包、TeX Live Fandol 字体，代码检验另需可用的 `latexminted`。不默认开启不受限 shell escape；测试字体不决定最终字体。

运行全部现有接口检验（每个两轮）：

```sh
mkdir -p preamble/tests/build/mystyle
for test in highlight input-code input-code-pages quoteblock separator; do
    for pass in 1 2; do
        xelatex -interaction=nonstopmode -halt-on-error \
            -output-directory=preamble/tests/build/mystyle \
            "preamble/tests/mystyle/$test.tex" || exit 1
    done
done
```

详细检查项见 `mystyle/README.md`。编译成功后仍需检查 PDF 的内容、颜色、缺字、溢出及跨页，历史结果不作为新实现的验证证据。旧 `build/` 顶层产物不代表新目录中的检验结果。

## 与三版构建的关系

根目录 `run.sh` 只构建三版主文档，不运行这些检验；主文档产物在根目录 `build/<版本>/`。本目录使用独立的 `preamble/tests/build/`，清理范围互不影响。

纵向版检验（2026-10-12）：三份样张编译收敛，综合样张 6 页、两份数学样张各 1 页；全部 8 页已渲染检查。既有五个接口检验重新两轮编译通过。完整笔记尚未验证。

InputCode 卡片样式与语言图标的纵向检验见 `portrait/code-cards.tex`，由 `portrait/run.sh` 一同编译。公共 `mystyle.tex` 使用 Maple Mono NF CN 的 Nerd Font 字形，因此独立接口检验也需要该字体。
