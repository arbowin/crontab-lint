"""CLI entry point for the crontab scorer."""

import argparse
import sys
from typing import List

from .scorer import score, format_score_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-score",
        description="Score crontab expressions by complexity and readability.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expression(s) to score.",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing crontab expressions (one per line).",
    )
    parser.add_argument(
        "--min-score",
        type=int,
        default=0,
        metavar="N",
        help="Exit with code 1 if any expression scores below N.",
    )
    return parser


def _read_file(path: str) -> List[str]:
    expressions: List[str] = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                expressions.append(line)
    return expressions


def main(argv=None) -> int:
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
        parser.print_help()
        return 2

    failed = False
    for expr in expressions:
        result = score(expr)
        print(format_score_result(result))
        print()
        if result.score < args.min_score or not result.is_valid:
            failed = True

    return 1 if failed else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
