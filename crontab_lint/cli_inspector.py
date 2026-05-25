"""CLI entry point for the inspector module."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .inspector import inspect


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="crontab-inspect",
        description="Deep field-level inspection of cron expressions.",
    )
    p.add_argument("expressions", nargs="*", help="Cron expressions to inspect")
    p.add_argument("-f", "--file", help="File containing cron expressions (one per line)")
    p.add_argument("--json", dest="as_json", action="store_true", help="Output as JSON")
    return p


def _read_file(path: str) -> list[str]:
    lines = []
    for line in Path(path).read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            lines.append(stripped)
    return lines


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
        parser.print_help(sys.stderr)
        return 2

    results = [inspect(expr) for expr in expressions]
    exit_code = 0

    if args.as_json:
        print(json.dumps([r.to_dict() for r in results], indent=2))
        return exit_code

    for r in results:
        print(f"Expression : {r.expression}")
        if not r.is_valid:
            print(f"  ERROR    : {r.error}")
            exit_code = 1
        else:
            for f in r.fields:
                vals = f.values if f.values else "(all)"
                print(f"  {f.name:<14} [{f.kind:<8}]  {f.raw:<12}  values={vals}")
                print(f"               note: {f.note}")
        print()

    return exit_code


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
