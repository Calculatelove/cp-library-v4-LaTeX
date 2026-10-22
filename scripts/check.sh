#!/usr/bin/env bash
# 一键检查。默认只做快速检查：单元测试（含入口一致性）与代码版入口是否最新。
# --full 另编译默认回归样张并运行 PDF 功能检查。整书由 ./run.sh 构建，按影响范围抽查。
# 用法：scripts/check.sh [--full]；可从任意目录调用。
# 某一步失败不中断后续步骤，最后汇总失败的步骤；有失败时返回 1，用法错误返回 2。
set -uo pipefail

usage() {
    printf '用法：%s [--full]\n' "${0##*/}"
}

full=false
case "${1:-}" in
    '') ;;
    --full) full=true ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac
if (( $# > 1 )); then
    usage >&2
    exit 2
fi
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."

failed=()
step() {
    local name="$1"
    shift
    printf '\n== %s\n' "$name"
    if "$@"; then
        printf '通过：%s\n' "$name"
    else
        printf '失败：%s\n' "$name" >&2
        failed+=("$name")
    fi
}

step '单元测试与入口一致性' python3 -B -m unittest discover -s scripts/tests
step '代码版入口是否最新' bash -c 'python3 scripts/generate-code.py --check > /dev/null'
if [[ "$full" == true ]]; then
    for group in portrait landscape code; do
        step "编译 $group 样张" bash "preamble/tests/$group/run.sh"
    done
    step '竖版样张检查' python3 preamble/tests/portrait/check.py
    step '横版样张检查' python3 preamble/tests/landscape/check.py
    step '代码版样张检查' python3 preamble/tests/landscape/check.py code
fi

printf '\n'
if (( ${#failed[@]} > 0 )); then
    printf '共 %s 步失败：\n' "${#failed[@]}" >&2
    printf '  - %s\n' "${failed[@]}" >&2
    exit 1
fi
printf '全部检查通过。\n'
