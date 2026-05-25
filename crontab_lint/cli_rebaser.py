"""CLI entry point for the cron expression rebaser."""

import argparse
import sys
from typing import List, Optional

from .rebaser import rebase, format_rebase_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-rebase",
        description="Shift cron expression minute/hour fields by a fixed offset.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="Cron expressions to rebase (including command).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing cron expressions (one per line).",
    )
    parser.add_argument(
        "-m", "--minute-offset",
        type=int,
        default=0,
        metavar="N",
        help="Shift minute field by N (default: 0).",
    )
    parser.add_argument(
        "-H", "--hour-offset",
        type=int,
        default=0,
        metavar="N",
        help="Shift hour field by N (default: 0).",
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


def main(argv: Optional[List[str]] = None) -> int:
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
        parser.print_help(sys.stderr)
        return 2

    exit_code = 0
    for expr in expressions:
        result = rebase(expr, minute_offset=args.minute_offset, hour_offset=args.hour_offset)
        print(format_rebase_result(result))
        if len(expressions) > 1:
            print()
        if not result.is_valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
