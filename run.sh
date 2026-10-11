#!/usr/bin/env bash
# 依赖：XeLaTeX、latexminted 及项目导言区使用的 TeX 宏包。
# 用法：./run.sh；PDF 写入 build/，成功后清理编译辅助文件和缓存。
set -euo pipefail

project_dir="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
cd -- "$project_dir"

for dependency in xelatex latexminted; do
    if ! command -v "$dependency" >/dev/null 2>&1; then
        printf '缺少依赖：%s，请安装并加入 PATH。\n' "$dependency" >&2
        exit 1
    fi
done

mkdir -p build

# 比较目录、交叉引用和书签记录；minted 首轮生成缓存后可能改变分页。
# 至少编译两轮，最多八轮；使用 TeX Live 默认的受限 shell escape。
max_passes=8
previous_state=''
converged=false
for ((pass = 1; pass <= max_passes; pass++)); do
    printf '\n正在编译 main-portrait.tex（第 %s/%s 轮）……\n' "$pass" "$max_passes"
    xelatex -interaction=nonstopmode -halt-on-error -file-line-error \
        -output-directory=build main-portrait.tex

    current_state="$(
        for extension in aux toc out lof lot; do
            record="build/main-portrait.$extension"
            if [[ -f "$record" ]]; then
                cksum "$record"
            else
                printf '%s missing\n' "$record"
            fi
        done
    )"
    if ((pass >= 2)) && [[ "$current_state" == "$previous_state" ]] &&
        ! grep -Eq 'Rerun to get|Rerun LaTeX|Please rerun LaTeX|Label\(s\) may have changed' build/main-portrait.log; then
        converged=true
        break
    fi
    previous_state="$current_state"
done

if [[ "$converged" != true ]]; then
    printf '\n编译 %s 轮后目录或交叉引用仍未稳定；已保留辅助文件和日志，请检查 build/main-portrait.log。\n' "$max_passes" >&2
    exit 1
fi

printf '\n目录与交叉引用已稳定（共 %s 轮）。\n' "$pass"
# 仅在编译成功且记录稳定后清理；失败时保留日志供排查。
rm -f -- build/main-portrait.{aux,log,out,toc,lof,lot,fls,fdb_latexmk,xdv,synctex.gz}
rm -rf -- build/_minted

printf '\nPDF 已生成：%s/build/main-portrait.pdf\n' "$project_dir"
