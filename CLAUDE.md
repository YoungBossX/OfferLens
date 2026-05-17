# OfferLens

本地优先的面试复盘工具。Python 包 + Claude Code Skill 双层结构。

## 架构

```
offerlens/          # Python 包 — 确定性步骤（CLI、管线、渲染）
skill/offerlens/    # Claude Code Skill — 教 Agent 何时调用 CLI、何时做判断
```

Python 包负责：`offerlens init/render/validate/pipeline/sample`
Skill 负责：环境检查、ASR 转写判断、review_plan.json 编写、渲染/校验编排

Skill 调用 `offerlens` CLI，所以 `pip install -e .` 必须先于 Skill 安装。

## 命令速查

```bash
offerlens sample --out /tmp/demo              # 生成示例报告（端到端验证）
offerlens init --workdir <dir> --input <v>    # 初始化工作目录
offerlens render --workdir <dir> [--compile]  # 渲染 Markdown/HTML/LaTeX
offerlens validate --workdir <dir>            # 校验 review_plan.json
```

## 开发约定

- 示例数据（`offerlens/examples/`）必须虚构，不包含真实面试内容
- LaTeX 模板变量用 `<<PLACEHOLDER>>` 格式，由 `render.py` 替换
- `review_plan.json` 是核心数据模型，`supporting_files/` 放重建/出处文件
- 隐私默认：不上传音频/视频/转写，就地处理
