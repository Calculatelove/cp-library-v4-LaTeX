#!/usr/bin/env bash
# 用 XeLaTeX 反复编译一个 .tex 文件，直到目录与交叉引用稳定；根目录 run.sh 与 preamble/tests 各运行脚本共用。
# 用法：scripts/xelatex-converge.sh [--quiet] [--strict] <tex 文件> <输出目录>
#   两个路径都相对于项目根目录；脚本先回到项目根目录再编译，可从任意目录调用。
#   --quiet   XeLaTeX 输出写入 <输出目录>/<文件名>-console.txt，失败时显示末尾 40 行；默认直接输出到终端。
#   --strict  收敛后检查日志，有缺字、Overfull、字体替换或页眉高度不足时失败；供样张使用。
# 收敛后汇总末轮日志的警告：Overfull、Underfull、缺字、字体替换的数量，以及按来源统计的其他警告。
#   默认模式逐项列出（含 0）；--quiet 模式只在行尾列出不为零的项。
# 至少两轮、最多八轮：比较 aux/toc/out/lof/lot 的校验和，并检查日志中的重编译提示；最后确认 PDF 非空。
# 使用默认的受限 shell escape。只编译、不清理：失败时辅助文件与日志都保留在输出目录。
# 返回值：0 成功；1 编译失败、八轮未收敛、PDF 为空或严格检查不通过；2 用法错误。
set -euo pipefail

usage() {
    printf '用法：%s [--quiet] [--strict] <tex 文件> <输出目录>\n' "${0##*/}"
}

quiet=false
strict=false
while (( $# > 0 )); do
    case "$1" in
        --quiet) quiet=true; shift ;;
        --strict) strict=true; shift ;;
        -h|--help) usage; exit 0 ;;
        -*) usage >&2; exit 2 ;;
        *) break ;;
    esac
done
if (( $# != 2 )); then
    usage >&2
    exit 2
fi
source_file="$1"
output_dir="$2"
job="$(basename -- "$source_file" .tex)"

cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
if [[ ! -f "$source_file" ]]; then
    printf '找不到源文件：%s（路径相对于项目根目录）\n' "$source_file" >&2
    exit 2
fi
mkdir -p -- "$output_dir"

max_passes=8
previous_state=''
converged=false
console="$output_dir/$job-console.txt"
for ((pass = 1; pass <= max_passes; pass++)); do
    if [[ "$quiet" == true ]]; then
        if ! xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
            -output-directory="$output_dir" "$source_file" > "$console" 2>&1; then
            tail -40 "$console" >&2
            printf '\n%s 编译失败，请检查 %s/%s.log。\n' "$job" "$output_dir" "$job" >&2
            exit 1
        fi
    else
        printf '\n正在编译 %s（第 %s/%s 轮）……\n' "$source_file" "$pass" "$max_passes"
        if ! xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
            -output-directory="$output_dir" "$source_file"; then
            printf '\n%s 编译失败，请检查 %s/%s.log。\n' "$job" "$output_dir" "$job" >&2
            exit 1
        fi
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
    printf '\n%s 编译 %s 轮后仍未稳定，请检查 %s/%s.log。\n' "$job" "$max_passes" "$output_dir" "$job" >&2
    exit 1
fi
if [[ ! -s "$output_dir/$job.pdf" ]]; then
    printf '\n未生成非空 PDF：%s/%s.pdf。\n' "$output_dir" "$job" >&2
    exit 1
fi
# 末轮日志的警告汇总：四类计数，加上按来源统计的其他 LaTeX、宏包与文档类警告。
log="$output_dir/$job.log"
count() {
    grep -cE "$1" "$log" || true
}
overfull=$(count '^Overfull \\[hv]box')
underfull=$(count '^Underfull \\[hv]box')
missing=$(count 'Missing character:')
fonts=$(count 'Font shape .*undefined|Some font shapes were not available')
others=$(grep -oE '^(Package [A-Za-z0-9_.-]+|Class [A-Za-z0-9_.-]+|LaTeX) Warning' "$log" |
    sed -E 's/^(Package|Class) //; s/ Warning$//' | sort | uniq -c |
    awk '{ printf "%s%s %s", (NR > 1 ? "，" : ""), $2, $1 }' || true)
summary="Overfull $overfull，Underfull $underfull，缺字 $missing，字体替换 $fonts"
if [[ -n "$others" ]]; then
    summary+="；其他：$others"
fi
# 样张只列不为零的项。
brief=''
for item in "Overfull $overfull" "Underfull $underfull" "缺字 $missing" "字体替换 $fonts"; do
    if [[ "${item##* }" != 0 ]]; then
        brief+="${brief:+，}$item"
    fi
done
if [[ -n "$others" ]]; then
    brief+="${brief:+；}$others"
fi

if [[ "$strict" == true ]] &&
    grep -Eq 'Missing character:|Overfull|Font shape .*undefined|Some font shapes were not available|headheight is too small' "$log"; then
    printf '%s：日志中有缺字、Overfull、字体替换或页眉高度不足（末轮警告：%s），请检查 %s。\n' \
        "$job" "$summary" "$log" >&2
    exit 1
fi
if [[ "$quiet" == true ]]; then
    printf '%s：%s 轮收敛%s\n' "$job" "$pass" "${brief:+（末轮警告：$brief）}"
else
    printf '\n目录与交叉引用已稳定（共 %s 轮）。\n末轮警告：%s\n' "$pass" "$summary"
fi
