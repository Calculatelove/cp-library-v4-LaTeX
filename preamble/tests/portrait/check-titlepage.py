"""检查竖版扉页的文字、字体、颜色、位置、配图区域、眉题式提交信息、未提交修改标签及页码；需要 PyMuPDF。

用法（从任意目录）：python3 preamble/tests/portrait/check-titlepage.py
横版、代码版扉页的检查在 preamble/tests/landscape/check-titlepage.py。
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdfcheck as pc  # noqa: E402
from pdfcheck import compact, mm, pt  # noqa: E402

c = pc.Checker('竖版扉页')
EXPECTED = [('算法竞赛小记', 'Semibold', 44, 0x1D1D1F, -80),
            ('Competitive Programming Library', 'Regular', 15, 0x6E6E73, -66.5),
            ('Calculatelove', 'Medium', 12, 0x1D1D1F, -55)]

pages = []
with c.section('读取样张'):
    with c.open(pc.BUILD / 'portrait/titlepage.pdf', '请先运行 bash preamble/tests/portrait/run.sh') as doc:
        c.check(doc.metadata['title'] == '算法竞赛小记', 'PDF 文档属性中的标题', doc.metadata['title'])
        c.check(doc.metadata['author'] == 'Calculatelove', 'PDF 文档属性中的作者', doc.metadata['author'])
        c.require(len(doc) == 4, '样张应为 4 页', len(doc))
        pages = [pc.text_rows(page) for page in doc]
        images = [[info['bbox'] for info in page.get_image_info()] for page in doc]
        advances = [pc.cjk_advances(doc[i]) for i in range(2)]
        frames = [pc.hairline_frames(page) for page in doc]
        width, height = doc[0].rect.width, doc[0].rect.height
if not pages:
    sys.exit(c.finish())

cx, cy = width / 2, height / 2
stamp_south = cy + mm(131.5)

with c.section('标题区'):
    # 三页位置一致，不随配图或提交信息变化；扉页不显示页眉页码。
    for number in range(3):
        head = pages[number][:3]
        c.require(len(head) == 3, f'第 {number + 1} 页应有三行标题区', [r['text'] for r in head])
        for row, (text, weight, size, color, offset) in zip(head, EXPECTED):
            span = row['spans'][0]
            c.check(row['text'] == text, f'第 {number + 1} 页标题区文字应为“{text}”', row['text'])
            c.check('PingFang' in span['font'] and weight in span['font'], f'“{text}”应为苹方 {weight}', span['font'])
            c.check(abs(span['size'] - pt(size)) < 0.05 and span['color'] == color, f'“{text}”的字号与颜色',
                    round(span['size'], 2), f"{span['color']:06X}")
            c.check(abs(row['y'] - (cy + mm(offset))) < 0.3, f'“{text}”的基线位置', row['y'])
            c.check(abs((row['x0'] + row['x1']) / 2 - cx) < 0.5, f'“{text}”应水平居中', row['x0'], row['x1'])
        c.check(not any(r['text'].strip().isdigit() for r in pages[number]), f'第 {number + 1} 页不应显示页码')

with c.section('配图区域'):
    # 在 130 × 110 mm 区域内等比缩放，中心位于纸张中心下方 20 mm。
    for number, (w, h) in ((0, (130, 130 * 300 / 800)), (1, (110 * 300 / 800, 110))):
        if not c.check(len(images[number]) == 1, f'第 {number + 1} 页应有一张配图', images[number]):
            continue
        x0, y0, x1, y1 = images[number][0]
        c.check(abs((x1 - x0) - mm(w)) < 0.5 and abs((y1 - y0) - mm(h)) < 0.5, f'第 {number + 1} 页配图尺寸',
                (x1 - x0, y1 - y0))
        c.check(abs((x0 + x1) / 2 - cx) < 0.5 and abs((y0 + y1) / 2 - (cy + mm(20))) < 0.5,
                f'第 {number + 1} 页配图中心', ((x0 + x1) / 2, (y0 + y1) / 2))
        stamp_top = pages[number][3]['y'] - pt(6.5)
        c.check(pages[number][2]['y'] < y0 and y1 < stamp_top, f'第 {number + 1} 页配图不应与标题区、提交信息重叠',
                (y0, y1, stamp_top))
    c.check(images[2] == [], '第 3 页不应有配图', images[2])

with c.section('眉题式提交信息'):
    # 眉题、日期与哈希、提交说明各占一行，不使用“·”等分隔符。
    for number, (date, digest, dirty) in enumerate((('2026-10-15', '0123abc', False),
                                                   ('2026-10-15', 'abcdef0', True))):
        eyebrow, ident = pages[number][3], pages[number][4]
        span = eyebrow['spans'][0]
        c.check(compact(eyebrow['text']) == 'LASTCOMMIT', f'第 {number + 1} 页眉题文字', eyebrow['text'])
        c.check('PingFang' in span['font'] and 'Medium' in span['font'], '眉题应为苹方 Medium', span['font'])
        c.check(abs(span['size'] - pt(6.5)) < 0.05 and span['color'] == 0x6E6E73, '眉题的字号与颜色',
                round(span['size'], 2), f"{span['color']:06X}")
        c.check(abs((eyebrow['x0'] + eyebrow['x1']) / 2 - cx) < 0.5, '眉题应水平居中', eyebrow['x0'], eyebrow['x1'])
        c.check(compact(ident['text']) == date + digest + ('含未提交修改' if dirty else ''),
                f'第 {number + 1} 页日期与哈希行', ident['text'])
        code = [s for s in ident['spans'] if s['text'].strip() in (date, digest)]
        c.check(len(code) == 2 and all('MapleMono' in s['font'] for s in code), '日期与哈希应为 Maple Mono',
                [(s['text'], s['font']) for s in code])
        c.check(len(code) == 2 and code[1]['color'] == 0x506B82, '哈希应为灰蓝色',
                [f"{s['color']:06X}" for s in code])
        c.check(not any('·' in r['text'] for r in pages[number][3:]), '提交信息不应使用“·”分隔',
                [r['text'] for r in pages[number]])
        if dirty:
            # 未提交修改：深色 6.5 pt 文字，外有一个 0.4 pt 浅灰细框；连同细框整行居中。
            tag = next((s for s in ident['spans'] if '含未提交修改' in s['text']), None)
            c.require(tag is not None, f'第 {number + 1} 页应有“含未提交修改”标签')
            c.check(tag['color'] == 0x1D1D1F and abs(tag['size'] - pt(6.5)) < 0.05, '标签文字的颜色与字号',
                    f"{tag['color']:06X}", round(tag['size'], 2))
            c.require(len(frames[number]) == 1, '标签外应有一个细框', frames[number])
            frame = frames[number][0]
            c.check(frame.x0 < tag['bbox'][0] and tag['bbox'][2] < frame.x1, '细框应在水平方向包住标签文字',
                    frame, tag['bbox'])
            c.check(frame.y0 < tag['origin'][1] < frame.y1, '细框应在竖直方向包住标签基线', frame, tag['origin'])
            c.check(len(code) == 2 and abs((code[0]['bbox'][0] + frame.x1) / 2 - cx) < 0.5, '连同细框整行应居中',
                    frame)
        else:
            c.check(frames[number] == [], '干净状态不应有细框', frames[number])
            c.check(abs((ident['x0'] + ident['x1']) / 2 - cx) < 0.5, '日期与哈希行应水平居中',
                    ident['x0'], ident['x1'])

with c.section('提交说明原样输出与换行'):
    # 第 1 页：特殊字符原样输出（`--` 不被替换为连接号），提交说明为苹方。
    second = pages[0][5]
    c.check(compact(second['text']) == compact(pc.commit_subject('titlepage-special.commit')),
            '第 1 页提交说明应原样输出', second['text'])
    c.check('--' in second['text'] and '–' not in second['text'], '`--` 不应被替换为连接号', second['text'])
    c.check(all('PingFang' in s['font'] for s in second['spans']), '提交说明应为苹方',
            [s['font'] for s in second['spans']])
    c.check(len(pages[0]) == 6, '第 1 页应共 6 行', [r['text'] for r in pages[0]])
    # 第 2 页：超长说明居中换行，整体向上增长、底边不变。
    rest = pages[1][5:]
    c.check(len(rest) >= 2, '第 2 页超长说明应换行', [r['text'] for r in rest])
    c.check(compact(''.join(r['text'] for r in rest)) == compact(pc.commit_subject('titlepage-long-dirty.commit')),
            '第 2 页提交说明应完整')
    c.check(all(abs((r['x0'] + r['x1']) / 2 - cx) < 1 for r in rest), '换行后每行都应居中',
            [(r['x0'], r['x1']) for r in rest])
    c.check(pages[1][3]['y'] < pages[0][3]['y'], '超长说明应使提交信息整体向上增长',
            pages[1][3]['y'], pages[0][3]['y'])

with c.section('字距与底边'):
    # 居中不拉开字距：汉字步进等于字号（短行也不把 xeCJK 字间胶撑开）。
    for number in range(2):
        c.check(advances[number], f'第 {number + 1} 页应找到相邻汉字')
        c.check(all(abs(step - size) < 0.1 for step, size in advances[number]),
                f'第 {number + 1} 页居中不应拉开字距', advances[number][:5])
    # 提交信息贴近底边：末行基线位于底边以上 3 bp 内，且不进入 15 mm 下边距。
    for number in range(2):
        last = pages[number][-1]
        c.check(stamp_south - 3 < last['y'] <= stamp_south, f'第 {number + 1} 页提交信息末行应贴近底边',
                last['y'], stamp_south)
        c.check(last['bottom'] <= height - mm(15), f'第 {number + 1} 页提交信息不应进入 15 mm 下边距',
                last['bottom'])

with c.section('无提交信息与正文页'):
    c.check([r['text'] for r in pages[2]] == [text for text, *_ in EXPECTED], '第 3 页只应显示标题区',
            [r['text'] for r in pages[2]])
    c.check(any(r['text'] == '4' and r['y'] > height - mm(20) for r in pages[3]), '第 4 页应显示页码 4',
            [r['text'] for r in pages[3]])

sys.exit(c.finish())
