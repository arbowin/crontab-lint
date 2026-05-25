"""CLI entry point for the cron expression predictor."""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from typing import List, Optional

from .predictor import predict, format_predict_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-predict",
        description="Predict when a cron expression will run within a time window.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPRESSION",
        help="One or more cron expressions (with command).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing cron expressions (one per line).",
    )
    parser.add_argument(
        "-w", "--window",
        type=int,
        default=24,
        metavar="HOURS",
        help="Prediction window in hours (default: 24).",
    )
    parser.add_argument(
        "--start",
        metavar="YYYY-MM-DDTHH:MM",
        help="Window start time (default: now).",
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

    window_start: Optional[datetime] = None
    if args.start:
        try:
            window_start = datetime.strptime(args.start, "%Y-%m-%dT%H:%M")
        except ValueError:
            print("Invalid --start format. Use YYYY-MM-DDTHH:MM.", file=sys.stderr)
            return 2

    exit_code = 0
    for expr in expressions:
        result = predict(expr, window_start=window_start, window_hours=args.window)
        print(format_predict_result(result))
        print()
        if not result.is_valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
