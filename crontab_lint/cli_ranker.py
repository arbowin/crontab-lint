"""CLI entry point for ranking crontab expressions."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .ranker import rank, format_rank_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-rank",
        description="Rank crontab expressions by frequency or complexity.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "expressions",
        nargs="*",
        default=None,
        help="Crontab expressions to rank.",
    )
    group.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing one crontab expression per line.",
    )
    parser.add_argument(
        "--key",
        choices=["frequency", "complexity"],
        default="frequency",
        help="Ranking strategy (default: frequency).",
    )
    return parser


def _read_file(path: str) -> List[str]:
    expressions = []
    with open(path) as fh:
        for line in fh:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                expressions.append(stripped)
    return expressions


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.file:
        try:
            expressions = _read_file(args.file)
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2
    else:
        expressions = args.expressions or []

    if not expressions:
        print("No expressions provided.", file=sys.stderr)
        return 2

    try:
        result = rank(expressions, key=args.key)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2

    print(format_rank_result(result))
    return 0


if __name__ == "__main__":
    sys.exit(main())
