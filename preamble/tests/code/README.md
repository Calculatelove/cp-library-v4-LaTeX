# 代码版布局检验

本目录检验 `preamble/layout-code.tex`，不引用章节。代码版布局与横版除注释外逐行相同，由 `scripts/tests/test_layouts.py` 检查，其余版式由横版样张检验，所以本目录只留扉页样张（用户确认：两版取值相同时，代码版其余样张的 PDF 与横版逐页相同，只是重复编译）。

| 样张 | 检验内容 |
| --- | --- |
| `titlepage.tex` | 内容同横版样张；前两页带版本标记，第 3 页不设版本标记 |

检查复用横版的 `check.py`，加参数 `code` 时只查扉页：断言与横版相同，另查版本标记的显示与省略；悬挂位置通过样张目视验收。

```sh
bash preamble/tests/code/run.sh
python3 preamble/tests/landscape/check.py code
```

两版取值要分开时，先为代码版加回其余样张，再删去 `scripts/tests/test_layouts.py`：横版 `quotes`、`flow`、`code-cards`、`toc-layout` 的正文都在 `../fixtures/`，每份只需加一个载入代码版布局的包装，并让 `../landscape/check.py` 加参数 `code` 时也检查它们。

编译方式、产物位置与依赖见 `../README.md`。代码版入口的生成及其测试见 `scripts/README.md`。
