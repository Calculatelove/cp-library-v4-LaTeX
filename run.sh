#!/usr/bin/env bash
# 依赖：XeLaTeX、latexminted 及项目导言区使用的 TeX 宏包；扉页提交信息另需 git（可选）。
# 用法：./run.sh [portrait|landscape|code|all]；默认 portrait。
# 编译收敛循环在 scripts/xelatex-converge.sh，与 preamble/tests 的运行脚本共用。
set -euo pipefail
SECONDS=0

usage() {
    printf '用法：%s [portrait|landscape|code|all]\n默认编译 portrait；产物写入 build/<版本>/。\n' "${0##*/}"
}
if (( $# > 1 )); then
    usage >&2
    exit 2
fi
case "${1:-portrait}" in
    portrait|landscape|code) targets=("${1:-portrait}") ;;
    all) targets=(portrait landscape code) ;;
    -h|--help) usage; exit 0 ;;
    *) usage >&2; exit 2 ;;
esac

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$project_dir"

# 代码版先生成入口；生成器失败时不启动任何版本的编译。
for target in "${targets[@]}"; do
    if [[ "$target" == code ]]; then
        if ! command -v python3 >/dev/null 2>&1; then
            printf '缺少依赖：python3。\n' >&2
            exit 1
        fi
        python3 scripts/generate-code.py
    fi
done

# all 在编译前检查全部入口，避免空占位文件导致无意义的部分构建。
for target in "${targets[@]}"; do
    source_file="main-$target.tex"
    if [[ ! -f "$source_file" ]] || ! grep -q '[^[:space:]]' "$source_file"; then
        printf '入口不存在或仍为空占位文件：%s，请先补全。\n' "$source_file" >&2
        exit 1
    fi
done
for dependency in xelatex latexminted; do
    if ! command -v "$dependency" >/dev/null 2>&1; then
        printf '缺少依赖：%s，请安装并加入 PATH。\n' "$dependency" >&2
        exit 1
    fi
done

build_target() {
    local target="$1"
    local job="main-$target" output_dir="build/$target"
    local commit_info
    mkdir -p "$output_dir"

    # 扉页提交信息：在代码版入口生成之后读取 Git 状态；不在 Git 仓库中时不生成文件。
    commit_info="$(bash scripts/commit-info.sh)"
    if [[ -n "$commit_info" ]]; then
        printf '%s\n' "$commit_info" > "$output_dir/$job.commit"
        if [[ "${commit_info##*$'\n'}" == dirty ]]; then
            printf '提示：build/ 以外有未提交修改，扉页将标注“含未提交修改”。\n' >&2
        fi
    else
        rm -f -- "$output_dir/$job.commit"
    fi

    # 编译至收敛（至少两轮、最多八轮）由共用脚本负责；从根目录编译，使用默认受限 shell escape。
    if ! bash scripts/xelatex-converge.sh "$job.tex" "$output_dir"; then
        printf '已保留本版辅助文件和日志：%s/。\n' "$output_dir" >&2
        return 1
    fi

    # 保留辅助文件、日志与 minted 缓存，供后续构建复用及警告排查。
}

format_duration() {
    local seconds="$1"
    if (( seconds == 0 )); then
        printf '不足 1 秒'
        return
    fi
    if (( seconds >= 3600 )); then printf '%s 小时 ' "$((seconds / 3600))"; fi
    if (( seconds >= 60 )); then printf '%s 分 ' "$((seconds / 60 % 60))"; fi
    printf '%s 秒' "$((seconds % 60))"
}

summary=''
for target in "${targets[@]}"; do
    started=$SECONDS
    build_target "$target"
    elapsed=$((SECONDS - started))
    case "$target" in
        portrait) label=竖版 ;;
        landscape) label=横版 ;;
        code) label=代码版 ;;
    esac
    printf -v summary '%s\n- %s：%s\n  PDF：%s/build/%s/main-%s.pdf\n' \
        "$summary" "$label" "$(format_duration "$elapsed")" "$project_dir" "$target" "$target"
done
printf '\n构建完成，总耗时：%s\n%s' "$(format_duration "$SECONDS")" "$summary"
