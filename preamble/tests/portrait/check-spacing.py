"""检查竖版 block-spacing 样张：代码卡片与引用块的前后距、二级列表与分隔线的竖向间距；需要 PyMuPDF。

用法（从任意目录）：python3 preamble/tests/portrait/check-spacing.py
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdfcheck as pc  # noqa: E402

c = pc.Checker('竖版块间距')
with c.section('block-spacing：卡片、引用块、二级列表与分隔线'):
    with c.open(pc.BUILD / 'portrait/block-spacing.pdf', '请先运行 bash preamble/tests/portrait/run.sh') as doc:
        # 与 layout-portrait.tex 一致：行距 15 pt、段距 3 pt、盒前距 9.5 pt、盒后距 0 pt。
        pc.check_block_spacing(c, doc, baselineskip=15, parskip=3, box_before=9.5, box_after=0)
sys.exit(c.finish())
