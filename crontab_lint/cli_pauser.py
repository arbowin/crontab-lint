"""CLI for the pauser module."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .pauser import pause, format_pause_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-pause",
        description="Show quiet windows where a cron expression does not run.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        help="Cron expressions to analyse.",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Read expressions from a file (one per line).",
    )
    parser.add_argument(
        "--min-pause",
        type=int,
        default=0,
        metavar="HOURS",
        help="Only report expressions whose longest pause is >= HOURS.",
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


def main(argv: list | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions or [])
    if args.file:
        try:
            expressions.extend(_read_file(args.file))
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help(sys.stderr)
        return 2

    exit_code = 0
    for expr in expressions:
        result = pause(expr)
        if not result.is_valid:
            exit_code = 1
        if result.longest_pause_hours >= args.min_pause:
            print(format_pause_result(result))
            print()
    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
