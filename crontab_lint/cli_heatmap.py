"""CLI entry point for the heatmap subcommand."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .heatmap import build_heatmap, format_heatmap


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-heatmap",
        description="Show a 24x7 activity heatmap for cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="One or more cron expressions.",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Read expressions from a file (one per line).",
    )
    parser.add_argument(
        "--color",
        action="store_true",
        help="Colorize non-zero cells.",
    )
    return parser


def _read_file(path: str) -> List[str]:
    expressions: List[str] = []
    with open(path, "r", encoding="utf-8") as fh:
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
        parser.print_help()
        return 2

    exit_code = 0
    for expr in expressions:
        result = build_heatmap(expr)
        print(format_heatmap(result, use_color=args.color))
        print()
        if not result.is_valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
