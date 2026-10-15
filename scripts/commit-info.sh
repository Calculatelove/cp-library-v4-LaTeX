#!/usr/bin/env bash
# 输出扉页使用的提交信息，由根目录 run.sh 写入 build/<版本>/main-<版本>.commit。
# 共四行：提交日期（按提交自身时区，YYYY-MM-DD）、短哈希、提交说明首行、clean 或 dirty。
# 取 build/ 以外最后一次提交：只改构建产物的提交不计入。
# build/ 以外有未提交修改（含未跟踪文件）时第四行为 dirty。
# 不是 Git 仓库、找不到 git 或尚无提交时不输出内容，在标准错误说明原因并返回 0。
set -euo pipefail

root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"

if ! command -v git >/dev/null 2>&1 ||
    ! git -C "$root" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    printf '未找到 Git 仓库，扉页不显示提交信息。\n' >&2
    exit 0
fi

if ! info="$(git -C "$root" log -1 --format='%cd%n%h%n%s' --date=format:%Y-%m-%d \
    -- . ':(exclude)build' 2>/dev/null)" || [[ -z "$info" ]]; then
    printf '尚无提交，扉页不显示提交信息。\n' >&2
    exit 0
fi

if [[ -n "$(git -C "$root" status --porcelain --untracked-files=normal -- . ':(exclude)build')" ]]; then
    state=dirty
else
    state=clean
fi
printf '%s\n%s\n' "$info" "$state"
