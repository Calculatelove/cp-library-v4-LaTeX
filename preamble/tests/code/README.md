# 代码版布局检验

本目录检验 `preamble/layout-code.tex`，不引用章节。版式参数目前与横版相同；样张从横版选取，各自载入代码版布局。

| 样张 | 检验内容 |
| --- | --- |
| `quotes.tex` | 中文双引号随字体族切换：正文、粗斜体、嵌套恢复、三级目录、页眉、行内代码、minted、卡片标题与代码、其他标点、窄行禁则及 Unicode 书签；与双反引号写法比较字形与相对位置；正文在 `../fixtures/quotes-body.tex`，PDF 断言复用 `../pdfcheck.py` 的 `check_quotes` |
| `titlepage.tex` | 4 页，内容同横版样张；前两页带版本标记，第 3 页不设版本标记 |
| `flow.tex` | 连续章节、空标题、页顶所在章的页眉与分页边界 |
| `code-cards.tex` | 代码跨栏跨页、长文件名与内嵌代码折行、框外三位行号与空行编号 |
| `syntax-colors.tex` | 四色配色与直立的代码字体 |
| `block-spacing.tex` | 代码卡片与引用块前后、二级列表、分隔线的竖向间距 |
| `toc-layout.tex` | 双栏目录、长条目与标题组分页 |

除扉页外的样张正文与横版共用（`quotes`、`syntax-colors`、`block-spacing` 还与竖版共用），放在 `../fixtures/*-body.tex`；本目录只保留载入代码版布局的包装。检查复用横版的 `check.py`，加参数 `code`：断言与横版相同，扉页另查书名后悬挂的“（代码版）”与书名同基线、不参与居中。

```sh
bash preamble/tests/code/run.sh
python3 preamble/tests/landscape/check.py code
```

编译方式、产物位置与依赖见 `../README.md`。代码版入口的生成及其测试见 `scripts/README.md`；整书的越栏检查用 `python3 scripts/check-full.py build/code/main-code.pdf`。
