"""Sample random valid cron expressions with optional filtering by tag or frequency."""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import List, Optional

from .linter import lint
from .tagger import tag


_POOL: List[str] = [
    "* * * * *",
    "0 * * * *",
    "0 0 * * *",
    "0 0 * * 0",
    "0 0 1 * *",
    "0 0 1 1 *",
    "*/5 * * * *",
    "*/10 * * * *",
    "*/15 * * * *",
    "*/30 * * * *",
    "0 9 * * 1-5",
    "0 6,12,18 * * *",
    "30 8 * * 1",
    "0 0 15 * *",
    "0 2 * * 0",
    "15 4 1 * *",
    "0 12 * * 1-5",
    "45 23 * * *",
    "0 8-17 * * 1-5",
    "0 0 * 1 *",
]


@dataclass
class SampleResult:
    expressions: List[str]
    requested: int
    tag_filter: Optional[str]

    def __len__(self) -> int:
        return len(self.expressions)


def sample(
    count: int = 5,
    tag_filter: Optional[str] = None,
    seed: Optional[int] = None,
) -> SampleResult:
    """Return a random sample of valid cron expressions.

    Args:
        count: Number of expressions to return.
        tag_filter: If given, only return expressions matching this tag.
        seed: Optional random seed for reproducibility.
    """
    rng = random.Random(seed)

    pool = list(_POOL)
    if tag_filter:
        pool = [
            expr for expr in pool
            if tag_filter in tag(expr).tags
        ]

    if not pool:
        return SampleResult(expressions=[], requested=count, tag_filter=tag_filter)

    chosen: List[str] = []
    attempts = 0
    while len(chosen) < count and attempts < count * 10:
        expr = rng.choice(pool)
        result = lint(expr)
        if result.is_valid and expr not in chosen:
            chosen.append(expr)
        attempts += 1

    return SampleResult(expressions=chosen, requested=count, tag_filter=tag_filter)


def format_sample_result(result: SampleResult) -> str:
    """Format a SampleResult as a human-readable string."""
    lines = []
    if result.tag_filter:
        lines.append(f"Sampled expressions (tag={result.tag_filter!r}):")
    else:
        lines.append("Sampled expressions:")
    if not result.expressions:
        lines.append("  (none found)")
    else:
        for expr in result.expressions:
            lines.append(f"  {expr}")
    return "\n".join(lines)
