# Data Contracts

All files are UTF-8 JSON unless stated otherwise. Examples are fictional and must not contain real interview content, user names, home directories, or company-sensitive details.

## transcript_normalized.json

```json
{
  "segments": [
    {
      "id": 0,
      "start": 72.0,
      "end": 80.0,
      "time": "01:12",
      "speaker": "SPEAKER_00",
      "role": "interviewer",
      "text": "你先介绍一下最近做的项目。"
    }
  ]
}
```

`role` may be empty before role inference. Allowed roles: `interviewer`, `candidate`, `unknown`.

## interview_events.json

Before writing final events, create `question_candidates.json` from transcript segments. It is a high-recall heuristic list and may contain noise:

```json
{
  "candidates": [
    {
      "id": "qc001",
      "segment_id": 12,
      "time": "03:10",
      "text": "这个方案为什么能降低延迟？",
      "confidence": "heuristic"
    }
  ]
}
```

Use it to avoid missing interviewer questions. Final reports should merge adjacent duplicate follow-ups, not compress an entire topic into one card.

```json
{
  "events": [
    {
      "id": "q01",
      "type": "question",
      "start": 72.0,
      "end": 160.0,
      "time_range": "01:12--02:40",
      "interviewer_question": "你先介绍一下最近做的项目。",
      "candidate_answer": "候选人介绍了一个缓存系统优化项目，但没有先说明负责模块和指标。",
      "technical_topics": ["cache", "latency", "experiment design"],
      "evidence_frames": []
    }
  ]
}
```

Event types: `question`, `followup`, `coding`, `project`, `small_talk`, `logistics`.

## evidence_frames.json

```json
{
  "frames": [
    {
      "id": "code-final",
      "artifact_id": "code-final.png",
      "path": "<run-dir>/supporting_files/code-final.png",
      "time": "07:40",
      "time_range": "07:10--08:00",
      "caption": "代码题最终版本。",
      "reason": "Shows code evidence and final result."
    }
  ]
}
```

Only include frames with evidence value. Avoid decorative screenshots and face-only frames. Public reports should display `artifact_id`/time range instead of local absolute paths.

## review_plan.json

For compact sourced reports, set `metadata.report_style = "compact_sourced"` and use:

```json
{
  "metadata": {"report_style": "compact_sourced"},
  "dashboard": {},
  "overview": [],
  "questions": [],
  "technical_remediation": [],
  "coding_reviews": [],
  "learning_resources": [],
  "source_registry": {"sources": []}
}
```

### metadata

Required keys: `title`, `generated_at`, `duration`, `source_video`, `asr_backend`.

Privacy rule: `source_video` should be a basename, placeholder, or user-approved label. Do not place a home-directory path in PDF-visible metadata.

### dashboard

Required keys: `verdict`, `fatal_risks`, `top_deductions`, `top_strengths`, `high_risk_topics`, `next_priorities`, `local_evidence`.

### questions

Compact sourced question item:

```json
{
  "id": "q01",
  "time_range": "01:12--02:40",
  "title": "缓存系统优化项目",
  "question": "你先介绍一下最近做的项目。",
  "question_original": "你先介绍一下最近做的项目。",
  "question_cleaned": "你先介绍一下最近做的项目。",
  "intent": "验证候选人能否把问题、方案、负责范围和效果压缩成清楚主线。",
  "answer_summary": "候选人说明做过缓存优化，但负责边界和实验指标不够靠前。",
  "my_answer_raw": "我最近做的是一个缓存系统优化项目 主要目标是降低核心接口的延迟...",
  "my_answer_cleaned": "我当时主要介绍了缓存系统优化：背景是核心接口延迟比较高，我的做法是先梳理读路径，再把高频但变化不快的数据放到缓存里，并补了命中率、延迟和错误率监控。",
  "answer_source_window": "01:18--02:35",
  "answer_confidence": "medium",
  "suggested_answer": "建议先用一句话说明问题、动作和结果，再补负责模块、指标口径和限制。项目事实只引用本地转写或用户补充材料。",
  "refs": ["L-q01"],
  "importance_label": "key",
  "quality_label": "passable",
  "score": "3/5",
  "score_reason": "回答有有效信息，但表达需要更聚焦。",
  "comment": "方向能过，但要先给贡献和证据。",
  "is_key": true
}
```

Every compact question must have `my_answer_cleaned`, `suggested_answer`, and at least one `refs` item.

Coverage rule: include most substantive interviewer questions. Non-key questions can have a short `suggested_answer`; key questions should set `is_key: true` for deeper review.

### technical_remediation

Each item should include `topic`, `risk`, `rule`, optional `formula_latex`, `symbols`, `how_to_say`, `pitfalls`, and `refs`.

### coding_reviews

Each item should include `problem`, `time_range`, `observed_behavior`, `mistakes`, `standard_code`, `complexity`, `next_script`, `refs`, and optional `evidence`.

### learning_resources

Compact reports end with `后续巩固资料`. Add 5-8 resources that match the topics actually exposed by the interview.

```json
{
  "topic": "缓存系统设计",
  "title": "Caching at Scale",
  "type": "engineering_article",
  "url": "https://example.com/caching-at-scale",
  "why": "用于补齐缓存一致性、失效策略和观测指标的面试表达。",
  "priority": "high",
  "language": "English",
  "duration": "short"
}
```

Rules:
- Required keys: `topic`, `title`, `type`, `why`, `priority`, plus `url` or `citation`.
- Optional keys: `language`, `duration`.
- Acceptable public sources include papers, official docs, official repositories/docs, university/course notes, original blogs, Zhihu articles, YouTube videos, Bilibili videos, and comparable knowledge-sharing pages.
- Learning resources are follow-up study suggestions, not proof of interview facts.
- If no reliable material is available, do not fabricate a resource. Mark the relevant report answer as `来源不足，建议补材料`.

## source_registry.json

`supporting_files/source_registry.json` records local and public evidence. Mirror the same object into compact `review_plan.json`.

```json
{
  "sources": [
    {
      "id": "L-q01",
      "type": "local_event",
      "title": "q01 缓存系统优化项目",
      "artifact_id": "interview_events.json",
      "event_id": "q01",
      "time_range": "01:12--02:40"
    },
    {
      "id": "PY-BISECT",
      "type": "official_docs",
      "title": "Python documentation: bisect",
      "url": "https://docs.python.org/3/library/bisect.html",
      "accessed": "YYYY-MM-DD"
    }
  ]
}
```

Rules:
- local sources need `event_id`, `artifact_id`, or a sanitized relative/basename `path`;
- public sources need `url` or `citation`;
- body refs should use source ids like `[L-q01]` and `[PY-BISECT]`;
- if a reliable public source is unavailable, mark the answer as `来源不足，建议补材料`.
