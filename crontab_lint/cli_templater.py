"""CLI entry point for the crontab-lint template browser."""

import argparse
import sys

from crontab_lint.templater import (
    list_templates,
    get_template,
    search_templates,
    format_template,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-templates",
        description="Browse and look up cron expression templates.",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="List all available template names")

    get_parser = subparsers.add_parser("get", help="Show details for a named template")
    get_parser.add_argument("name", help="Template name")

    search_parser = subparsers.add_parser("search", help="Search templates by keyword")
    search_parser.add_argument("keyword", help="Keyword to search for")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 2

    if args.command == "list":
        names = list_templates()
        for name in names:
            print(name)
        return 0

    if args.command == "get":
        tmpl = get_template(args.name)
        if tmpl is None:
            print(f"Unknown template: {args.name}", file=sys.stderr)
            print(f"Use 'list' to see available templates.", file=sys.stderr)
            return 1
        print(format_template(tmpl))
        return 0

    if args.command == "search":
        results = search_templates(args.keyword)
        if not results:
            print(f"No templates matched '{args.keyword}'.")
            return 0
        for tmpl in results:
            print(format_template(tmpl))
            print()
        return 0

    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
