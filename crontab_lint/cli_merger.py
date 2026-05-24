"""CLI entry point for the crontab merger tool."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Tuple

from .merger import merge, format_merge_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-merge",
        description="Merge multiple crontab files, deduplicating equivalent expressions.",
    )
    parser.add_argument(
        "files",
        nargs="*",
        metavar="FILE",
        help="Crontab files to merge. Use '-' for stdin.",
    )
    parser.add_argument(
        "-e",
        "--expression",
        action="append",
        dest="expressions",
        metavar="EXPR",
        help="Inline expression to include (may be repeated).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show duplicate-of details.",
    )
    parser.add_argument(
        "--output",
        metavar="FILE",
        help="Write unique valid expressions to FILE.",
    )
    return parser


def _read_file(path: str) -> List[str]:
    if path == "-":
        return [line.rstrip("\n") for line in sys.stdin]
    return Path(path).read_text().splitlines()


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.files and not args.expressions:
        parser.print_help()
        return 2

    sources: List[Tuple[str, str]] = []

    for expr in args.expressions or []:
        sources.append((expr, "<inline>"))

    for filepath in args.files or []:
        try:
            lines = _read_file(filepath)
        except OSError as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        label = filepath
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                sources.append((stripped, label))

    result = merge(sources)
    print(format_merge_result(result, verbose=args.verbose))

    if args.output:
        unique_exprs = [
            e.expression for e in result.unique_entries if e.result.valid
        ]
        Path(args.output).write_text("\n".join(unique_exprs) + "\n")

    return 1 if result.has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
