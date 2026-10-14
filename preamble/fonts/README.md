# 单色符号字体

`NotoEmoji-Regular.ttf` 是 Noto Emoji 可变字体的 `wght=400` 静态实例，保留完整字符集，供纵向与横向布局的 `⭐`（U+2B50）和 `🚩`（U+1F6A9）使用。字体通过相对项目根目录的路径加载，无需安装到系统；不要删除同目录的 `OFL-NotoEmoji.txt`（SIL OFL 1.1）。未使用彩色字体或图片替代。

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

静态实例避免依赖 XeLaTeX 对可变字重的选择。布局将常规、粗体、斜体、粗斜体均绑定此文件，符号随字号缩放且继承文字颜色。当前只映射上述两个单码位，不承诺复合 emoji、变体选择符或 minted 代码中的 emoji 支持。字体更新后须重新核对字形覆盖、PDF 嵌入及文字提取。

Noto Emoji 的 space 字形 advance 为 2600/2048 em；不可直接用作中文与符号的间隔。纵向与横向布局均在符号命令内部设置 0.25em 的 CJKecglue，避免字体切换造成宽空白。
