# 脚本测试

从项目根目录运行（依赖 Python 3 与 git）：

```sh
python3 -B -m unittest discover -s scripts/tests
```

`scripts/check.sh` 会运行这些测试：

- `test_generate_code.py`：代码提取、标题归属、顺序与入口模板转换。
- `test_commit_info.py`：提交信息原文、日期与工作区状态。
- `test_entries.py`：两个手写入口除布局引用外逐行一致。

临时文件使用系统临时目录。排版验收见 `preamble/tests/README.md`。
