"""CLI entry point for the crontab syntax highlighter."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

from .highlighter import highlight, format_highlight_result, has_errors


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-highlight",
        description="Syntax-highlight crontab expressions with ANSI colors.",
    )
    p.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expression(s) to highlight.",
    )
    p.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Read expressions from a file (one per line).",
    )
    p.add_argument(
        "--no-legend",
        action="store_true",
        help="Suppress the color legend.",
    )
    return p


def _read_file(path: str) -> list[str]:
    lines = Path(path).read_text().splitlines()
    return [
        line for line in lines
        if line.strip() and not line.strip().startswith("#")
    ]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: list[str] = list(args.expressions)
    if args.file:
        try:
            expressions.extend(_read_file(args.file))
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help(file=sys.stderr)
        return 2

    any_errors = False
    for expr in expressions:
        result = highlight(expr)
        output = format_highlight_result(result)
        if args.no_legend:
            print(result.highlighted)
        else:
            print(output)
        if has_errors(result):
            any_errors = True

    return 1 if any_errors else 0


if __name__ == "__main__":
    sys.exit(main())
