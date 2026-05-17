# OfferLens

Local-first interview review reports. Turn interview recordings into structured Chinese review documents — without uploading your audio or transcripts to the cloud.

## What it does

- Extracts audio from local interview videos (`.mov`, `.mp4`, `.m4a`, `.wav`)
- Runs local ASR with speaker diarization (whisperx, faster-whisper, etc.)
- Identifies interviewer questions and candidate answers
- Generates a compact review report with:
  - Interviewer questions & your cleaned answers
  - Short suggested answers with source citations
  - Code question review with invariant and complexity
  - High-risk technical point remediation
  - Follow-up learning resources (5-8 traceable items)
- Outputs **Markdown**, **HTML**, and optionally **LaTeX/PDF**

## Install

```bash
pip install -e .
```

Requires Python >= 3.9. For full pipeline features you also need:

```bash
# FFmpeg (audio extraction & probing)
# macOS:  brew install ffmpeg
# Linux:  apt install ffmpeg
# Windows: https://ffmpeg.org/download.html

# LaTeX (optional, for PDF output)
# macOS:  brew install mactex-no-gui
# Linux:  apt install texlive-xetex texlive-latex-extra latexmk
```

## Quick start

```bash
# Create a sample report to verify the pipeline works
offerlens sample --out /tmp/demo

# View results
open /tmp/demo/interview_review.html
```

## Usage

```bash
# 1. Initialize a work directory for your recording
offerlens init --workdir ./my-review --input interview.mov

# 2. Probe media metadata
offerlens pipeline probe --input interview.mov --out-dir ./my-review/supporting_files

# 3. Extract mono 16kHz WAV
offerlens pipeline extract-audio --input interview.mov --audio ./my-review/supporting_files/audio.wav

# 4. Run local ASR to produce transcript_raw.json
#    (use whisperx, faster-whisper, or openai-whisper)

# 5. Normalize transcript into transcript_normalized.json
#    Infer speaker roles, extract question candidates

# 6. Agent/LLM writes review_plan.json, then render
offerlens render --workdir ./my-review

# 7. Validate
offerlens validate --workdir ./my-review

# Optional: compile LaTeX to PDF
offerlens render --workdir ./my-review --compile
```

## Output structure

```
my-review/
  interview_review.md          # Chinese Markdown report
  interview_review.html        # Styled HTML report
  references.md                # Source citations
  supporting_files/
    interview_review.tex       # LaTeX source
    review_plan.json           # Core data model
    source_registry.json       # Evidence registry
    quality_report.json        # Validation results
    ...
```

## Privacy

All processing is local-first. Audio, video, transcripts, and screenshots stay on your machine unless you explicitly choose a cloud ASR backend. Default examples are fictional and contain no real interview data.

## License

MIT
