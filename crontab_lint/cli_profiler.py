"""CLI entry point for the crontab profiler."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .profiler import profile


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-profile",
        description="Analyze crontab expressions for run frequency and load.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="One or more crontab expressions to profile (quoted).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Read expressions from a file (one per line, # comments ignored).",
    )
    parser.add_argument(
        "--warn-only",
        action="store_true",
        help="Only print entries that carry warnings.",
    )
    return parser


def _read_file(path: str) -> List[str]:
    expressions: List[str] = []
    try:
        with open(path, "r", encoding="utf-8") as fh:
            for line in fh:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    expressions.append(stripped)
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
    return expressions


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions)
    if args.file:
        expressions.extend(_read_file(args.file))

    if not expressions:
        parser.print_help()
        return 2

    exit_code = 0
    for expr in expressions:
        result = profile(expr)
        if args.warn_only and not result.warnings:
            continue
        status = "OK" if result.is_valid else "INVALID"
        print(f"[{status}] {expr!r}")
        if result.is_valid:
            print(f"  Frequency : {result.frequency_label}")
            print(f"  Runs/day  : {result.runs_per_day}")
            print(f"  Runs/week : {result.runs_per_week}")
        for w in result.warnings:
            print(f"  WARNING   : {w}")
        if not result.is_valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
