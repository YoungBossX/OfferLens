from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .render import read_json, render_all, write_json

SUPPORT_DIR_NAME = "supporting_files"


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def run(cmd: list[str]) -> int:
    print("+ " + " ".join(cmd), flush=True)
    return subprocess.call(cmd)


def require_bin(name: str) -> str:
    path = shutil.which(name)
    if not path:
        raise SystemExit(f"missing required executable: {name}")
    return path


def ensure_support(workdir: Path) -> Path:
    support = workdir.expanduser().resolve() / SUPPORT_DIR_NAME
    support.mkdir(parents=True, exist_ok=True)
    return support


def init_run(workdir: Path, input_path: str | None = None) -> None:
    workdir = workdir.expanduser().resolve()
    support = ensure_support(workdir)
    metadata = {
        "created_at": now_iso(),
        "input": Path(input_path).name if input_path else None,
        "privacy": "local-first; raw media is not copied by default",
    }
    write_json(support / "run_metadata.json", metadata)
    if not (support / "review_plan.json").exists():
        write_json(
            support / "review_plan.json",
            {
                "metadata": {
                    "title": "面试复盘报告",
                    "generated_at": datetime.now().date().isoformat(),
                    "source_video": Path(input_path).name if input_path else "",
                },
                "overview": ["请将 ASR 和问题抽取结果整理到 questions 字段。"],
                "questions": [],
                "source_registry": {"sources": []},
            },
        )
    if not (support / "transcript_normalized.json").exists():
        write_json(support / "transcript_normalized.json", {"segments": []})
    print(f"initialized: {workdir}")


def probe(input_path: Path, out_dir: Path) -> None:
    require_bin("ffprobe")
    out_dir.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffprobe",
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        str(input_path),
    ]
    result = subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    data = json.loads(result.stdout or "{}")
    if isinstance(data.get("format"), dict):
        data["format"]["filename"] = Path(str(data["format"].get("filename", ""))).name
    write_json(out_dir / "media_probe.json", data)
    print(out_dir / "media_probe.json")


def extract_audio(input_path: Path, audio_path: Path) -> None:
    require_bin("ffmpeg")
    audio_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(input_path),
        "-vn",
        "-ac",
        "1",
        "-ar",
        "16000",
        str(audio_path),
    ]
    raise_code = run(cmd)
    if raise_code:
        raise SystemExit(raise_code)


def compile_pdf(tex_path: Path) -> None:
    latexmk = shutil.which("latexmk")
    xelatex = shutil.which("xelatex")
    if latexmk:
        rc = run([latexmk, "-xelatex", "-interaction=nonstopmode", str(tex_path)])
    elif xelatex:
        rc = run([xelatex, "-interaction=nonstopmode", str(tex_path)])
    else:
        raise SystemExit("missing latexmk/xelatex; report has been rendered to .md/.html/.tex")
    if rc:
        raise SystemExit(rc)


def validate_report(workdir: Path) -> dict[str, Any]:
    workdir = workdir.expanduser().resolve()
    support = ensure_support(workdir)
    plan_path = support / "review_plan.json"
    if not plan_path.exists():
        raise SystemExit(f"missing: {plan_path}")
    plan = read_json(plan_path)
    questions = plan.get("questions") or []
    warnings: list[str] = []
    if not questions:
        warnings.append("questions is empty")
    for idx, q in enumerate(questions, 1):
        if not (q.get("question") or q.get("question_cleaned")):
            warnings.append(f"question {idx}: missing question text")
        if not (q.get("my_answer_cleaned") or q.get("answer_summary")):
            warnings.append(f"question {idx}: missing answer text")
        if not q.get("refs"):
            warnings.append(f"question {idx}: missing refs")
    report = {
        "ok": not warnings,
        "question_count": len(questions),
        "warnings": warnings,
        "checked_at": now_iso(),
    }
    write_json(support / "quality_report.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="offerlens pipeline")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("init-run")
    p.add_argument("--workdir", required=True)
    p.add_argument("--input")

    p = sub.add_parser("probe")
    p.add_argument("--input", required=True)
    p.add_argument("--out-dir", required=True)

    p = sub.add_parser("extract-audio")
    p.add_argument("--input", required=True)
    p.add_argument("--audio", required=True)

    p = sub.add_parser("compile-pdf")
    p.add_argument("--tex", required=True)

    p = sub.add_parser("validate-report")
    p.add_argument("--workdir", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.cmd == "init-run":
        init_run(Path(args.workdir), args.input)
    elif args.cmd == "probe":
        probe(Path(args.input), Path(args.out_dir))
    elif args.cmd == "extract-audio":
        extract_audio(Path(args.input), Path(args.audio))
    elif args.cmd == "compile-pdf":
        compile_pdf(Path(args.tex))
    elif args.cmd == "validate-report":
        validate_report(Path(args.workdir))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
