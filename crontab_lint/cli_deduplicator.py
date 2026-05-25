"""CLI entry point for the deduplicator module."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .deduplicator import deduplicate, format_deduplicate_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-dedup",
        description="Remove duplicate cron expressions from a list.",
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="One or more cron expressions to deduplicate.",
        default=[],
    )
    group.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing cron expressions, one per line.",
    )
    parser.add_argument(
        "--unique-only",
        action="store_true",
        help="Print only the unique expressions (no report).",
    )
    return parser


def _read_file(path: str) -> List[str]:
    with open(path) as fh:
        lines = []
        for line in fh:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                lines.append(stripped)
        return lines


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    # Manually check for no args before parsing
    if not argv and len(sys.argv) == 1:
        parser.print_help()
        return 2

    args = parser.parse_args(argv)

    if args.file:
        try:
            expressions = _read_file(args.file)
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2
    else:
        expressions = args.expressions

    if not expressions:
        parser.print_help()
        return 2

    result = deduplicate(expressions)

    if args.unique_only:
        for expr in result.unique_expressions:
            print(expr)
    else:
        print(format_deduplicate_result(result))

    return 1 if result.duplicate_count > 0 else 0


if __name__ == "__main__":
    sys.exit(main())
