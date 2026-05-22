"""CLI entry-point for diffing two crontab expressions."""

import argparse
import sys

from .differ import diff
from .parser import ParseError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-diff",
        description="Compare two crontab expressions and show what changed.",
    )
    parser.add_argument("old", help="Original crontab expression")
    parser.add_argument("new", help="New crontab expression")
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    return parser


def _colorize(text: str, code: str, no_color: bool) -> str:
    if no_color:
        return text
    return f"\033[{code}m{text}\033[0m"


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        result = diff(args.old, args.new)
    except ParseError as exc:
        print(
            _colorize(f"Parse error: {exc}", "31", getattr(args, "no_color", False)),
            file=sys.stderr,
        )
        return 2

    no_color = args.no_color

    if not result.has_changes:
        print(_colorize("No changes detected.", "32", no_color))
        return 0

    if result.command_changed:
        old_cmd = args.old.split(None, 5)[-1] if len(args.old.split()) > 5 else ""
        new_cmd = args.new.split(None, 5)[-1] if len(args.new.split()) > 5 else ""
        print(
            _colorize(f"command: '{old_cmd}' -> '{new_cmd}'", "33", no_color)
        )

    for fd in result.field_diffs:
        header = _colorize(
            f"{fd.field}: '{fd.old_value}' -> '{fd.new_value}'", "33", no_color
        )
        old_line = _colorize(f"  was: {fd.old_explanation}", "31", no_color)
        new_line = _colorize(f"  now: {fd.new_explanation}", "32", no_color)
        print(header)
        print(old_line)
        print(new_line)

    return 1


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
