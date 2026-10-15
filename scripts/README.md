# 代码版生成脚本

`generate-code.py` 使用 Python 3 标准库，从任意工作目录运行均以项目根目录解析路径：

```sh
python3 scripts/generate-code.py
python3 scripts/generate-code.py --check
python3 -B scripts/test_generate_code.py
./run.sh code
```

章节顺序取自 `main-landscape.tex` 的 contents 引用；章内按源码顺序保留 `InputCode` 与完整 minted 环境，只输出这些代码所属的原有标题及祖先标题。无代码分支不输出。未被入口引用的编号章节会警告，未引用的 code 文件会列出但不收录。不会创建 code-index.tex，不修改章节或代码文件。

生成 `main-code.tex`，不要手工编辑它；修改源章节后重新生成。保留代码参数、语言、缩进、空行和注释，保留标题格式和可选短标题。生成入口逐项标记来源行号；其元信息固定与当前横版一致。`--check` 不写文件，入口过期返回非零。`run.sh code/all` 在入口预检前自动生成，失败则停止。

解析器针对当前项目的静态 LaTeX 写法，支持平衡花括号、注释和 minted 原样文本；不是 TeX 宏展开器。不支持宏动态生成标题/代码或条件分支选目。遇到已识别的其他代码环境、带星号标题、嵌套 input、缺失文件、参数未闭合时报告来源并停止。引入新内容语法时需扩展解析与测试，不应把复杂 TeX 当作已自动支持。

所有检查成功后才原子替换入口；失败不覆盖旧入口，相同内容不重复写入。首次核对为 79 处 InputCode、20 段 minted，数量不是永久限制。测试覆盖注释中的假命令、嵌套标题、代码内假标题、空分支裁剪、缺失文件、坏语法与真实内容顺序/逐段一致性。

## 扉页提交信息

`commit-info.sh` 只依赖 Bash 与 git，从任意工作目录运行均以项目根目录为准，结果输出到标准输出：

```sh
bash scripts/commit-info.sh
python3 -B scripts/test_commit_info.py
```

输出四行：提交日期（按提交自身时区，`YYYY-MM-DD`）、短哈希、提交说明首行、`clean` 或 `dirty`。取 `build/` 以外最后一次提交，只改构建产物的提交不计入；`build/` 以外有未提交修改（含未跟踪文件）时为 `dirty`。不在 Git 仓库中、找不到 git 或尚无提交时不输出内容，在标准错误说明原因并返回 0，扉页随之省略提交信息。根目录 `run.sh` 在每个版本编译前调用它，写入 `build/<版本>/main-<版本>.commit`，成功后随辅助文件清理；读取与排版见 `preamble/titlepage-portrait.tex`。

提交说明原样输出，不做 TeX 转义；扉页按原样逐行读取。测试在临时仓库中运行并屏蔽用户 Git 配置，覆盖非仓库、无提交、提交时区、特殊字符、只改 `build/` 的提交，以及 `build/` 内外的修改与未跟踪文件；改用本地时区、`log` 或 `status` 不排除 `build/`、忽略未跟踪文件四种错误实现均会被测试发现。
