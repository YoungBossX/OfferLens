from __future__ import annotations

import html
import json
import re
from datetime import date
from pathlib import Path
from typing import Any

SPECIALS = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def md_escape(text: Any) -> str:
    return "" if text is None else str(text).strip()


def tex_escape(text: Any) -> str:
    raw = "" if text is None else str(text)
    return "".join(SPECIALS.get(ch, ch) for ch in raw)


def answer_text(q: dict[str, Any]) -> str:
    return (
        q.get("my_answer_cleaned")
        or q.get("my_answer")
        or q.get("answer_cleaned")
        or q.get("answer_summary")
        or ""
    )


def list_block(items: Any) -> str:
    if not items:
        return "- 未记录。"
    if isinstance(items, str):
        return f"- {items}"
    return "\n".join(f"- {md_escape(item)}" for item in items)


def render_markdown(plan: dict[str, Any]) -> str:
    meta = plan.get("metadata") or {}
    dashboard = plan.get("dashboard") or {}
    title = meta.get("title") or "面试复盘报告"
    lines: list[str] = [f"# {title}", ""]
    lines.append(f"生成日期：{meta.get('generated_at') or date.today().isoformat()}  ")
    if meta.get("duration"):
        lines.append(f"面试时长：{meta.get('duration')}  ")
    if meta.get("source_video"):
        lines.append(f"本地来源：{Path(str(meta.get('source_video'))).name}  ")
    lines.append("")

    if dashboard:
        lines.extend(["## 首页摘要", ""])
        for key, label in [
            ("verdict", "总体判断"),
            ("fatal_risks", "主要风险"),
            ("local_evidence", "本地证据"),
        ]:
            if dashboard.get(key):
                lines.append(f"**{label}**：{dashboard[key]}")
                lines.append("")
        for key, label in [
            ("top_strengths", "亮点"),
            ("top_deductions", "扣分点"),
            ("high_risk_topics", "高风险主题"),
            ("next_priorities", "下一步优先级"),
        ]:
            if dashboard.get(key):
                lines.extend([f"### {label}", "", list_block(dashboard.get(key)), ""])

    overview = plan.get("overview")
    if overview:
        lines.extend(["## 面试概览", "", list_block(overview), ""])

    questions = plan.get("questions") or []
    lines.extend(["## 面试官问题与我的回答", ""])
    if not questions:
        lines.append("暂无问题记录。")
    for idx, q in enumerate(questions, 1):
        title = q.get("title") or f"问题 {idx}"
        lines.extend([
            f"### {idx}. {title}",
            "",
            f"- 时间：{q.get('time_range') or '未记录'}",
            f"- 质量：{q.get('quality_label') or q.get('level') or '未评级'}",
            f"- 分数：{q.get('score') or '未评分'}",
            "",
            f"**面试官问题**：{q.get('question_cleaned') or q.get('question') or ''}",
            "",
            f"**我的回答**：{answer_text(q)}",
            "",
            f"**建议答案**：{q.get('suggested_answer') or q.get('standard_answer') or ''}",
            "",
        ])
        refs = q.get("refs") or q.get("source_refs") or []
        if refs:
            lines.extend([f"**来源**：{', '.join(map(str, refs))}", ""])
        if q.get("comment"):
            lines.extend([f"**一句评价**：{q.get('comment')}", ""])

    resources = plan.get("learning_resources") or []
    if resources:
        lines.extend(["## 后续巩固资料", ""])
        for item in resources:
            if isinstance(item, dict):
                title = item.get("title") or item.get("topic") or "资料"
                why = item.get("why") or ""
                url = item.get("url") or item.get("citation") or ""
                line = f"- **{title}**"
                if why:
                    line += f"：{why}"
                if url:
                    line += f"  \n  来源：{url}"
                lines.append(line)
            else:
                lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def render_html(markdown_text: str, title: str) -> str:
    # Minimal Markdown-to-HTML renderer sufficient for the generated report.
    body: list[str] = []
    in_list = False
    for raw in markdown_text.splitlines():
        line = raw.rstrip()
        if not line:
            if in_list:
                body.append("</ul>")
                in_list = False
            continue
        if line.startswith("# "):
            body.append(f"<h1>{html.escape(line[2:])}</h1>")
        elif line.startswith("## "):
            body.append(f"<h2>{html.escape(line[3:])}</h2>")
        elif line.startswith("### "):
            body.append(f"<h3>{html.escape(line[4:])}</h3>")
        elif line.startswith("- "):
            if not in_list:
                body.append("<ul>")
                in_list = True
            body.append(f"<li>{html.escape(line[2:])}</li>")
        else:
            if in_list:
                body.append("</ul>")
                in_list = False
            text = html.escape(line)
            text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
            body.append(f"<p>{text}</p>")
    if in_list:
        body.append("</ul>")
    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8" />
<title>{html.escape(title)}</title>
<style>
body {{ max-width: 920px; margin: 40px auto; padding: 0 24px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif; line-height: 1.75; color: #1f2937; }}
h1 {{ border-bottom: 2px solid #111827; padding-bottom: .3em; }}
h2 {{ margin-top: 2em; border-bottom: 1px solid #e5e7eb; padding-bottom: .2em; }}
h3 {{ margin-top: 1.6em; }}
li {{ margin: .25em 0; }}
strong {{ color: #111827; }}
</style>
</head>
<body>
{''.join(body)}
</body>
</html>
"""


def render_latex(plan: dict[str, Any]) -> str:
    meta = plan.get("metadata") or {}
    title = tex_escape(meta.get("title") or "面试复盘报告")
    body: list[str] = []
    if plan.get("overview"):
        body.append(r"\section{面试概览}")
        body.append(r"\begin{itemize}")
        for item in plan.get("overview") or []:
            body.append(r"\item " + tex_escape(item))
        body.append(r"\end{itemize}")

    body.append(r"\section{面试官问题与我的回答}")
    for idx, q in enumerate(plan.get("questions") or [], 1):
        body.append(rf"\subsection{{{idx}. {tex_escape(q.get('title') or '问题')}}}")
        body.append(rf"\textbf{{时间}}：{tex_escape(q.get('time_range') or '未记录')}\\")
        body.append(rf"\textbf{{质量}}：{tex_escape(q.get('quality_label') or '未评级')}\quad \textbf{{分数}}：{tex_escape(q.get('score') or '未评分')}\\")
        body.append(rf"\textbf{{面试官问题}}：{tex_escape(q.get('question_cleaned') or q.get('question') or '')}")
        body.append("")
        body.append(rf"\textbf{{我的回答}}：{tex_escape(answer_text(q))}")
        body.append("")
        body.append(rf"\textbf{{建议答案}}：{tex_escape(q.get('suggested_answer') or q.get('standard_answer') or '')}")
        body.append("")

    return "\\documentclass[11pt]{ctexart}\n\\usepackage[a4paper,margin=2.2cm]{geometry}\n\\usepackage{hyperref}\n\\title{" + title + "}\n\\author{OfferLens}\n\\date{" + tex_escape(meta.get("generated_at") or date.today().isoformat()) + "}\n\\begin{document}\n\\maketitle\n" + "\n\n".join(body) + "\n\\end{document}\n"


def render_all(review_plan: Path, workdir: Path) -> dict[str, Path]:
    plan = read_json(review_plan)
    meta = plan.get("metadata") or {}
    title = str(meta.get("title") or "面试复盘报告")
    support = workdir / "supporting_files"
    support.mkdir(parents=True, exist_ok=True)

    md = render_markdown(plan)
    html_text = render_html(md, title)
    tex = render_latex(plan)

    md_path = workdir / "interview_review.md"
    html_path = workdir / "interview_review.html"
    tex_path = support / "interview_review.tex"
    refs_path = workdir / "references.md"

    md_path.write_text(md, encoding="utf-8")
    html_path.write_text(html_text, encoding="utf-8")
    tex_path.write_text(tex, encoding="utf-8")
    refs_path.write_text(render_references(plan), encoding="utf-8")
    return {"markdown": md_path, "html": html_path, "tex": tex_path, "references": refs_path}


def render_references(plan: dict[str, Any]) -> str:
    sources = ((plan.get("source_registry") or {}).get("sources") or [])
    lines = ["# References", ""]
    if not sources:
        return "# References\n\n暂无来源。\n"
    for src in sources:
        sid = src.get("id") or "UNKNOWN"
        title = src.get("title") or sid
        detail = src.get("url") or src.get("artifact_id") or src.get("citation") or ""
        lines.append(f"- [{sid}] {title}" + (f" — {detail}" if detail else ""))
    return "\n".join(lines) + "\n"
