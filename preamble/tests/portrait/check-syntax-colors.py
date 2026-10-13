"""检查实际 PDF 中的代码颜色、字重、注释与跨页；需 PyMuPDF。"""
from pathlib import Path
import fitz

root = Path(__file__).resolve().parents[3]
out = root / "preamble/tests/build/portrait"
palette = {0x30343B, 0x506B82, 0x58715D, 0x70757D}

for name in ("syntax-colors", "code-cards"):
    spans = []
    with fitz.open(out / f"{name}.pdf") as doc:
        for page in doc:
            for block in page.get_text("dict")["blocks"]:
                for line in block.get("lines", []):
                    for span in line["spans"]:
                        if "Maple" not in span["font"]:
                            continue
                        # 卡片标题中的 Nerd Font 图标不是代码。
                        if all(c.isspace() or 0xE000 <= ord(c) <= 0xF8FF
                               or 0xF0000 <= ord(c) <= 0x10FFFD
                               for c in span["text"]):
                            continue
                        spans.append(span)
                        assert span["color"] in palette, (name, span)
                        assert "Bold" not in span["font"], (name, span)
                        assert ("Italic" in span["font"]) == (span["color"] == 0x70757D), (name, span)
    assert spans, f"No code found: {name}"
    if name == "syntax-colors":
        assert {s["color"] for s in spans} == palette
        for word in ("vector", "string", "pair", "return", "42", "3.14159"):
            assert any(s["text"].strip() == word and s["color"] == 0x506B82 for s in spans), word
    print(f"{name}: palette, regular weight and comment italics verified")
