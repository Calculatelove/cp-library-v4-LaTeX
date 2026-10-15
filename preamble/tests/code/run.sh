#!/usr/bin/env bash
# 从项目根目录或任意目录运行；不带参数时编译全部样张，也可只传入样张名。
# 每份样张由 scripts/xelatex-converge.sh 编译至收敛，并严格检查日志；产物在 preamble/tests/build/code/。
set -euo pipefail
cd "$(dirname "$0")/../../.."
if (( $# == 0 )); then
    set -- titlepage flow code-cards syntax-colors toc-layout
fi
for test in "$@"; do
    bash scripts/xelatex-converge.sh --quiet --strict \
        "preamble/tests/code/$test.tex" preamble/tests/build/code
done
