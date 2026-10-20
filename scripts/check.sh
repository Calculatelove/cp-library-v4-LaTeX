#!/usr/bin/env bash
# 一键检查。默认只做快速检查：单元测试（含入口一致性）、代码版入口是否最新、文档与脚本检查，约 1 秒。
# --full 另依次编译四组导言区样张、运行全部样张 PDF 检查；build/ 中已有完整横版、
# 代码版 PDF 时再做越栏检查（只输出警告）。完整三版 PDF 仍由 ./run.sh 构建。
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
step '文档与脚本检查' python3 -B scripts/check-docs.py
if [[ "$full" == true ]]; then
    for group in mystyle portrait landscape code; do
        step "编译 $group 样张" bash "preamble/tests/$group/run.sh"
    done
    step '竖版扉页' python3 preamble/tests/portrait/check-titlepage.py
    step '竖版四、五级标题' python3 preamble/tests/portrait/check-headings.py
    step '竖版代码配色' python3 preamble/tests/portrait/check-syntax-colors.py
    step '竖版块间距' python3 preamble/tests/portrait/check-spacing.py
    step '横版布局' python3 preamble/tests/landscape/check-layout.py
    step '横版扉页' python3 preamble/tests/landscape/check-titlepage.py
    step '代码版布局' python3 preamble/tests/landscape/check-layout.py code
    step '代码版扉页' python3 preamble/tests/landscape/check-titlepage.py code
    for edition in landscape code; do
        pdf="build/$edition/main-$edition.pdf"
        if [[ -f "$pdf" ]]; then
            step "完整 $edition PDF 越栏（只输出警告）" python3 scripts/check-full.py "$pdf"
        else
            printf '\n跳过完整 %s PDF 越栏检查：尚未构建 %s。\n' "$edition" "$pdf"
        fi
    done
fi

printf '\n'
if (( ${#failed[@]} > 0 )); then
    printf '共 %s 步失败：\n' "${#failed[@]}" >&2
    printf '  - %s\n' "${failed[@]}" >&2
    exit 1
fi
printf '全部检查通过。\n'
