---
name: offerlens
description: Turn local interview videos, interview recordings, or interview audio files into local-first Chinese interview review reports focused on interviewer questions, the candidate's answers, concise sourced standard answers, compact coding/technical follow-up review, and short follow-up learning resources. Use when the user provides a local .mov/.mp4/.m4a/.wav recording and asks for 面试复盘, 面经整理, 面试官问题, 我的回答, 建议答案, 标准答法, 回答评价, 代码题复盘, 后续巩固资料, Q&A extraction, speaker/role inference, source-backed corrections, or a polished Markdown/HTML/LaTeX report. The skill extracts audio locally, transcribes locally when possible, infers interviewer/candidate roles, registers local/public sources, renders a structured report, and validates the final output.
---

# OfferLens

Use this skill to convert any local interview video or audio recording into a Chinese interview review report. Optimize for: `面试官问题覆盖率 + 我的回答 > 简短建议答案 > 一句评价/关键扣分点 > 后续巩固资料`.

The output is not a course note, not a raw transcript, and not a long training plan. Keep the report compact enough to review before the next interview.

## Local-First Rule

Do not upload interview audio, video, transcripts, screenshots, resume details, or company-sensitive content unless the user explicitly asks for a cloud route.

Preferred ASR order:

1. `whisperx` with diarization when available.
2. `mlx-whisper` or `faster-whisper` for local ASR.
3. `openai-whisper` CLI fallback.
4. If diarization is unavailable, infer roles from dialogue structure and mark speaker confidence.

## Privacy Defaults

Treat the skill package as reusable and non-personal:

- do not include real interview transcripts, company names, candidate names, usernames, home directories, or absolute local paths in bundled examples;
- do not show local absolute paths in the final report or `references.md` by default;
- record local evidence with `event_id`, `artifact_id`, basename-only paths, and time ranges;
- keep full paths only in transient internal commands or when the user explicitly asks for a debug/provenance bundle;
- remove extracted audio, LaTeX intermediates, temporary text extracts, and OS metadata files after validation.

## Output Contract

Create one work directory per recording. Keep the final output clean and two-level:

```text
interview_review.md
interview_review.html
references.md
supporting_files/
  interview_review.tex
  review_plan.json
  source_registry.json
  question_candidates.json
  interview_events.json
  transcript_normalized.json
  transcript_raw.json
  transcript_raw.srt
  speaker_map.json
  media_probe.json
  run_metadata.json
  evidence_frames.json
  quality_report.json
  build_log.md
  <evidence-frame>.png
```

Keep Markdown output as a draft only. The final deliverable is `<run-dir>/interview_review.md` (primary) and `<run-dir>/interview_review.html`, with optional LaTeX/PDF compilation. Put rebuild/provenance files in `<run-dir>/supporting_files/`.

Delete or avoid retaining bulky/transient files after the report is validated unless the user asks for them: extracted `audio.wav`, LaTeX `.aux/.fls/.fdb_latexmk/.out/.toc/.xdv/.log`, duplicate ASR `.txt/.tsv/.vtt`, `.DS_Store`, and temporary run directories.

Use natural report titles in `metadata.title`, such as `<company/team/topic> 面试复盘`. Keep `metadata.subtitle` empty by default unless the user asks for a specific subtitle.

## Workflow

Use `offerlens` CLI for deterministic local steps:

```bash
SUPPORT=<run-dir>/supporting_files
offerlens init --workdir <run-dir> --input <video>
offerlens pipeline probe --input <video> --out-dir "$SUPPORT"
offerlens pipeline extract-audio --input <video> --audio "$SUPPORT/audio.wav"
# Run local ASR (whisperx, faster-whisper, etc.) to produce transcript_raw.json and transcript_raw.srt.
# Normalize into supporting_files/transcript_normalized.json
# Infer speaker roles into supporting_files/speaker_map.json
# Extract question candidates into supporting_files/question_candidates.json
# Agent/LLM reviews transcript, question candidates, and evidence,
# then writes interview_events.json, source_registry.json, and review_plan.json.
offerlens render --workdir <run-dir>
offerlens render --workdir <run-dir> --compile  # optional PDF compilation
offerlens validate --workdir <run-dir>
```

The agent owns the judgment-heavy parts:

- inspect transcript segments and evidence frames;
- inspect `supporting_files/question_candidates.json`;
- write `supporting_files/interview_events.json`;
- write `supporting_files/source_registry.json`;
- write or refine `supporting_files/review_plan.json`;
- rerun render/compile/validate until the report is useful and clean.

## Compact Sourced Report Standard

Set `metadata.report_style` to `compact_sourced`.

The report must contain these main sections:

1. `首页摘要`
2. `面试官问题与我的回答`
3. `重点追问复盘`
4. `代码题复盘`
5. `高风险技术点速记`
6. `参考来源`
7. `后续巩固资料`

Do not add `7天训练计划`, `证据与转写说明`, or long raw transcript sections unless the user explicitly asks.

Each question card should include:

- `时间`
- `面试官问题`
- `我的回答`
- `建议答案`
- `来源`
- optional `一句评价`

`面试官问题` must use `question_cleaned`, not the raw ASR fragment. Fix ASR spelling and missing words only when supported by the nearby transcript and answer window; if the exact question is unrecoverable, write a bounded form such as `面试官追问：这里的 X 具体指什么？` instead of rendering nonsense.

`我的回答` must be a cleaned version of the candidate's real answer from the transcript window, not a one-sentence evaluation. Keep the original order and concrete details; remove only obvious ASR hallucinations, long repeated phrases, filler, and screen-share noise. Use `answer_summary` only as an internal short summary or overview signal.

Each question card should show a compact top-left quality tag like `passable 3/5`, `risky 2/5`, or `strong 5/5`, plus an importance tag like `key` or `covered`.

Keep `建议答案` short. Use 1-3 sentences unless the user asks for deeper teaching notes.

Coverage rules:

- Preserve most substantive interviewer questions and follow-ups. Do not collapse a long technical discussion into one broad card.
- Only filter greetings, logistics, ASR hallucinations, and repeated acknowledgements.
- For interviews longer than 30 minutes, default targets are: 10-16 question cards for <=35 minute interviews, 14-20 for 35-65 minute interviews, and 18-28 for longer interviews. Actual count should follow transcript evidence.
- Mark 5-8 high-risk/high-value questions with `is_key: true`; those receive fuller review in `重点追问复盘`.

Add `learning_resources` for `后续巩固资料` at the end of the report:

- include 5-8 items, grouped by topics revealed in this interview;
- each item needs `topic`, `title`, `type`, `url` or `citation`, `why`, and `priority`;
- optional fields: `language`, `duration`;
- use traceable sources: papers, official docs, official repositories/docs, university/course notes, original blogs, Zhihu articles, YouTube videos, Bilibili videos, or comparable knowledge-sharing pages;
- keep each `why` to one concise sentence explaining the exact gap it helps fix;
- do not invent links or source titles. If reliable material is unavailable, write `来源不足，建议补材料` in the report rather than fabricating a resource.

## Source Rules

Use `supporting_files/source_registry.json` and mirror it into `review_plan.json` as `source_registry`.

- Interview facts must cite local sources: `transcript_normalized.json`, `interview_events.json`, or evidence frames.
- Technical corrections must cite public traceable sources: papers, official docs, official repositories/docs, course notes, or original blog posts.
- Project ownership, exact work done, experimental numbers, and company-specific claims must cite local video/transcript or user-provided materials. If not sourced, phrase as `建议表达方式`, not as a fact.
- If no reliable source exists, the answer must say `来源不足，建议补材料`. Do not invent citations.
- Use short refs in body, e.g. `[L-q01]`, `[PPO]`, `[DAPO]`.
- Follow-up learning resources are not evidence for what happened in the interview. They should be selected after reading the current transcript/events and should not be hard-coded for a company, team, or candidate.

## Writing Rules

- Write in Chinese unless the user requests another language.
- Keep interviewer questions concrete and close to the original wording.
- Filter greetings, repeated acknowledgements, screen-share logistics, silence hallucinations, and ordinary small talk unless they affect interview signal.
- Evaluate as an interviewer would, but keep the critique short.
- For high-risk technical points, include only the formula/rule needed to fix the answer.
- For code, prefer a compact interview-writeable version, invariant, complexity, and next-time oral script.
- Mark uncertainty rather than pretending diarization or ASR is perfect.

## Visual Evidence Rules

Use screenshots only when they carry evidence value:

- code editor or judge result;
- whiteboard or shared-screen formula;
- architecture diagram;
- table/plot/benchmark;
- system design sketch.

Do not insert random face frames or decorative images. Every included image must have a time provenance footnote on the same page. Use `supporting_files/evidence_frames.json` to record path, timestamp, caption, and reason.

## Bundled Resources

- `assets/interview-review-template.tex`: LaTeX template with `verdictbox`, `riskbox`, `betterbox`, `evidencebox`, `drillbox`, `codebox`, and `questioncard`.
- `offerlens/pipeline.py`: local probing, audio extraction, LaTeX compilation, and validation orchestration.
- `offerlens/render.py`: render `review_plan.json` into Markdown, HTML, and LaTeX.
- `offerlens/cli.py`: command-line entry point (`offerlens init`, `offerlens render`, `offerlens validate`, `offerlens pipeline`, `offerlens sample`).
- `references/data-contracts.md`: JSON contracts for transcript, events, source registry, and review plan.
- `references/report-rubric.md`: scoring dimensions and interviewer-signal interpretation.
- `references/formulas/ppo_grpo_clipping.md`: PPO/GRPO/DAPO clipping formula card.
- `references/formulas/kl_direction_cheatsheet.md`: KL direction and mode/mean-seeking cheatsheet.
- `references/answer_rewrites/project_claim_defense.md`: project claim defense templates.
- `templates/event-schema.json`: interview events JSON schema.
- `templates/report_sections.md`: report section ordering rules.
- `examples/`: non-sensitive transcript → review plan → report smoke-test sample.

## Final Checklist

Before delivery:

- run `offerlens render --workdir <run-dir>` to generate Markdown, HTML, and LaTeX;
- optionally compile PDF with `offerlens render --workdir <run-dir> --compile`;
- run `offerlens validate --workdir <run-dir>`;
- ensure report contains `首页摘要`, `面试官问题与我的回答`, `重点追问复盘`, `代码题复盘`, `高风险技术点速记`, `参考来源`, `后续巩固资料`;
- ensure report does not contain `7天训练计划` or `证据与转写说明`;
- fail on placeholders such as `TODO`, `TBD`, `[在此填写]`, `<<...>>`;
- check every question has `建议答案` and at least one source ref;
- check question coverage against `question_candidates.json` / `interview_events.json`;
- check public sources have URL/citation and local sources have path/event id;
- check `learning_resources` contains 5-8 useful traceable items;
- record commands, fallbacks, and limitations in `supporting_files/build_log.md`.
