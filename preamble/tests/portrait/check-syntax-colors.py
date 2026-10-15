"""检查竖版代码配色与卡片：只用四种配色、常规直立字形；需要 PyMuPDF。

用法（从任意目录）：python3 preamble/tests/portrait/check-syntax-colors.py
横版、代码版的同类检查在 preamble/tests/landscape/check-layout.py。
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pdfcheck as pc  # noqa: E402

c = pc.Checker('竖版代码配色')
for name in ('syntax-colors', 'code-cards'):
    with c.section(name):
        with c.open(pc.BUILD / f'portrait/{name}.pdf', '请先运行 bash preamble/tests/portrait/run.sh') as doc:
            pc.check_code_palette(c, doc, name, sample_tokens=(name == 'syntax-colors'))
sys.exit(c.finish())
