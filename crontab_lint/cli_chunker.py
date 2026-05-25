"""CLI entry point for the chunker module."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from .chunker import chunk, format_chunk_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-chunk",
        description="Split cron expressions into chunks and summarise each.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Cron expressions to chunk (inline).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing one cron expression per line.",
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=10,
        metavar="N",
        help="Number of expressions per chunk (default: 10).",
    )
    return parser


def _read_file(path: str) -> List[str]:
    lines = Path(path).read_text().splitlines()
    return [
        line.strip()
        for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions or [])

    if args.file:
        try:
            expressions += _read_file(args.file)
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help()
        return 2

    result = chunk(expressions, chunk_size=args.size)
    print(format_chunk_result(result))

    if result.has_error:
        return 2
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
