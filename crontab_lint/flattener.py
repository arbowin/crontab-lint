"""Flattener: expand a cron expression into a flat list of (minute, hour) run-time pairs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Tuple

from .validator import validate
from .normalizer import normalize


@dataclass
class FlattenResult:
    expression: str
    is_valid: bool
    error: str
    pairs: List[Tuple[int, int]] = field(default_factory=list)


def _expand_field(raw: str, lo: int, hi: int) -> List[int]:
    """Return sorted list of integers matched by a single cron field token."""
    values: set[int] = set()
    for part in raw.split(","):
        if part == "*":
            values.update(range(lo, hi + 1))
        elif "/" in part:
            base, step_str = part.split("/", 1)
            step = int(step_str)
            start = lo if base == "*" else int(base.split("-")[0])
            end = hi if base == "*" else (int(base.split("-")[1]) if "-" in base else hi)
            values.update(range(start, end + 1, step))
        elif "-" in part:
            a, b = part.split("-", 1)
            values.update(range(int(a), int(b) + 1))
        else:
            values.add(int(part))
    return sorted(values)


def flatten(expression: str) -> FlattenResult:
    """Expand *expression* into every (minute, hour) pair it fires within a day."""
    result = validate(expression)
    if not result.is_valid:
        msg = result.issues[0].message if result.issues else "invalid expression"
        return FlattenResult(expression=expression, is_valid=False, error=msg)

    norm = normalize(expression)
    canonical = norm.normalized if norm.normalized else expression
    parts = canonical.split()
    if len(parts) < 5:
        return FlattenResult(expression=expression, is_valid=False, error="too few fields")

    minutes = _expand_field(parts[0], 0, 59)
    hours = _expand_field(parts[1], 0, 23)

    pairs = [(m, h) for h in hours for m in minutes]
    return FlattenResult(expression=expression, is_valid=True, error="", pairs=pairs)


def format_flatten_result(result: FlattenResult, limit: int = 20) -> str:
    """Return a human-readable string describing the flatten result."""
    lines: List[str] = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    shown = result.pairs[:limit]
    lines.append(f"Total pairs: {len(result.pairs)}")
    for m, h in shown:
        lines.append(f"  {h:02d}:{m:02d}")
    if len(result.pairs) > limit:
        lines.append(f"  ... and {len(result.pairs) - limit} more")
    return "\n".join(lines)
