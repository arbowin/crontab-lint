"""CLI entry point for the splitter module."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .splitter import split, format_split_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-split",
        description="Split cron expressions into valid and invalid buckets.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        help="Cron expressions to split (include the command field).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Read expressions from a file (one per line).",
    )
    return parser


def _read_file(path: str) -> List[str]:
    lines: List[str] = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                lines.append(line)
    return lines


def main(argv: List[str] | None = None) -> int:
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

    result = split(expressions)
    print(format_split_result(result))
    return 1 if result.invalid_count > 0 else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
