"""CLI entry point for crontab-group: group crontab expressions."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .grouper import group, format_group_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-group",
        description="Group crontab expressions by tag or validity.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expressions to group (e.g. '* * * * * cmd').",
    )
    parser.add_argument(
        "--file", "-f",
        metavar="FILE",
        help="Read expressions from a file (one per line).",
    )
    parser.add_argument(
        "--by",
        choices=["tag", "validity"],
        default="tag",
        help="Grouping strategy (default: tag).",
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

    result = group(expressions, by=args.by)
    print(format_group_result(result))

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
