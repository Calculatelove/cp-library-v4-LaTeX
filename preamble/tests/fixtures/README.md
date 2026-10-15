# 共用测试资源

本目录存放导言区效果检验使用的资源，不属于算法笔记正文，也不要求代码片段可独立运行。

| 文件 | 用途 |
| --- | --- |
| `示例 文件_1.cpp` | 中文、空格、下划线路径，默认及显式代码标题，C++ 高亮。 |
| `sample.py` | Python 高亮与按语言配置字号。 |
| `sample.sh` | Bash 高亮。 |
| `Makefile test` | 含空格路径与 Makefile 高亮。 |
| `long-code.cpp` | 长代码跨页，确认续页不重复标题。 |

所有引用使用项目根目录相对路径，例如 `preamble/tests/fixtures/示例 文件_1.cpp`。保留文件真实名称和代码内容；不要在这里写入 PDF、日志或缓存。现由 `mystyle/` 检验引用，后续布局样张可复用；共用样张内容确有需要时再添加。

`landscape-long.cpp` 为横版新增的人工长代码资源，含 100 个不同编号的声明，用于核对单个卡片跨栏、跨页的顺序和完整性；不是算法模板。

竖版扉页样张 `portrait/titlepage.tex` 使用以下资源（2026-10-15）：

| 文件 | 用途 |
| --- | --- |
| `titlepage-special.commit` | 模拟 `scripts/commit-info.sh` 的四行输出；提交说明含 `\ { } $ & # ^ _ % ~`、`^^41`、`--` 及中文引号、破折号，状态 clean。 |
| `titlepage-long-dirty.commit` | 中西文混排的超长提交说明，检验居中换行与底边对齐；状态 dirty。 |
| `titlepage-wide.png`、`titlepage-tall.png` | 800 × 300 与 300 × 800 像素的人工配图（ImageMagick 生成），分别检验配图区域的宽度与高度约束。 |

横版、代码版扉页样张 `landscape/titlepage.tex`、`code/titlepage.tex` 复用上表资源（2026-10-15）；两版配图区域为 110 × 70 mm，宽、高约束同样分别由两张人工配图检验。

`.commit` 文件逐行原样读取，修改时保持四行结构，不要加入 TeX 转义。
