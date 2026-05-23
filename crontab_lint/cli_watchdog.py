"""CLI entry-point for the crontab watchdog."""

from __future__ import annotations

import argparse
import sys
from typing import List

from crontab_lint.watchdog import WatchEvent, watch
from crontab_lint.formatter import format_many


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-watch",
        description="Watch a crontab file and re-lint it whenever it changes.",
    )
    parser.add_argument("file", help="Path to the crontab file to watch.")
    parser.add_argument(
        "--interval",
        type=float,
        default=2.0,
        metavar="SECONDS",
        help="Polling interval in seconds (default: 2.0).",
    )
    parser.add_argument(
        "--max-cycles",
        type=int,
        default=None,
        metavar="N",
        help="Stop after N polling cycles (useful for testing).",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show output even when there are no issues.",
    )
    return parser


def _make_handler(verbose: bool):
    """Return an on_event callback that prints lint results to stdout."""

    def handler(event: WatchEvent) -> None:
        if event.error:
            print(f"[watchdog] ERROR: {event.error}", file=sys.stderr)
            return

        print(f"[watchdog] Change detected in {event.path}")
        output = format_many(event.results, verbose=verbose)
        if output.strip():
            print(output)
        else:
            print("  All expressions are valid.")

    return handler


def main(argv: list | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.file:
        parser.print_help()
        return 2

    print(f"[watchdog] Watching {args.file} (interval={args.interval}s) — press Ctrl+C to stop.")
    try:
        watch(
            filepath=args.file,
            interval=args.interval,
            max_cycles=args.max_cycles,
            on_event=_make_handler(args.verbose),
        )
    except KeyboardInterrupt:
        print("\n[watchdog] Stopped.")

    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
