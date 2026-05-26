"""CLI entry point for the balancer module."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .balancer import balance, format_balance_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-balance",
        description="Detect uneven load distribution across hours for cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        help="Cron expressions to analyse (inline).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing cron expressions (one per line).",
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
            print(f"ERROR: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help(sys.stderr)
        return 2

    result = balance(expressions)
    print(format_balance_result(result))
    return 0 if result.is_valid else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
