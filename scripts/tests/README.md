# 脚本的单元测试

本目录存放 `scripts/` 中各工具的单元测试，以及入口与布局的一致性检查。导言区样张及其 PDF 检查在 `preamble/tests/`，不放在这里。

| 文件 | 测试对象 |
| --- | --- |
| `test_generate_code.py` | `generate-code.py`：代码与标题的提取、三处模板变换、只改正文时入口不变、模板结构错误、真实入口的导言区，以及 `\TitlePageImage` 路径与 Git 中的文件名逐字一致 |
| `test_commit_info.py` | `commit-info.sh`：在临时仓库中检查非仓库与无提交时不输出、提交时区、特殊字符原样输出、只改 `build/` 的提交，以及 `build/` 内外的修改与未跟踪文件 |
| `test_check_full.py` | `check-full.py`：用构造的数据检查分栏、越界判定、扉页识别、扉页提交的读取与几何自检；未安装 PyMuPDF 时跳过 |
| `test_compare_pdf.py` | `compare-pdf.py`：用构造的数据检查完全相同，字体、颜色与位置变化的汇总，文字不同时按字符对齐，以及页数、链接与书签的差异；基线清单含三版整书与确有源码的样张；未安装 PyMuPDF 时跳过 |
| `test_check_docs.py` | `check-docs.py`：在临时目录中检查路径解析、目录 README、shell 变量展开与 AGENTS.md 体量 |
| `test_entries.py` | 竖版、横版两个手写入口除布局一行外逐行相同 |
| `test_layouts.py` | 代码版、横版两份布局除注释外逐行相同：整行注释与空白后的行尾注释可以不同，紧贴内容的 `%` 与空行都要一致 |

从项目根目录运行全部测试（需要 Python 3 标准库与 git）：

```sh
python3 -B -m unittest discover -s scripts/tests
```

`scripts/check.sh` 的快速检查会运行这些测试。被测脚本按本目录的上一级定位；测试不写入 `build/`，临时文件放在系统临时目录。
