#!/usr/bin/env bash
# 从项目根目录或任意目录运行；各样张最多八轮，直至辅助文件收敛。
set -euo pipefail
cd "$(dirname "$0")/../../.."
out=preamble/tests/build/landscape
mkdir -p "$out"
if (( $# == 0 )); then
    set -- titlepage flow preview code-cards syntax-colors interfaces toc-layout images
fi
for test in "$@"; do
    previous=''
    converged=false
    for pass in 1 2 3 4 5 6 7 8; do
        if ! xelatex -interaction=nonstopmode -halt-on-error \
            -output-directory="$out" "preamble/tests/landscape/$test.tex" \
            > "$out/$test-console.txt" 2>&1; then
            tail -40 "$out/$test-console.txt"
            exit 1
        fi
        current=$(for ext in aux toc out lof lot; do
            if [[ -f "$out/$test.$ext" ]]; then cksum "$out/$test.$ext"; fi
        done)
        if [[ "$pass" -ge 2 && "$current" == "$previous" ]] &&
            ! grep -Eq 'Rerun to get|Rerun LaTeX|Label\(s\) may have changed' "$out/$test.log"; then
            converged=true
            break
        fi
        previous=$current
    done
    if [[ "$converged" != true ]]; then
        echo "$test: eight passes without convergence" >&2
        exit 1
    fi
    if grep -Eq 'Missing character:|Overfull|Font shape .*undefined|Some font shapes were not available|headheight is too small' "$out/$test.log"; then
        echo "$test: missing glyph, overflow or font substitution; inspect $out/$test.log" >&2
        exit 1
    fi
    echo "$test: converged in $pass passes"
done
