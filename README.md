# OfferLens

本地优先的面试复盘工具。将面试录音/视频转为结构化中文复盘报告——音频和转写内容默认不离开本机。

## 功能

- 从本地面试视频中提取音频（`.mov`、`.mp4`、`.m4a`、`.wav`）
- 本地 ASR 转写，支持说话人分离（whisperx、faster-whisper、mlx-whisper、openai-whisper）
- 识别面试官问题与候选人回答
- 生成紧凑复盘报告，包含：
  - 面试官问题 & 你的回答（清洗后）
  - 简短建议答案，附来源引用
  - 代码题复盘（不变量、复杂度、口述脚本）
  - 高风险技术点速记
  - 后续巩固资料（5-8 条可追溯资源）
- 输出 **Markdown**、**HTML**，可选 **LaTeX/PDF**

## 仓库结构

```
OfferLens/
├── offerlens/          # Python 包，提供 offerlens CLI
├── skill/offerlens/    # Claude Code Skill（SKILL.md + references + templates）
├── pyproject.toml
└── README.md
```

两层是配合工作的：Python 包负责确定性步骤（探测、抽音频、渲染、校验），Skill 教 Claude 何时调用 CLI、何时做判断。**两者必须都装好才能运行**。

## 安装

> ⚠️ **顺序很重要**：先装 Python 包，再装 Skill。Skill 调用的 `offerlens` 命令来自 Python 包，反过来不行。

### 1. 装 Python 包（必需）

```bash
git clone https://github.com/YoungBossX/OfferLens.git
cd OfferLens
pip install -e .
```

需要 Python >= 3.9。验证：

```bash
which offerlens   # 应该输出可执行路径
offerlens --help
```

### 2. 装系统依赖

```bash
# FFmpeg（必需，音频提取）
brew install ffmpeg              # macOS
sudo apt install ffmpeg          # Linux
# Windows: https://ffmpeg.org/download.html

# 本地 ASR（至少装一个）
pip install whisperx             # 推荐，支持说话人分离
# 或
pip install faster-whisper
# 或（Apple Silicon）
pip install mlx-whisper

# LaTeX（可选，仅 PDF 输出需要）
brew install --cask mactex-no-gui                                 # macOS
sudo apt install texlive-xetex texlive-latex-extra latexmk        # Linux
```

### 3. 安装 Skill

#### 方式 A：手动复制（最稳）

```bash
cp -r skill/offerlens ~/.claude/skills/offerlens
```

重启 Claude Code 后生效。

#### 方式 B：通过 cc-switch 安装

1. 打开 cc-switch，进入 Skills 面板
2. 添加 → 从 GitHub 仓库安装 → 粘贴 `https://github.com/YoungBossX/OfferLens`
3. install-name 设为 `offerlens`（cc-switch 会递归找到 `skill/offerlens/SKILL.md`）
4. 勾选分发到 Claude Code，同步方式建议选「文件复制」
5. 确认 `pip install -e .` 已在仓库根目录跑过

> cc-switch 只会同步 `skill/offerlens/` 这部分内容。**它不会替你装 Python 包**——这一步必须手动做。

### 4. 验证

```bash
# 跑示例，验证管线和环境
offerlens sample --out /tmp/demo
open /tmp/demo/interview_review.html
```

在 Claude Code 里输入「我有一段面试录像想复盘」，应该会触发 offerlens skill。

## 用法

```bash
# 1. 为面试录像创建工作目录
offerlens init --workdir ./my-review --input interview.mov

# 2. 探测媒体元信息
offerlens pipeline probe --input interview.mov --out-dir ./my-review/supporting_files

# 3. 提取单声道 16kHz WAV
offerlens pipeline extract-audio --input interview.mov --audio ./my-review/supporting_files/audio.wav

# 4. 跑本地 ASR 生成 transcript_raw.json（用 whisperx / faster-whisper / openai-whisper）

# 5. 将转写结果规范化为 transcript_normalized.json，推断说话人角色，抽取问题候选

# 6. Agent/LLM 填写 review_plan.json 后渲染
offerlens render --workdir ./my-review

# 7. 校验
offerlens validate --workdir ./my-review

# 可选：编译 LaTeX 为 PDF
offerlens render --workdir ./my-review --compile
```

通常你不需要手动跑这些——Skill 会指导 Claude 按顺序调用。

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

## 常见问题

**Claude 说 `offerlens: command not found`**
忘了 `pip install -e .`，或者装在了另一个 Python 环境。检查 `which offerlens` 与 Claude Code 使用的 shell 是否一致。

**ASR 输出乱码或全是英文**
确认本地 ASR 模型支持中文（whisperx、faster-whisper 默认的 `large-v3`、`medium` 都行，`tiny.en` 这种英文专用模型不行）。

**cc-switch 找不到 SKILL.md**
SKILL.md 在 `skill/offerlens/` 二级目录，cc-switch v3.13+ 才支持嵌套路径递归搜索。低版本请直接手动 `cp -r skill/offerlens ~/.claude/skills/offerlens`。

## License

MIT
