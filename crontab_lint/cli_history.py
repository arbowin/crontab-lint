"""CLI for crontab-lint history tracking."""

from __future__ import annotations

import argparse
import sys

from crontab_lint.history import load_history, record, save_history

DEFAULT_HISTORY_FILE = ".crontab_lint_history.json"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-history",
        description="Track lint history for crontab expressions.",
    )
    sub = parser.add_subparsers(dest="command")

    add_cmd = sub.add_parser("add", help="Lint and record a crontab expression.")
    add_cmd.add_argument("expression", help="Crontab expression to record.")
    add_cmd.add_argument("--file", default=DEFAULT_HISTORY_FILE, help="History file path.")

    show_cmd = sub.add_parser("show", help="Show recorded history.")
    show_cmd.add_argument("--file", default=DEFAULT_HISTORY_FILE, help="History file path.")
    show_cmd.add_argument("--last", type=int, default=10, help="Number of recent entries.")
    show_cmd.add_argument("--only-invalid", action="store_true", help="Show only invalid entries.")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 2

    if args.command == "add":
        history = load_history(args.file)
        entry = record(args.expression, history)
        save_history(history, args.file)
        status = "valid" if entry.valid else "invalid"
        print(f"Recorded [{status}]: {entry.expression}")
        if entry.explanation:
            print(f"  {entry.explanation}")
        return 0 if entry.valid else 1

    if args.command == "show":
        history = load_history(args.file)
        entries = history.filter_invalid() if args.only_invalid else history.last(args.last)
        if not entries:
            print("No history entries found.")
            return 0
        for e in entries:
            status = "OK" if e.valid else "FAIL"
        for e in entries:
            status = "OK" if e.valid else "FAIL"
            errors = f"{e.error_count}E/{e.warning_count}W"
            print(f"[{status}] {errors:>8}  {e.expression:<30}  {e.timestamp}")
        return 0

    return 2


if __name__ == "__main__":
    raise SystemExit(main())
