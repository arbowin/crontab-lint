"""Expand a cron expression into all explicit (minute, hour) pairs it covers."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .validator import validate
from .normalizer import normalize


@dataclass
class ExpandResult:
    expression: str
    is_valid: bool
    error: str | None
    pairs: List[Tuple[int, int]]  # (minute, hour)


def _expand_single(raw: str, max_val: int) -> List[int]:
    """Expand a single normalized field token into a sorted list of integers."""
    values: List[int] = []
    for part in raw.split(","):
        if part == "*":
            values.extend(range(0, max_val + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            start = 0 if base == "*" else int(base)
            values.extend(range(start, max_val + 1, int(step)))
        elif "-" in part:
            lo, hi = part.split("-", 1)
            values.extend(range(int(lo), int(hi) + 1))
        else:
            values.append(int(part))
    return sorted(set(values))


def expand(expression: str) -> ExpandResult:
    """Return every (minute, hour) pair the expression fires on within one day."""
    result = validate(expression)
    if not result.is_valid:
        msg = result.issues[0].message if result.issues else "Invalid expression"
        return ExpandResult(expression=expression, is_valid=False, error=msg, pairs=[])

    norm = normalize(expression)
    if not norm.is_valid or norm.normalized is None:
        return ExpandResult(
            expression=expression,
            is_valid=False,
            error="Normalization failed",
            pairs=[],
        )

    parts = norm.normalized.split()
    minute_field = parts[0]
    hour_field = parts[1]

    minutes = _expand_single(minute_field, 59)
    hours = _expand_single(hour_field, 23)

    pairs = [(m, h) for h in hours for m in minutes]
    return ExpandResult(expression=expression, is_valid=True, error=None, pairs=pairs)


def format_expand_result(result: ExpandResult, limit: int = 10) -> str:
    """Return a human-readable summary of the expansion."""
    if not result.is_valid:
        return f"ERROR: {result.error}"
    total = len(result.pairs)
    lines = [f"Expression: {result.expression}", f"Total (minute, hour) pairs: {total}"]
    shown = result.pairs[:limit]
    for m, h in shown:
        lines.append(f"  {h:02d}:{m:02d}")
    if total > limit:
        lines.append(f"  ... and {total - limit} more")
    return "\n".join(lines)
