# 单色符号字体

`NotoEmoji-Regular.ttf` 是 Noto Emoji 可变字体的 `wght=400` 静态实例，保留完整字符集，供三版的 `⭐`（U+2B50）和 `🚩`（U+1F6A9）使用，映射写在 `../shared/fonts.tex`。字体通过相对项目根目录的路径加载，无需安装到系统；不要删除同目录的 `OFL-NotoEmoji.txt`（SIL OFL 1.1）。没有用彩色字体或图片替代。

## 来源与生成

下载日期：2026-10-12。

- 原始字体：https://github.com/google/fonts/blob/main/ofl/notoemoji/NotoEmoji%5Bwght%5D.ttf
- 许可：https://github.com/google/fonts/blob/main/ofl/notoemoji/OFL.txt
- 原始文件 SHA-256：`de6c18832938afc99caf132b39d6a30a19bac7f2e812e28db2535b4608d27551`
- 静态实例 SHA-256：`bb0b7c50babec65b164ff346f0a0ea1786bf306c9f08730b9410cd0237da982f`

使用 fontTools 4.60.2 生成（仅更新字体时需要，编译无需 Python）：

```python
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
font = TTFont("NotoEmoji[wght].ttf")
font = instantiateVariableFont(font, {"wght": 400}, inplace=True)
font.save("NotoEmoji-Regular.ttf")
```

## 使用方式

静态实例避免依赖 XeLaTeX 对可变字重的选择。常规、粗体、斜体、粗斜体都绑定这个文件，符号随字号缩放，继承文字颜色。目前只映射上述两个单码位，不承诺支持复合 emoji、变体选择符，或 minted 代码中的 emoji。更新字体后，须重新核对字形覆盖、PDF 嵌入与文字提取。

Noto Emoji 的空格字形过宽，不能直接用作中文与符号之间的间隔。`../shared/fonts.tex` 在符号命令内部设置 CJKecglue，避免切换字体时出现宽空白。
