# OfferLens

本地优先的面试复盘工具。将面试录音/视频转为结构化中文复盘报告——音频和转写内容不会上传到云端。

## 功能

- 从本地面试视频中提取音频（`.mov`、`.mp4`、`.m4a`、`.wav`）
- 本地 ASR 转写，支持说话人分离（whisperx、faster-whisper 等）
- 识别面试官问题和候选人回答
- 生成紧凑复盘报告，包含：
  - 面试官问题 & 你的回答（清洗后）
  - 简短建议答案，附来源引用
  - 代码题复盘（不变量、复杂度、口述脚本）
  - 高风险技术点速记
  - 后续巩固资料（5-8 条可追溯资源）
- 输出 **Markdown**、**HTML**，可选 **LaTeX/PDF**

## 安装

```bash
pip install -e .
```

需要 Python >= 3.9。完整管线还需要：

```bash
# FFmpeg（音频提取和元信息探测）
# macOS:  brew install ffmpeg
# Linux:  apt install ffmpeg
# Windows: https://ffmpeg.org/download.html

# LaTeX（可选，用于 PDF 输出）
# macOS:  brew install mactex-no-gui
# Linux:  apt install texlive-xetex texlive-latex-extra latexmk
```

## 快速上手

```bash
# 生成示例报告，验证管线是否正常
offerlens sample --out /tmp/demo

# 查看结果
open /tmp/demo/interview_review.html
```

## 用法

```bash
# 1. 为面试录像创建工作目录
offerlens init --workdir ./my-review --input interview.mov

# 2. 探测媒体元信息
offerlens pipeline probe --input interview.mov --out-dir ./my-review/supporting_files

# 3. 提取单声道 16kHz WAV
offerlens pipeline extract-audio --input interview.mov --audio ./my-review/supporting_files/audio.wav

# 4. 运行本地 ASR 生成 transcript_raw.json
#    （用 whisperx / faster-whisper / openai-whisper）

# 5. 将转写结果规范化为 transcript_normalized.json
#    推断说话人角色、抽取问题候选

# 6. Agent/LLM 填写 review_plan.json 后渲染
offerlens render --workdir ./my-review

# 7. 校验
offerlens validate --workdir ./my-review

# 可选：编译 LaTeX 为 PDF
offerlens render --workdir ./my-review --compile
```

## 输出结构

```
my-review/
  interview_review.md          # 中文 Markdown 报告
  interview_review.html        # 带样式的 HTML 报告
  references.md                # 来源引用
  supporting_files/
    interview_review.tex       # LaTeX 源文件
    review_plan.json           # 核心数据模型
    source_registry.json       # 来源注册表
    quality_report.json        # 校验结果
    ...
```

## 隐私

所有处理默认本地运行。音频、视频、转写文本和截图均不上传，除非你主动选择云端 ASR 后端。示例数据均为虚构，不包含真实面试内容。

## 作为 Claude Code Skill 使用

将 skill 目录复制到 Claude Code 的 skills 路径：

```bash
cp -r skill/offerlens ~/.claude/skills/offerlens
```

重启 Claude Code 后，`/offerlens` 可在任意项目中触发。

## License

MIT
