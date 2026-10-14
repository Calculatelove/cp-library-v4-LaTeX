"""检查四、五级标题的字体、独立成行、与后文同页、竖向间距及书签；需 PyMuPDF。"""
from pathlib import Path
import fitz

root = Path(__file__).resolve().parents[3]
pdf = root / "preamble/tests/build/portrait/heading-levels.pdf"
PT = 72.27 / 72  # PDF 坐标（bp）换算为 TeX pt


def main_rows(page):
    """按基线归并文字；忽略上下标、页眉页码等小于 9.5 bp 的行。"""
    rows = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if not span["text"].strip():
                    continue
                y = span["origin"][1]
                row = next((r for r in rows if abs(r["y"] - y) < 0.6), None)
                if row is None:
                    rows.append({"y": y, "spans": [span]})
                else:
                    row["spans"].append(span)
    rows = [r for r in rows if max(s["size"] for s in r["spans"]) >= 9.5]
    for r in rows:
        r["spans"].sort(key=lambda s: s["origin"][0])
        r["text"] = "".join(s["text"] for s in r["spans"]).replace(" ", "")
    return sorted(rows, key=lambda r: r["y"])


def is_heading(row):
    """标题行内的文字全为苹方 Semibold 10.5 pt，没有同行的正文字体。"""
    spans = [s for s in row["spans"] if "Math" not in s["font"]]
    return bool(spans) and all(
        "PingFang" in s["font"] and "Semibold" in s["font"]
        and abs(s["size"] * PT - 10.5) < 0.05 for s in spans)


with fitz.open(pdf) as doc:
    pages = [main_rows(page) for page in doc]
    bookmarks = {title.replace(" ", ""): level for level, title, _ in doc.get_toc()}


def find(prefix):
    hits = [(i, j) for i, rows in enumerate(pages)
            for j, row in enumerate(rows) if row["text"].startswith(prefix)]
    assert len(hits) == 1, (prefix, hits)
    return hits[0]


def above(prefix):
    i, j = find(prefix)
    assert j > 0, prefix
    return (pages[i][j]["y"] - pages[i][j - 1]["y"]) * PT


def below(prefix):
    i, j = find(prefix)
    assert j + 1 < len(pages[i]), prefix
    return (pages[i][j + 1]["y"] - pages[i][j]["y"]) * PT


headings = [
    "四级标题：紧接三级", "四级标题：正文之间", "四级标题：后接行间公式",
    "四级标题：行间公式之后", "四级标题：引用块之后", "四级标题：后接列表",
    "四级标题：后接五级标题", "五级标题：与四级同字号", "一个用于检验四级标题换行的长标题",
    "页底四级标题：后接正文", "页底四级标题：后接行间公式",
]
for prefix in headings:
    i, j = find(prefix)
    rows = pages[i]
    assert is_heading(rows[j]), (prefix, [(s["font"], s["size"]) for s in rows[j]["spans"]])
    # 长标题的续行、紧随的五级标题同属标题；其后第一行正文或公式须与标题同页。
    k = j + 1
    while k < len(rows) and is_heading(rows[k]):
        k += 1
    assert k < len(rows), f"{prefix}: heading is separated from the following content"

# 竖向节奏（基线距）：四级标题上方 24 pt、下方 20 pt，均小于三级标题。
level4 = above("四级标题：正文之间"), below("四级标题：正文之间")
level3 = above("三级标题：正文之后"), below("三级标题：正文之后")
assert abs(level4[0] - 24) < 1 and abs(level4[1] - 20) < 1, level4
assert level3[0] > level4[0] + 1 and level3[1] > level4[1], (level3, level4)
adjacent = above("四级标题：紧接三级")
assert 15 < adjacent < level4[0], adjacent

# 页底边界：标题移到下一页页首，不留在上一页页底。
for filler, heading in (("边界一：", "页底四级标题：后接正文"),
                        ("边界二：", "页底四级标题：后接行间公式")):
    (fi, _), (hi, hj) = find(filler), find(heading)
    assert (hi, hj) == (fi + 1, 0), (heading, (fi, hi, hj))

assert bookmarks.get("四级标题：正文之间") == 4, bookmarks
assert bookmarks.get("五级标题：与四级同字号") == 5, bookmarks
print("heading-levels: level-4/5 font, own line, keep-with-next, spacing and bookmarks verified")
print(f"  level 4 above/below {level4[0]:.1f}/{level4[1]:.1f} pt, "
      f"level 3 above/below {level3[0]:.1f}/{level3[1]:.1f} pt, level 3 to 4 {adjacent:.1f} pt")
