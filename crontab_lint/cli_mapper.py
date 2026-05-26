"""CLI entry point for the mapper module."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .mapper import format_map_result, map_expression


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-map",
        description="Map crontab expressions to (hour, minute) run slots.",
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="Crontab expression(s) to map.",
    )
    group.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing crontab expressions (one per line).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    return parser


def _read_file(path: str) -> List[str]:
    with open(path) as fh:
        return [
            line.strip()
            for line in fh
            if line.strip() and not line.strip().startswith("#")
        ]


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = []
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

    results = [map_expression(expr) for expr in expressions]
    exit_code = 0

    if args.json:
        import json
        print(json.dumps([r.to_dict() for r in results], indent=2))
    else:
        for result in results:
            print(format_map_result(result))
            print()

    if any(not r.is_valid for r in results):
        exit_code = 1

    return exit_code


if __name__ == "__main__":
    sys.exit(main())
