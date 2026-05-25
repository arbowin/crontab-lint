"""CLI entry point for the cron expression sampler."""

from __future__ import annotations

import argparse
import sys

from .sampler import sample, format_sample_result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="crontab-sample",
        description="Sample random valid cron expressions.",
    )
    parser.add_argument(
        "-n", "--count",
        type=int,
        default=5,
        metavar="N",
        help="Number of expressions to sample (default: 5).",
    )
    parser.add_argument(
        "-t", "--tag",
        default=None,
        metavar="TAG",
        help="Only sample expressions matching this tag.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        metavar="SEED",
        help="Random seed for reproducible output.",
    )
    parser.add_argument(
        "--plain",
        action="store_true",
        help="Print one expression per line without header.",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.count < 1:
        print("error: count must be at least 1", file=sys.stderr)
        return 2

    result = sample(count=args.count, tag_filter=args.tag, seed=args.seed)

    if args.plain:
        for expr in result.expressions:
            print(expr)
    else:
        print(format_sample_result(result))

    if not result.expressions:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
