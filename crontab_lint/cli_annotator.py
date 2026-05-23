"""CLI entry-point for the crontab annotator."""

import argparse
import sys
from typing import List, Optional

from crontab_lint.annotator import render_annotated


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-annotate",
        description="Add inline human-readable annotations to crontab expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="Crontab expressions to annotate (reads stdin if omitted).",
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        help="Read expressions from FILE (one per line).",
    )
    parser.add_argument(
        "-c",
        "--column",
        type=int,
        default=60,
        metavar="N",
        help="Column at which to align annotations (default: 60).",
    )
    return parser


def _read_lines(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as fh:
        return [line.rstrip("\n") for line in fh]


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.file:
        try:
            lines = _read_lines(args.file)
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
    elif args.expressions:
        lines = args.expressions
    else:
        lines = [line.rstrip("\n") for line in sys.stdin]

    if not lines:
        parser.print_help(sys.stderr)
        return 2

    print(render_annotated(lines, column=args.column))
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
