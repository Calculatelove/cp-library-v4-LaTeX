#!/usr/bin/env python3
"""从横版章节清单生成代码版；仅支持本项目明确使用的 LaTeX 内容结构。"""
from pathlib import Path
import argparse
import os
import re
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
HEADINGS = {'section': 1, 'subsection': 2, 'subsubsection': 3, 'paragraph': 4, 'subparagraph': 5}


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


def generate(root):
    entry = root / 'main-landscape.tex'
    chapters = [e[1] for e in scan(entry.read_text(), entry.name)
                if e[0] == 'input' and e[1].startswith('contents/')]
    if not chapters or len(chapters) != len(set(chapters)):
        raise ValueError('章节清单为空或有重复')
    discovered = {str(p.relative_to(root)) for p in (root / 'contents').rglob('*.tex')
                  if re.match(r'0x[0-9A-Fa-f]{2}\s', p.name)}
    for path in sorted(discovered - set(chapters)):
        print('警告：横版入口未引用章节：' + path, file=sys.stderr)
    output = ['% 自动生成：python3 scripts/generate-code.py；请修改章节源文件后重新生成。',
              r'\documentclass{article}', '', r'\input{preamble/packages.tex}',
              r'\input{preamble/layout-code.tex}', r'\input{preamble/mystyle.tex}', '',
              r'\title{算法竞赛小记}', r'\author{Calculatelove}', r'\date{}', '',
              r'\begin{document}', '', r'\tableofcontents', '']
    counts, references = [], set()
    for chapter in chapters:
        stack, emitted = [], set()
        files = inline = 0
        for kind, value, raw, line in scan((root / chapter).read_text(), chapter):
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
                        output.extend([f'% 来源：{chapter}:{hline}', heading, ''])
                        emitted.add(hline)
                output.extend([f'% 来源：{chapter}:{line}', raw, ''])
            elif kind == 'input':
                raise ValueError(f'{chapter}:{line}: 不支持章节内嵌套 input')
        counts.append((chapter, files, inline))
    if not references and not any(c[2] for c in counts):
        raise ValueError('没有找到代码')
    output.append(r'\end{document}')
    unused = sorted(str(p.relative_to(root)) for p in (root / 'contents').rglob('*')
                    if p.is_file() and 'code' in p.parts and str(p.relative_to(root)) not in references)
    return '\n'.join(output) + '\n', counts, unused


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='只检查生成入口是否与源文件一致')
    args = parser.parse_args()
    try:
        result, counts, unused = generate(ROOT)
        destination = ROOT / 'main-code.tex'
        if args.check:
            if not destination.exists() or destination.read_text() != result:
                raise ValueError('main-code.tex 需要重新生成')
        elif not destination.exists() or destination.read_text() != result:
            temporary = None
            try:
                with tempfile.NamedTemporaryFile(mode='w', encoding='utf-8', dir=ROOT,
                                                 prefix='.main-code-', delete=False) as f:
                    temporary = Path(f.name)
                    f.write(result)
                temporary.chmod(0o644)
                os.replace(temporary, destination)
            finally:
                if temporary and temporary.exists(): temporary.unlink()
        for chapter, files, inline in counts:
            print(f'{Path(chapter).stem}: 文件 {files}，内嵌 {inline}')
        print(f'合计：文件 {sum(c[1] for c in counts)}，内嵌 {sum(c[2] for c in counts)}')
        for path in unused: print('未收录（正文未引用）：' + path)
    except (ValueError, OSError) as e:
        print(f'生成失败：{e}', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
