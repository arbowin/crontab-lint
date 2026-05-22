"""Compute next scheduled run times for a cron expression."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Iterator, List

from .parser import ParsedCron, parse, ParseError


def _matches_field(value: int, field_str: str, min_val: int, max_val: int) -> bool:
    """Return True if *value* is matched by a single cron field string."""
    if field_str == "*":
        return True

    for part in field_str.split(","):
        # Step syntax: */n or start-end/n
        if "/" in part:
            range_part, step_str = part.split("/", 1)
            step = int(step_str)
            if range_part == "*":
                start, end = min_val, max_val
            elif "-" in range_part:
                s, e = range_part.split("-", 1)
                start, end = int(s), int(e)
            else:
                start, end = int(range_part), max_val
            if start <= value <= end and (value - start) % step == 0:
                return True
        elif "-" in part:
            start, end = part.split("-", 1)
            if int(start) <= value <= int(end):
                return True
        else:
            if value == int(part):
                return True

    return False


def next_runs(expression: str, after: datetime | None = None, count: int = 5) -> List[datetime]:
    """Return the next *count* datetimes matching *expression* after *after*.

    Parameters
    ----------
    expression:
        A five-field cron expression (without command).
    after:
        Start searching after this datetime.  Defaults to ``datetime.now()``.
    count:
        How many upcoming run times to return.
    """
    if after is None:
        after = datetime.now()

    # Ensure we start at the next whole minute.
    start = after.replace(second=0, microsecond=0) + timedelta(minutes=1)

    parsed: ParsedCron = parse(expression + " _placeholder_command")

    minute_str = parsed.minute.raw
    hour_str = parsed.hour.raw
    dom_str = parsed.day_of_month.raw
    month_str = parsed.month.raw
    dow_str = parsed.day_of_week.raw

    results: List[datetime] = []
    candidate = start

    # Guard against infinite loops — search at most ~4 years ahead.
    limit = start + timedelta(days=1500)

    while len(results) < count and candidate < limit:
        if (
            _matches_field(candidate.month, month_str, 1, 12)
            and _matches_field(candidate.day, dom_str, 1, 31)
            and _matches_field(candidate.weekday(), dow_str, 0, 6)
            and _matches_field(candidate.hour, hour_str, 0, 23)
            and _matches_field(candidate.minute, minute_str, 0, 59)
        ):
            results.append(candidate)

        candidate += timedelta(minutes=1)

    return results
