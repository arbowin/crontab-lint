"""CLI entry point for the batch linter."""
from __future__ import annotations

import argparse
import sys
from typing import List

from .batcher import batch, format_batch_result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-batch",
        description="Lint multiple cron expressions in one pass.",
    )
    p.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Cron expressions to lint (e.g. '* * * * * cmd').",
    )
    p.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing one cron expression per line (comments and blank lines ignored).",
    )
    p.add_argument(
        "--stop-on-error",
        action="store_true",
        default=False,
        help="Stop processing after the first invalid expression.",
    )
    p.add_argument(
        "--summary",
        action="store_true",
        default=False,
        help="Print only the summary line, not per-expression details.",
    )
    return p


def _read_file(path: str) -> List[str]:
    with open(path) as fh:
        lines = []
        for line in fh:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                lines.append(stripped)
    return lines


def main(argv=None) -> int:
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

    result = batch(expressions, stop_on_error=args.stop_on_error)

    if args.summary:
        print(f"Total: {result.total}  Valid: {result.valid_count}  Invalid: {result.invalid_count}")
    else:
        print(format_batch_result(result))

    return 0 if result.invalid_count == 0 else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
