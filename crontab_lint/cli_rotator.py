"""CLI entry point for the cron expression rotator."""

import argparse
import sys
from typing import List

from .rotator import rotate, format_rotate_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-rotate",
        description="Rotate cron expression minute offsets to spread load.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        help="Cron expressions to rotate (each as a quoted string).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing cron expressions (one per line).",
    )
    parser.add_argument(
        "--step",
        type=int,
        default=5,
        metavar="N",
        help="Minute offset step between consecutive expressions (default: 5).",
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
        parser.print_help(sys.stderr)
        return 2

    result = rotate(expressions, step=args.step)
    print(format_rotate_result(result))

    return 1 if result.invalid_count > 0 else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
