# Codebook Cinema

把 Python 或 TypeScript 仓库转换为本地、可追溯证据的讲解章节、Mermaid 架构图、可编辑镜头清单和旁白草稿；不依赖在线 LLM。

```bash
python -m pip install -e '.[dev]'
codebook-cinema analyze examples/python_cli --output demo-output
```

输出 `report.json`、`report.md` 和可直接打开的 `storyboard.html`。每条自动描述都链接到真实文件和可确认的符号；无法从结构确认的用途会标为 `unknown`。项目状态：**v0.1.0**。

核心价值：离线保护代码隐私、可编辑演示资产、基于文件/符号的事实链。完整英文说明、测试命令、非目标和隐私边界请见 [README.md](README.md)。
