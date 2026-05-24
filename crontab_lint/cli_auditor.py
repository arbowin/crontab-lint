"""CLI entry point for the crontab auditor."""

import argparse
import json
import sys
from typing import List

from .auditor import audit, format_audit_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-audit",
        description="Audit crontab expressions with grade, tags, and frequency info.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expressions to audit (inline).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="File containing crontab expressions (one per line).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON.",
    )
    return parser


def _read_file(path: str) -> List[str]:
    expressions = []
    try:
        with open(path) as fh:
            for line in fh:
                stripped = line.strip()
                if stripped and not stripped.startswith("#"):
                    expressions.append(stripped)
    except OSError as exc:
        print(f"Error reading file: {exc}", file=sys.stderr)
    return expressions


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    expressions: List[str] = list(args.expressions or [])
    if args.file:
        expressions.extend(_read_file(args.file))

    if not expressions:
        parser.print_help()
        return 2

    report = audit(expressions)

    if args.json:
        data = {
            "total": report.total,
            "valid": report.valid_count,
            "invalid": report.invalid_count,
            "entries": [e.to_dict() for e in report.entries],
        }
        print(json.dumps(data, indent=2))
    else:
        print(format_audit_report(report))

    return 0 if report.invalid_count == 0 else 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
