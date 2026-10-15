#!/usr/bin/env python3
"""以横版入口为模板生成代码版入口；仅支持本项目明确使用的 LaTeX 内容结构。

只做三处变换：布局一行换成代码版布局；在导言区末尾加版本标记；把每个章节引用换成该章中的代码
及其所属标题。横版入口中的其他内容（元信息、扉页、目录等）原样沿用。
"""
from pathlib import Path
import argparse
import os
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = {'section': 1, 'subsection': 2, 'subsubsection': 3, 'paragraph': 4, 'subparagraph': 5}
SOURCE = 'main-landscape.tex'
LAYOUT_LINE = r'\input{preamble/layout-landscape.tex}'
CODE_LAYOUT_LINE = r'\input{preamble/layout-code.tex}'
BEGIN_LINE = r'\begin{document}'
EDITION_LABEL = r'\EditionLabel{代码版}'
HEADER = ('% 自动生成：python3 scripts/generate-code.py，以 main-landscape.tex 为模板；'
          '请修改横版入口或章节源文件后重新生成。')


def skip(s, i):
    while i < len(s):
        if s[i].isspace():
            i += 1
        elif s[i] == '%':
            end = s.find('\n', i)
            i = len(s) if end < 0 else end + 1
        else:
            break
    return i


def group(s, i, left='{', right='}'):
    i = skip(s, i)
    if i >= len(s) or s[i] != left:
        raise ValueError('缺少参数 ' + left)
    start = i + 1
    depth, braces = 1, 0
    i += 1
    while i < len(s):
        c = s[i]
        if c == '\\':
            i += 2
            continue
        if c == '%':
            end = s.find('\n', i)
            i = len(s) if end < 0 else end + 1
            continue
        if left == '[':
            if c == '{': braces += 1
            if c == '}': braces -= 1
        if not braces:
            if c == left: depth += 1
            if c == right:
                depth -= 1
                if depth == 0:
                    return s[start:i], i + 1
        i += 1
    raise ValueError('参数未闭合 ' + left)


def optional(s, i):
    i = skip(s, i)
    return group(s, i, '[', ']')[1] if i < len(s) and s[i] == '[' else i


def scan(s, source):
    """返回标题、代码和 input；逐字符跳过注释，minted 内容不作为 TeX 解析。"""
    i = 0
    while i < len(s):
        if s[i] == '%':
            i = skip(s, i)
            continue
        if s[i] != '\\':
            i += 1
            continue
        start = i
        m = re.match(r'\\([A-Za-z]+|.)', s[i:])
        if not m:
            break
        name = m[1]
        i += len(m[0])
        line = s.count('\n', 0, start) + 1
        try:
            if name in HEADINGS:
                if s[i:i+1] == '*':
                    raise ValueError('暂不支持带星号标题')
                i = optional(s, i)
                _, i = group(s, i)
                yield ('heading', HEADINGS[name], s[start:i], line)
            elif name == 'InputCode':
                i = optional(s, i)
                _, i = group(s, i)
                path, i = group(s, i)
                yield ('file', path, s[start:i], line)
            elif name == 'begin':
                env, i = group(s, i)
                if env == 'minted':
                    i = optional(s, i)
                    _, i = group(s, i)
                    end = re.search(r'(?m)^[ \t]*\\end\{minted\}', s[i:])
                    if end is None:
                        raise ValueError('minted 未闭合')
                    i += end.end()
                    yield ('inline', None, s[start:i], line)
                elif env in ('verbatim', 'lstlisting', 'Verbatim', 'comment'):
                    raise ValueError('不支持的原样文本环境 ' + env)
            elif name == 'input':
                path, i = group(s, i)
                yield ('input', path, s[start:i], line)
            elif name in ('inputminted', 'include', 'lstinputlisting', 'verb', 'iffalse'):
                raise ValueError('不支持的内容命令 \\' + name)
        except ValueError as e:
            raise ValueError(f'{source}:{line}: {e}') from e


def chapter_code(root, chapter):
    """一章中的代码及其所属的原有标题，返回 (行列表, 引用的代码文件集合, 文件数, 内嵌数)。"""
    lines, references = [], set()
    stack, emitted = [], set()
    files = inline = 0
    for kind, value, raw, line in scan((root / chapter).read_text(encoding='utf-8'), chapter):
        if kind == 'heading':
            while stack and stack[-1][0] >= value:
                stack.pop()
            stack.append((value, line, raw))
        elif kind in ('file', 'inline'):
            if not stack or stack[0][0] != 1:
                raise ValueError(f'{chapter}:{line}: 代码缺少所属一级标题')
            if kind == 'file':
                if not (root / value).is_file():
                    raise ValueError(f'{chapter}:{line}: 代码文件不存在：{value}')
                references.add(value)
                files += 1
            else:
                inline += 1
            for level, hline, heading in stack:
                if hline not in emitted:
                    lines.extend([f'% 来源：{chapter}:{hline}', heading, ''])
                    emitted.add(hline)
            lines.extend([f'% 来源：{chapter}:{line}', raw, ''])
        elif kind == 'input':
            raise ValueError(f'{chapter}:{line}: 不支持章节内嵌套 input')
    return lines, references, files, inline


def derive(source, blocks):
    """由横版入口文本得到代码版入口：换布局一行，导言区末尾加版本标记，章节引用行换成 blocks 中的内容。"""
    out = [HEADER]
    for line in source.splitlines():
        stripped = line.strip()
        if stripped == LAYOUT_LINE:
            out.append(CODE_LAYOUT_LINE)
        elif stripped == BEGIN_LINE:
            while out and not out[-1].strip():
                out.pop()
            out.extend([EDITION_LABEL, '', line])
        elif stripped in blocks:
            out.extend(blocks[stripped])
        else:
            out.append(line)
    return re.sub(r'\n{3,}', '\n\n', '\n'.join(out).rstrip('\n') + '\n')


def generate(root):
    """返回 (代码版入口内容, 各章代码统计, 未收录的代码文件)。"""
    source = (root / SOURCE).read_text(encoding='utf-8')
    lines = [line.strip() for line in source.splitlines()]
    for marker in (LAYOUT_LINE, BEGIN_LINE):
        if lines.count(marker) != 1:
            raise ValueError(f'{SOURCE} 中应恰好有一行 {marker}')
    inputs = [(e[1], e[2]) for e in scan(source, SOURCE) if e[0] == 'input' and e[1].startswith('contents/')]
    chapters = [path for path, _ in inputs]
    if not chapters or len(chapters) != len(set(chapters)):
        raise ValueError('章节清单为空或有重复')
    for path, raw in inputs:
        if raw not in lines:
            raise ValueError(f'{SOURCE}：章节引用须单独占一行：{raw}')
    discovered = {str(p.relative_to(root)) for p in (root / 'contents').rglob('*.tex')
                  if re.match(r'0x[0-9A-Fa-f]{2}\s', p.name)}
    for path in sorted(discovered - set(chapters)):
        print('警告：横版入口未引用章节：' + path, file=sys.stderr)
    blocks, counts, references = {}, [], set()
    for path, raw in inputs:
        block, refs, files, inline = chapter_code(root, path)
        blocks[raw] = block
        references |= refs
        counts.append((path, files, inline))
    if not references and not any(c[2] for c in counts):
        raise ValueError('没有找到代码')
    unused = sorted(str(p.relative_to(root)) for p in (root / 'contents').rglob('*')
                    if p.is_file() and 'code' in p.parts and str(p.relative_to(root)) not in references)
    return derive(source, blocks), counts, unused


def replace_atomically(destination, text):
    """先写临时文件再整体替换，失败时不留下半个入口。"""
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=destination.parent,
                                         prefix=f'.{destination.stem}-', delete=False) as f:
            temporary = Path(f.name)
            f.write(text)
        temporary.chmod(0o644)
        os.replace(temporary, destination)
    finally:
        if temporary and temporary.exists():
            temporary.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='只检查 main-code.tex 是否与横版入口及章节一致，不写文件')
    args = parser.parse_args()
    try:
        result, counts, unused = generate(ROOT)
        destination = ROOT / 'main-code.tex'
        current = destination.read_text(encoding='utf-8') if destination.exists() else None
        if args.check and current != result:
            raise ValueError('main-code.tex 需要重新生成')
        if not args.check and current != result:
            replace_atomically(destination, result)
        for chapter, files, inline in counts:
            print(f'{Path(chapter).stem}: 文件 {files}，内嵌 {inline}')
        print(f'合计：文件 {sum(c[1] for c in counts)}，内嵌 {sum(c[2] for c in counts)}')
        for path in unused:
            print('未收录（正文未引用）：' + path)
    except (ValueError, OSError) as e:
        print(f'生成失败：{e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
