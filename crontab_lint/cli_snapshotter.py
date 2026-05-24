"""CLI for the snapshotter: take or compare crontab snapshots."""

from __future__ import annotations

import argparse
import sys
from typing import List

from .snapshotter import (
    take_snapshot,
    diff_snapshots,
    save_snapshot,
    load_snapshot,
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-snapshot",
        description="Capture and compare crontab lint snapshots.",
    )
    sub = parser.add_subparsers(dest="command")

    take_p = sub.add_parser("take", help="Take a new snapshot")
    take_p.add_argument("expressions", nargs="+", help="Cron expressions to snapshot")
    take_p.add_argument("--output", "-o", required=True, help="Path to save snapshot JSON")

    diff_p = sub.add_parser("diff", help="Diff two snapshots")
    diff_p.add_argument("old", help="Path to old snapshot JSON")
    diff_p.add_argument("new", help="Path to new snapshot JSON")

    return parser


def _read_file(path: str) -> List[str]:
    with open(path, "r", encoding="utf-8") as fh:
        lines = []
        for line in fh:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                lines.append(stripped)
    return lines


def main(argv: list | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        parser.print_help()
        return 2

    if args.command == "take":
        snap = take_snapshot(args.expressions)
        save_snapshot(snap, args.output)
        print(f"Snapshot saved to {args.output} ({len(snap.entries)} entries)")
        has_errors = any(e.error_count > 0 for e in snap.entries)
        return 1 if has_errors else 0

    if args.command == "diff":
        old = load_snapshot(args.old)
        new = load_snapshot(args.new)
        if old is None:
            print(f"Error: could not load snapshot from {args.old}", file=sys.stderr)
            return 2
        if new is None:
            print(f"Error: could not load snapshot from {args.new}", file=sys.stderr)
            return 2

        diff = diff_snapshots(old, new)
        if not diff.has_changes:
            print("No changes between snapshots.")
            return 0

        for expr in diff.added:
            print(f"+ {expr}")
        for expr in diff.removed:
            print(f"- {expr}")
        for expr in diff.changed:
            print(f"~ {expr}")
        return 1

    return 2


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
