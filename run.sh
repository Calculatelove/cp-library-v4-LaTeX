#!/usr/bin/env bash
# 依赖：XeLaTeX、latexminted 及项目导言区使用的 TeX 宏包。
# 用法：./run.sh [portrait|landscape|code|all]；默认 portrait。
set -euo pipefail

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
    local max_passes=8 previous_state='' current_state converged=false
    local pass extension record
    mkdir -p "$output_dir"

    # 至少两轮，最多八轮；从根目录编译，使用默认受限 shell escape。
    for ((pass = 1; pass <= max_passes; pass++)); do
        printf '\n正在编译 %s.tex（第 %s/%s 轮）……\n' "$job" "$pass" "$max_passes"
        if ! xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
            -output-directory="$output_dir" "$job.tex"; then
            printf '\n编译失败；已保留本版辅助文件，请检查 %s/%s.log。\n' "$output_dir" "$job" >&2
            return 1
        fi
        current_state="$(
            for extension in aux toc out lof lot; do
                record="$output_dir/$job.$extension"
                if [[ -f "$record" ]]; then
                    cksum "$record"
                else
                    printf '%s missing\n' "$record"
                fi
            done
        )"
        if ((pass >= 2)) && [[ "$current_state" == "$previous_state" ]] &&
            [[ -f "$output_dir/$job.log" ]] &&
            ! grep -Eq 'Rerun to get|Rerun LaTeX|Please rerun LaTeX|Label\(s\) may have changed' "$output_dir/$job.log"; then
            converged=true
            break
        fi
        previous_state="$current_state"
    done
    if [[ "$converged" != true ]]; then
        printf '\n%s 编译 %s 轮后仍未稳定；已保留辅助文件和日志：%s/%s.log。\n' "$job" "$max_passes" "$output_dir" "$job" >&2
        return 1
    fi
    if [[ ! -s "$output_dir/$job.pdf" ]]; then
        printf '\n未生成非空 PDF：%s/%s.pdf；已保留辅助文件和日志。\n' "$output_dir" "$job" >&2
        return 1
    fi

    printf '\n目录与交叉引用已稳定（共 %s 轮）。\n' "$pass"
    # 仅清理当前版本的已知辅助文件及 minted 缓存。
    for extension in aux log out toc lof lot fls fdb_latexmk xdv synctex.gz; do
        rm -f -- "$output_dir/$job.$extension"
    done
    rm -rf -- "$output_dir/_minted" "$output_dir/_minted-$job"
    printf '\nPDF 已生成：%s/%s/%s.pdf\n' "$project_dir" "$output_dir" "$job"
}

for target in "${targets[@]}"; do
    build_target "$target"
done
