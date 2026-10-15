#!/usr/bin/env bash
# 从项目根目录或任意目录运行；不带参数时编译全部接口样张，也可只传入样张名。
# 每份样张由 scripts/xelatex-converge.sh 编译至收敛，并严格检查日志；产物在 preamble/tests/build/mystyle/。
set -euo pipefail
cd "$(dirname "$0")/../../.."
if (( $# == 0 )); then
    set -- highlight input-code input-code-pages quoteblock separator
fi
for test in "$@"; do
    bash scripts/xelatex-converge.sh --quiet --strict \
        "preamble/tests/mystyle/$test.tex" preamble/tests/build/mystyle
done
