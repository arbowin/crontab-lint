"""CLI entry point for the crontab segmenter."""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List

from .segmenter import segment, format_segment_result


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-segment",
        description="Break a crontab expression into time-of-day segments.",
    )
    p.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expression(s) to segment.",
    )
    p.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing crontab expressions (one per line).",
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    return p


def _read_file(path: str) -> List[str]:
    lines = []
    for line in Path(path).read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
    return lines


def main(argv: List[str] | None = None) -> int:
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
        parser.print_help(sys.stderr)
        return 2

    if args.json:
        import json
        output = []
        for expr in expressions:
            r = segment(expr)
            output.append({
                "expression": r.expression,
                "is_valid": r.is_valid,
                "error": r.error,
                "segments": [s.to_dict() for s in r.segments],
                "total_runs": r.total_runs(),
            })
        print(json.dumps(output, indent=2))
        return 0

    exit_code = 0
    for expr in expressions:
        r = segment(expr)
        print(format_segment_result(r))
        print()
        if not r.is_valid:
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
