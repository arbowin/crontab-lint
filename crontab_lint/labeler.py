"""Assign human-readable labels to crontab expressions based on their schedule pattern."""

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import lint
from .normalizer import normalize


@dataclass
class LabelResult:
    expression: str
    is_valid: bool
    label: str
    sublabel: Optional[str]
    error: Optional[str]


def _label_for(normalized: str) -> tuple:
    """Return (label, sublabel) for a normalized cron expression."""
    parts = normalized.split()
    if len(parts) != 5:
        return ("unknown", None)

    minute, hour, dom, month, dow = parts

    if all(p == "*" for p in parts):
        return ("every-minute", "runs every minute of every day")

    if minute == "*" and hour == "*" and dom == "*" and month == "*" and dow == "*":
        return ("every-minute", "runs every minute of every day")

    if dom == "*" and month == "*" and dow == "*":
        if hour == "*" and minute.startswith("*/"):
            step = minute[2:]
            return ("frequent", f"every {step} minutes")
        if hour == "*" and minute == "0":
            return ("hourly", "once per hour at the top of the hour")
        if hour == "*":
            return ("sub-hourly", f"at minute {minute} of every hour")
        if minute == "0" and hour == "0":
            return ("daily", "once per day at midnight")
        if minute == "0":
            return ("daily", f"once per day at {hour}:00")
        return ("daily", f"once per day at {hour}:{minute.zfill(2)}")

    if dom == "*" and month == "*" and dow != "*":
        day_map = {"0": "Sunday", "1": "Monday", "2": "Tuesday",
                   "3": "Wednesday", "4": "Thursday", "5": "Friday", "6": "Saturday"}
        day_name = day_map.get(dow, f"weekday {dow}")
        return ("weekly", f"every {day_name}")

    if dom != "*" and month == "*" and dow == "*":
        return ("monthly", f"on day {dom} of each month")

    if dom != "*" and month != "*" and dow == "*":
        return ("yearly", f"on {month}/{dom} each year")

    return ("custom", None)


def label(expression: str) -> LabelResult:
    """Assign a label to a single crontab expression."""
    result = lint(expression)
    if not result.valid:
        error_msg = result.issues[0].message if result.issues else "invalid expression"
        return LabelResult(
            expression=expression,
            is_valid=False,
            label="invalid",
            sublabel=None,
            error=error_msg,
        )

    norm = normalize(expression)
    normalized_expr = norm.normalized if norm.normalized else expression
    lbl, sublbl = _label_for(" ".join(normalized_expr.split()[:5]))

    return LabelResult(
        expression=expression,
        is_valid=True,
        label=lbl,
        sublabel=sublbl,
        error=None,
    )


def format_label_result(result: LabelResult) -> str:
    """Format a LabelResult for display."""
    if not result.is_valid:
        return f"{result.expression}  [invalid: {result.error}]"
    parts = [f"{result.expression}  [{result.label}]",]
    if result.sublabel:
        parts.append(f"  # {result.sublabel}")
    return "".join(parts)
