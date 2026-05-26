"""CLI entry point for the crontab estimator."""

import argparse
import sys
from typing import List, Optional

from .estimator import estimate, format_estimate_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-estimate",
        description="Estimate average interval and runs-per-day for cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="Cron expression(s) to estimate (with command).",
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


def main(argv: Optional[List[str]] = None) -> int:
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
        result = estimate(expr)
        print(format_estimate_result(result))
        print()
        if not result.is_valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
