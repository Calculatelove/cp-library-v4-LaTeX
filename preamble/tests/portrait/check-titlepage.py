"""检查竖版扉页的文字、字体、颜色、位置、配图区域、眉题式提交信息、未提交修改标签及页码；需 PyMuPDF。"""
from pathlib import Path
import fitz

root = Path(__file__).resolve().parents[3]
pdf = root / "preamble/tests/build/portrait/titlepage.pdf"
fixtures = root / "preamble/tests/fixtures"
MM = 72 / 25.4      # mm 换算为 PDF 坐标（bp）
PT = 72 / 72.27     # TeX pt 换算为 bp


def compact(text):
    """xeCJK 的中西文间距是胶而非空格字符，比较前去掉全部空白。"""
    return "".join(text.split())


def rows(page):
    """按基线归并文字行，返回自上而下的 [{y, spans, text}]。"""
    result = []
    for block in page.get_text("dict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if not span["text"].strip():
                    continue
                y = span["origin"][1]
                row = next((r for r in result if abs(r["y"] - y) < 0.6), None)
                if row is None:
                    result.append({"y": y, "spans": [span]})
                else:
                    row["spans"].append(span)
    for r in result:
        r["spans"].sort(key=lambda s: s["origin"][0])
        r["text"] = "".join(s["text"] for s in r["spans"])
        r["x0"] = min(s["bbox"][0] for s in r["spans"])
        r["x1"] = max(s["bbox"][2] for s in r["spans"])
        r["bottom"] = max(s["bbox"][3] for s in r["spans"])
    return sorted(result, key=lambda r: r["y"])


def subject(name):
    return (fixtures / name).read_text(encoding="utf-8").splitlines()[2]


def cjk_advances(page):
    """提交信息（小于 9 bp）中直接相邻的两个汉字之间的步进。"""
    result = []
    for block in page.get_text("rawdict")["blocks"]:
        for line in block.get("lines", []):
            for span in line["spans"]:
                if span["size"] >= 9:
                    continue
                chars = span["chars"]
                result += [(b["origin"][0] - a["origin"][0], span["size"])
                           for a, b in zip(chars, chars[1:]) if is_cjk(a["c"]) and is_cjk(b["c"])]
    return result


def is_cjk(char):
    return 0x4E00 <= ord(char) <= 0x9FFF


def hairline_frames(page):
    """0.4 pt、D1D1D6 描边的路径（未提交修改标签的圆角细框）。"""
    return [d["rect"] for d in page.get_drawings()
            if d.get("color") and all(abs(a - b / 255) < 0.005 for a, b in zip(d["color"], (209, 209, 214)))
            and abs(d.get("width", 0) - 0.4 * PT) < 0.02]


with fitz.open(pdf) as doc:
    assert doc.metadata["title"] == "算法竞赛小记", doc.metadata
    assert doc.metadata["author"] == "Calculatelove", doc.metadata
    assert len(doc) == 4, len(doc)
    pages = [rows(page) for page in doc]
    images = [[info["bbox"] for info in page.get_image_info()] for page in doc]
    advances = [cjk_advances(doc[i]) for i in range(2)]
    frames = [hairline_frames(page) for page in doc]
    width, height = doc[0].rect.width, doc[0].rect.height

cx, cy = width / 2, height / 2
stamp_south = cy + 131.5 * MM

# 标题区：三页位置一致，不随配图或提交信息变化。
expected = [("算法竞赛小记", "Semibold", 44, 0x1D1D1F, -80),
            ("Competitive Programming Library", "Regular", 15, 0x6E6E73, -66.5),
            ("Calculatelove", "Medium", 12, 0x1D1D1F, -55)]
for number in range(3):
    head = pages[number][:3]
    for row, (text, weight, size, color, offset) in zip(head, expected):
        span = row["spans"][0]
        assert row["text"] == text, (number + 1, row["text"])
        assert "PingFang" in span["font"] and weight in span["font"], (text, span["font"])
        assert abs(span["size"] - size * PT) < 0.05 and span["color"] == color, (text, span)
        assert abs(row["y"] - (cy + offset * MM)) < 0.3, (text, row["y"])
        assert abs((row["x0"] + row["x1"]) / 2 - cx) < 0.5, (text, row["x0"], row["x1"])
    # 扉页不显示页眉页码。
    assert not any(r["text"].strip().isdigit() for r in pages[number]), number + 1

# 配图：在 130 × 110 mm 区域内等比缩放，中心位于纸张中心下方 20 mm。
for number, (w, h) in ((0, (130, 130 * 300 / 800)), (1, (110 * 300 / 800, 110))):
    assert len(images[number]) == 1, images[number]
    x0, y0, x1, y1 = images[number][0]
    assert abs((x1 - x0) - w * MM) < 0.5 and abs((y1 - y0) - h * MM) < 0.5, (number + 1, w, h)
    assert abs((x0 + x1) / 2 - cx) < 0.5 and abs((y0 + y1) / 2 - (cy + 20 * MM)) < 0.5
    stamp_top = pages[number][3]["y"] - 6.5 * PT
    assert pages[number][2]["y"] < y0 and y1 < stamp_top, (number + 1, y0, y1, stamp_top)
assert images[2] == [], images[2]

# 眉题式提交信息：眉题、日期与哈希、提交说明各占一行，不使用“·”等分隔符。
for number, (date, digest, dirty) in enumerate((("2026-10-15", "0123abc", False),
                                               ("2026-10-15", "abcdef0", True))):
    eyebrow, ident = pages[number][3], pages[number][4]
    span = eyebrow["spans"][0]
    assert compact(eyebrow["text"]) == "LASTCOMMIT", eyebrow["text"]
    assert "PingFang" in span["font"] and "Medium" in span["font"], span["font"]
    assert abs(span["size"] - 6.5 * PT) < 0.05 and span["color"] == 0x6E6E73, span
    assert abs((eyebrow["x0"] + eyebrow["x1"]) / 2 - cx) < 0.5, (eyebrow["x0"], eyebrow["x1"])
    assert compact(ident["text"]) == date + digest + ("含未提交修改" if dirty else ""), ident["text"]
    code = [s for s in ident["spans"] if s["text"].strip() in (date, digest)]
    assert len(code) == 2 and all("MapleMono" in s["font"] for s in code), code
    assert code[1]["color"] == 0x506B82, code[1]["color"]
    assert not any("·" in r["text"] for r in pages[number][3:]), [r["text"] for r in pages[number]]
    if dirty:
        # 未提交修改：深色 6.5 pt 文字，外有一个 0.4 pt 浅灰细框；连同细框整行居中。
        tag = next(s for s in ident["spans"] if "含未提交修改" in s["text"])
        assert tag["color"] == 0x1D1D1F and abs(tag["size"] - 6.5 * PT) < 0.05, tag
        assert len(frames[number]) == 1, frames[number]
        frame = frames[number][0]
        assert frame.x0 < tag["bbox"][0] and tag["bbox"][2] < frame.x1, (frame, tag["bbox"])
        assert frame.y0 < tag["origin"][1] < frame.y1, (frame, tag["origin"])
        assert abs((code[0]["bbox"][0] + frame.x1) / 2 - cx) < 0.5, (code[0]["bbox"], frame)
    else:
        assert frames[number] == [], frames[number]
        assert abs((ident["x0"] + ident["x1"]) / 2 - cx) < 0.5, (ident["x0"], ident["x1"])

# 第 1 页：特殊字符原样输出（`--` 不被替换为连接号），提交说明为苹方。
second = pages[0][5]
assert compact(second["text"]) == compact(subject("titlepage-special.commit")), second["text"]
assert "--" in second["text"] and "–" not in second["text"], second["text"]
assert all("PingFang" in s["font"] for s in second["spans"]), second["spans"]
assert len(pages[0]) == 6, [r["text"] for r in pages[0]]

# 第 2 页：超长说明居中换行，整体向上增长、底边不变。
rest = pages[1][5:]
assert len(rest) >= 2, [r["text"] for r in rest]
assert compact("".join(r["text"] for r in rest)) == compact(subject("titlepage-long-dirty.commit"))
assert all(abs((r["x0"] + r["x1"]) / 2 - cx) < 1 for r in rest), [(r["x0"], r["x1"]) for r in rest]
assert pages[1][3]["y"] < pages[0][3]["y"], (pages[1][3]["y"], pages[0][3]["y"])

# 居中不拉开字距：汉字步进等于字号（短行也不把 xeCJK 字间胶撑开）。
for number in range(2):
    assert advances[number], number + 1
    assert all(abs(step - size) < 0.1 for step, size in advances[number]), (number + 1, advances[number])

# 提交信息贴近底边：末行基线位于底边以上 3 bp 内，且不进入 15 mm 下边距。
for number in range(2):
    last = pages[number][-1]
    assert stamp_south - 3 < last["y"] <= stamp_south, (number + 1, last["y"], stamp_south)
    assert last["bottom"] <= height - 15 * MM, (number + 1, last["bottom"])

# 第 3 页：提交信息文件不存在时只显示标题区。
assert [r["text"] for r in pages[2]] == [text for text, *_ in expected], pages[2]

# 第 4 页：扉页之后的正文页照常显示页码。
assert any(r["text"] == "4" and r["y"] > height - 20 * MM for r in pages[3]), pages[3]
print("titlepage: title block, image area, eyebrow stamp, raw commit text, dirty tag, wrapping and page numbers verified")
