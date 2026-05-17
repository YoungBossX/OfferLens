from __future__ import annotations

import argparse
import shutil
import sys
from importlib import resources
from pathlib import Path

from . import pipeline
from .render import render_all


def ensure_support(workdir: Path) -> Path:
    support = workdir.expanduser().resolve() / "supporting_files"
    support.mkdir(parents=True, exist_ok=True)
    return support


def copy_resource(package_path: str, dest: Path) -> None:
    with resources.files("offerlens").joinpath(package_path).open("rb") as src:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(src.read())


def cmd_init(args: argparse.Namespace) -> int:
    pipeline.init_run(Path(args.workdir), args.input)
    return 0


def cmd_pipeline(args: argparse.Namespace) -> int:
    return pipeline.main(args.pipeline_args)


def cmd_render(args: argparse.Namespace) -> int:
    workdir = Path(args.workdir).expanduser().resolve()
    support = ensure_support(workdir)
    review_plan = Path(args.review_plan).expanduser().resolve() if args.review_plan else support / "review_plan.json"
    outputs = render_all(review_plan, workdir)
    for name, path in outputs.items():
        print(f"{name}: {path}")
    if args.compile:
        pipeline.compile_pdf(outputs["tex"])
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    report = pipeline.validate_report(Path(args.workdir))
    return 0 if report["ok"] else 1


def cmd_sample(args: argparse.Namespace) -> int:
    out = Path(args.out).expanduser().resolve()
    support = ensure_support(out)
    copy_resource("examples/review_plan.sample.json", support / "review_plan.json")
    copy_resource("examples/transcript.sample.json", support / "transcript_normalized.json")
    rc = cmd_render(argparse.Namespace(workdir=str(out), review_plan=None, compile=args.compile))
    if rc:
        return rc
    if not args.no_validate:
        return cmd_validate(argparse.Namespace(workdir=str(out)))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="offerlens", description="Minimal local-first interview review reports.")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_init = sub.add_parser("init", help="Initialize a clean local interview review directory.")
    p_init.add_argument("--workdir", required=True)
    p_init.add_argument("--input")
    p_init.set_defaults(func=cmd_init)

    p_pipeline = sub.add_parser("pipeline", help="Run deterministic local helper steps.")
    p_pipeline.add_argument("pipeline_args", nargs=argparse.REMAINDER)
    p_pipeline.set_defaults(func=cmd_pipeline)

    p_render = sub.add_parser("render", help="Render review_plan.json into Markdown/HTML/LaTeX.")
    p_render.add_argument("--workdir", required=True)
    p_render.add_argument("--review-plan")
    p_render.add_argument("--compile", action="store_true", help="Optionally compile LaTeX with latexmk/xelatex.")
    p_render.set_defaults(func=cmd_render)

    p_validate = sub.add_parser("validate", help="Validate report inputs.")
    p_validate.add_argument("--workdir", required=True)
    p_validate.set_defaults(func=cmd_validate)

    p_sample = sub.add_parser("sample", help="Create a fictional minimal sample report.")
    p_sample.add_argument("--out", required=True)
    p_sample.add_argument("--compile", action="store_true", help="Optionally compile LaTeX with latexmk/xelatex.")
    p_sample.add_argument("--no-validate", action="store_true")
    p_sample.set_defaults(func=cmd_sample)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
