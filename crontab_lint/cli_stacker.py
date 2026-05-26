"""CLI entry point for the stacker module."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .stacker import stack, format_stack_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-stacker",
        description="Find overlapping run times across multiple cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        help="Cron expressions to stack (inline).",
    )
    parser.add_argument(
        "-f", "--file",
        dest="file",
        default=None,
        help="File containing cron expressions (one per line).",
    )
    parser.add_argument(
        "--hours",
        type=int,
        default=24,
        help="Window size in hours to check for overlaps (default: 24).",
    )
    return parser


def _read_file(path: str) -> List[str]:
    expressions: List[str] = []
    with open(path) as fh:
        for line in fh:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                expressions.append(stripped)
    return expressions


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions)

    if args.file:
        try:
            expressions.extend(_read_file(args.file))
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help()
        return 2

    result = stack(expressions, hours=args.hours)
    print(format_stack_result(result))

    if not result.is_valid:
        return 1
    if result.has_overlaps():
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
