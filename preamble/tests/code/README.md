# 代码版布局检验

本目录检验 `preamble/layout-code.tex`，不引用章节。版式参数目前与横版相同；样张从横版选取，各自载入代码版布局。

| 样张 | 检验内容 |
| --- | --- |
| `titlepage.tex` | 4 页，内容同横版样张；前两页带版本标记，第 3 页不设版本标记 |
| `flow.tex` | 连续章节、空标题、页顶所在章的页眉与分页边界 |
| `code-cards.tex` | 代码跨栏跨页、长文件名与内嵌代码折行 |
| `syntax-colors.tex` | 四色配色与直立的代码字体 |
| `toc-layout.tex` | 双栏目录、长条目与标题组分页 |

后四份的正文与横版共用（`syntax-colors` 还与竖版共用），放在 `../fixtures/*-body.tex`；本目录只保留载入代码版布局的包装。检查复用横版的脚本，加参数 `code`：`check-layout.py code` 检查后四份，断言与横版相同；`check-titlepage.py code` 检查扉页，另查书名后悬挂的“（代码版）”与书名同基线、不参与居中。

```sh
bash preamble/tests/code/run.sh
python3 preamble/tests/landscape/check-layout.py code
python3 preamble/tests/landscape/check-titlepage.py code
```

编译方式、产物位置与依赖见 `../README.md`。代码版入口的生成及其测试见 `scripts/README.md`；整书的越栏检查用 `python3 scripts/check-full.py build/code/main-code.pdf`。
