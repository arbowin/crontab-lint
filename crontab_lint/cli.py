"""Command-line interface for crontab-lint."""

import argparse
import sys

from crontab_lint.linter import lint, lint_many
from crontab_lint.formatter import format_result, format_many


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-lint",
        description="Static analyzer and validator for crontab expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="One or more crontab expressions to lint (e.g. '*/5 * * * * /cmd').",
    )
    parser.add_argument(
        "-f",
        "--file",
        metavar="FILE",
        help="Read crontab expressions from a file (one per line).",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Show explanation even when there are no issues.",
    )
    return parser


def read_expressions_from_file(path: str) -> list[str]:
    """Read non-empty, non-comment lines from a file."""
    with open(path, "r", encoding="utf-8") as fh:
        return [
            line.rstrip("\n")
            for line in fh
            if line.strip() and not line.lstrip().startswith("#")
        ]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: list[str] = list(args.expressions)

    if args.file:
        try:
            expressions.extend(read_expressions_from_file(args.file))
        except OSError as exc:
            print(f"crontab-lint: error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help(sys.stderr)
        return 2

    if len(expressions) == 1:
        result = lint(expressions[0])
        print(format_result(result, verbose=args.verbose))
        return 0 if result.valid else 1
    else:
        results = lint_many(expressions)
        print(format_many(results, verbose=args.verbose))
        has_error = any(not r.valid for r in results)
        return 1 if has_error else 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
