"""Streak analysis: find consecutive days/hours a cron expression is active."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .validator import validate
from .normalizer import normalize


@dataclass
class StreakResult:
    expression: str
    is_valid: bool
    error: str
    # Consecutive hours in a day the job fires (0-23 window)
    active_hours: List[int]
    max_hour_streak: int
    # Consecutive days of the week the job fires (0=Mon … 6=Sun)
    active_days: List[int]
    max_day_streak: int


def _max_consecutive(values: List[int], modulo: int) -> int:
    """Return the longest run of consecutive integers in *values* (wraps around modulo)."""
    if not values:
        return 0
    s = sorted(set(values))
    best = current = 1
    for i in range(1, len(s)):
        if s[i] == s[i - 1] + 1:
            current += 1
            best = max(best, current)
        else:
            current = 1
    # Check wrap-around (e.g. hours 22,23,0,1)
    wrap = 1
    lo, hi = 0, len(s) - 1
    while lo < hi and s[lo] + modulo - s[hi] == 1:
        # the two ends are adjacent mod modulo
        wrap += 1
        lo += 1
        hi -= 1
        if s[lo] != s[lo - 1] + 1 or s[hi] != s[hi + 1] - 1:
            break
    return max(best, wrap)


def _expand_field(raw: str, lo: int, hi: int) -> List[int]:
    """Expand a single normalised cron field to a sorted list of integers."""
    result: set[int] = set()
    for part in raw.split(","):
        if part == "*":
            result.update(range(lo, hi + 1))
        elif "/" in part:
            base, step = part.split("/", 1)
            start = lo if base == "*" else int(base.split("-")[0])
            result.update(range(start, hi + 1, int(step)))
        elif "-" in part:
            a, b = part.split("-", 1)
            result.update(range(int(a), int(b) + 1))
        else:
            result.add(int(part))
    return sorted(result)


def streak(expression: str) -> StreakResult:
    """Analyse the active-hour and active-day streaks for *expression*."""
    result = validate(expression)
    if not result.is_valid:
        msg = result.issues[0].message if result.issues else "invalid expression"
        return StreakResult(
            expression=expression,
            is_valid=False,
            error=msg,
            active_hours=[],
            max_hour_streak=0,
            active_days=[],
            max_day_streak=0,
        )

    norm = normalize(expression)
    parts = norm.normalized.split()
    # parts: minute hour dom month dow [command...]
    hour_raw = parts[1]
    dow_raw = parts[4]

    active_hours = _expand_field(hour_raw, 0, 23)
    active_days = _expand_field(dow_raw, 0, 6)

    return StreakResult(
        expression=expression,
        is_valid=True,
        error="",
        active_hours=active_hours,
        max_hour_streak=_max_consecutive(active_hours, 24),
        active_days=active_days,
        max_day_streak=_max_consecutive(active_days, 7),
    )


def format_streak_result(r: StreakResult) -> str:
    if not r.is_valid:
        return f"[ERROR] {r.expression}: {r.error}"
    lines = [
        f"Expression : {r.expression}",
        f"Active hours ({len(r.active_hours)}): {r.active_hours}  →  max streak {r.max_hour_streak}h",
        f"Active days  ({len(r.active_days)}): {r.active_days}  →  max streak {r.max_day_streak}d",
    ]
    return "\n".join(lines)
