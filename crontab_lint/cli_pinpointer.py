"""CLI entry point for the cron expression pinpointer."""

import argparse
import sys
from typing import List

from .pinpointer import pinpoint, format_pinpoint_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-pinpoint",
        description="Identify which fields of a cron expression contain issues.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="One or more cron expressions to pinpoint (e.g. '*/5 * * * * cmd').",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Read expressions from a file (one per line; # comments ignored).",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Only print expressions that have at least one error.",
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


def main(argv=None) -> int:
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

    any_invalid = False
    for expr in expressions:
        result = pinpoint(expr)
        if args.errors_only and not result.fields_with_errors() and result.is_valid:
            continue
        print(format_pinpoint_result(result))
        print()
        if not result.is_valid:
            any_invalid = True

    return 1 if any_invalid else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
