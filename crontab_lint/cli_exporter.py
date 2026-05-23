"""CLI entry-point for exporting lint results to JSON or CSV."""

from __future__ import annotations

import argparse
import sys
from typing import List

from crontab_lint.cli import read_expressions_from_file
from crontab_lint.exporter import to_csv, to_json
from crontab_lint.linter import lint, LintResult


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-export",
        description="Export crontab lint results to JSON or CSV.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expressions to lint and export.",
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        help="File containing crontab expressions (one per line).",
    )
    parser.add_argument(
        "--format",
        choices=["json", "csv"],
        default="json",
        help="Output format (default: json).",
    )
    parser.add_argument(
        "--indent",
        type=int,
        default=2,
        metavar="N",
        help="JSON indentation level (default: 2).",
    )
    return parser


def main(argv: List[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions)

    if args.file:
        try:
            expressions.extend(read_expressions_from_file(args.file))
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help(sys.stderr)
        return 2

    results: List[LintResult] = [lint(expr) for expr in expressions]

    if args.format == "json":
        print(to_json(results, indent=args.indent))
    else:
        print(to_csv(results), end="")

    has_errors = any(not r.validation.valid for r in results)
    return 1 if has_errors else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
