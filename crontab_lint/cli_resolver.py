"""CLI entry point for the crontab resolver."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import List

from .resolver import format_resolve_result, resolve


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-resolve",
        description="Show the next scheduled run times for crontab expressions.",
    )
    group = p.add_mutually_exclusive_group(required=True)
    group.add_argument("expressions", nargs="*", metavar="EXPR", help="Crontab expression(s) to resolve.")
    group.add_argument("-f", "--file", metavar="FILE", help="File containing one expression per line.")
    p.add_argument("-n", "--count", type=int, default=5, metavar="N", help="Number of future runs to show (default: 5).")
    p.add_argument("--format", dest="fmt", default="%Y-%m-%d %H:%M", metavar="FMT", help="strftime format string.")
    return p


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
    args = parser.parse_args(argv)

    if not args.expressions and not args.file:
        parser.print_help()
        return 2

    expressions: List[str]
    if args.file:
        try:
            expressions = _read_file(args.file)
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2
    else:
        expressions = args.expressions

    if not expressions:
        print("No expressions provided.", file=sys.stderr)
        return 2

    now = datetime.now()
    exit_code = 0
    for expr in expressions:
        result = resolve(expr, count=args.count, after=now, fmt=args.fmt)
        print(format_resolve_result(result))
        print()
        if not result.is_valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
