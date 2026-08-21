"""Argparse CLI for Video Factory."""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

from .exceptions import VideoFactoryError
from .project import clean_project, create_project
from .render import render_project
from .timeline import timeline_as_dicts
from .validate import ValidationResult, validate_project


def _show_validation(result: ValidationResult) -> None:
    if result.config:
        print(f"Project: {result.config.project.title}")
        print(f"Timeline du kien: {result.duration:.3f} giay")
        for item in timeline_as_dicts(result.config.scenes):
            print(f"  {item['id']:<24} {item['start']:>7.3f} -> {item['end']:>7.3f}")
    for warning in result.warnings:
        print(f"CANH BAO: {warning}")
    for error in result.errors:
        print(f"LOI: {error}", file=sys.stderr)
    print("Project hop le." if result.ok else f"Phat hien {len(result.errors)} loi.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="video_factory", description="XV2DA Video Factory V1 - dung video doc bang FFmpeg")
    parser.add_argument("--debug", action="store_true", help="Hien traceback khi co loi")
    sub = parser.add_subparsers(dest="command", required=True)
    new = sub.add_parser("new-project", help="Tao project moi tu template")
    new.add_argument("name")
    validate = sub.add_parser("validate", help="Kiem tra YAML, media va moi truong")
    validate.add_argument("project", type=Path)
    render = sub.add_parser("render", help="Validate va render master/preview")
    render.add_argument("project", type=Path)
    render.add_argument("--overwrite", action="store_true")
    render.add_argument("--dry-run", action="store_true")
    clean = sub.add_parser("clean", help="Xoa file trung gian trong work/")
    clean.add_argument("project", type=Path)
    clean.add_argument("--include-output", action="store_true")
    clean.add_argument("--yes", action="store_true", help="Khong hoi xac nhan")
    return parser


def run(args: argparse.Namespace) -> int:
    if args.command == "new-project":
        print(f"Da tao project: {create_project(args.name)}")
        return 0
    if args.command == "validate":
        result = validate_project(args.project)
        _show_validation(result)
        return 0 if result.ok else 2
    if args.command == "render":
        result = validate_project(args.project)
        _show_validation(result)
        if not result.ok:
            return 2
        report = render_project(args.project, result, overwrite=args.overwrite, dry_run=args.dry_run)
        if args.dry_run:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            config = result.config
            assert config
            print(f"Master: {(args.project / config.outputs.master.file).resolve()}")
            if config.outputs.preview.enabled:
                print(f"Preview: {(args.project / config.outputs.preview.file).resolve()}")
            print(f"Report: {(args.project / config.outputs.report.file).resolve()}")
        return 0
    if args.command == "clean":
        if args.include_output and not args.yes:
            answer = input("Xoa ca output/? Nhap YES de xac nhan: ")
            if answer != "YES":
                print("Da huy; khong xoa file nao.")
                return 1
        clean_project(args.project, include_output=args.include_output)
        print("Da don work/" + (" va output/." if args.include_output else "."))
        return 0
    return 1


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    try:
        raise SystemExit(run(args))
    except VideoFactoryError as error:
        print(f"LOI: {error}", file=sys.stderr)
        if args.debug:
            traceback.print_exc()
        raise SystemExit(1) from error

