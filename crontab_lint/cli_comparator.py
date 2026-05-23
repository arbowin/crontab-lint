"""CLI entry point for comparing crontab expressions for schedule equivalence."""

import argparse
import sys
from typing import List

from .comparator import compare, format_comparison


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-compare",
        description="Detect duplicate or equivalent crontab schedules.",
    )
    parser.add_argument(
        "expressions",
        nargs="*",
        metavar="EXPR",
        help="Crontab expressions to compare (include command).",
    )
    parser.add_argument(
        "-f", "--file",
        metavar="FILE",
        help="Read expressions from a file (one per line, # comments ignored).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output result as JSON.",
    )
    return parser


def _read_file(path: str) -> List[str]:
    expressions = []
    with open(path) as fh:
        for line in fh:
            line = line.strip()
            if line and not line.startswith("#"):
                expressions.append(line)
    return expressions


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

    result = compare(expressions)

    if args.json:
        import json
        data = {
            "has_duplicates": result.has_duplicates(),
            "groups": [
                {"canonical": g.canonical, "expressions": g.expressions}
                for g in result.groups
            ],
            "unresolvable": result.unresolvable,
        }
        print(json.dumps(data, indent=2))
    else:
        print(format_comparison(result))

    return 1 if result.has_duplicates() else 0


if __name__ == "__main__":
    sys.exit(main())
