"""CLI entry-point for the digest sub-tool."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .digester import digest


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-digest",
        description="Produce a compact digest/fingerprint for cron expressions.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Cron expression(s) to digest (e.g. '* * * * * /bin/job').",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Read expressions from FILE (one per line; # lines ignored).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON array.",
    )
    return parser


def _read_file(path: str) -> list[str]:
    lines = Path(path).read_text().splitlines()
    return [l.strip() for l in lines if l.strip() and not l.strip().startswith("#")]


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: list[str] = list(args.expressions or [])
    if args.file:
        try:
            expressions.extend(_read_file(args.file))
        except OSError as exc:
            print(f"Error reading file: {exc}", file=sys.stderr)
            return 2

    if not expressions:
        parser.print_help()
        return 2

    results = [digest(expr) for expr in expressions]

    if args.json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return 0 if all(r.is_valid for r in results) else 1

    exit_code = 0
    for r in results:
        status = "OK" if r.is_valid else "INVALID"
        print(f"[{status}] {r.expression}")
        print(f"  fingerprint : {r.fingerprint}")
        if r.is_valid:
            print(f"  explanation : {r.explanation}")
            print(f"  tags        : {', '.join(r.tags) if r.tags else '-'}")
            print(f"  runs/day    : {r.runs_per_day}")
        else:
            print(f"  error       : {r.error}")
            exit_code = 1

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
