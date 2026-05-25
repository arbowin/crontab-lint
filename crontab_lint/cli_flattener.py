"""CLI entry point for the crontab-lint flattener."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .flattener import flatten, format_flatten_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-flatten",
        description="Expand a cron expression into all (minute, hour) run-time pairs.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Cron expression(s) to flatten (include command field).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing one cron expression per line.",
    )
    parser.add_argument(
        "-l", "--limit",
        type=int,
        default=20,
        metavar="N",
        help="Maximum number of pairs to display per expression (default: 20).",
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
        result = flatten(expr)
        print(format_flatten_result(result, limit=args.limit))
        print()
        if not result.is_valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
