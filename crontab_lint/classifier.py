"""Classify crontab expressions into human-readable schedule categories."""

from dataclasses import dataclass, field
from typing import Optional

from .linter import lint
from .normalizer import normalize


@dataclass
class ClassifyResult:
    expression: str
    is_valid: bool
    category: Optional[str]
    subcategory: Optional[str]
    description: str
    confidence: str  # 'high', 'medium', 'low'


def _classify_normalized(expr: str) -> tuple[Optional[str], Optional[str], str, str]:
    """Return (category, subcategory, description, confidence) for a normalized expression."""
    parts = expr.split()
    if len(parts) != 6:
        return None, None, "Unknown schedule", "low"

    minute, hour, dom, month, dow, _cmd = parts

    # Every minute
    if minute == "*" and hour == "*" and dom == "*" and month == "*" and dow == "*":
        return "frequent", "every-minute", "Runs every minute", "high"

    # Every N minutes
    if minute.startswith("*/") and hour == "*" and dom == "*" and month == "*" and dow == "*":
        n = minute[2:]
        return "frequent", "interval", f"Runs every {n} minutes", "high"

    # Hourly
    if hour == "*" and dom == "*" and month == "*" and dow == "*" and not minute.startswith("*"):
        return "hourly", "every-hour", f"Runs once per hour at minute {minute}", "high"

    # Every N hours
    if hour.startswith("*/") and dom == "*" and month == "*" and dow == "*":
        n = hour[2:]
        return "hourly", "interval", f"Runs every {n} hours", "high"

    # Daily (specific time, any day)
    if dom == "*" and month == "*" and dow == "*" and not hour.startswith("*") and not minute.startswith("*"):
        return "daily", "every-day", f"Runs daily at {hour}:{minute.zfill(2)}", "high"

    # Weekly (specific day of week)
    if dom == "*" and month == "*" and dow != "*" and not hour.startswith("*"):
        days = {"0": "Sunday", "1": "Monday", "2": "Tuesday", "3": "Wednesday",
                "4": "Thursday", "5": "Friday", "6": "Saturday", "7": "Sunday"}
        day_label = days.get(dow, f"day {dow}")
        return "weekly", "specific-day", f"Runs weekly on {day_label} at {hour}:{minute.zfill(2)}", "high"

    # Monthly (specific day of month)
    if dom != "*" and month == "*" and dow == "*" and not hour.startswith("*"):
        return "monthly", "specific-dom", f"Runs monthly on day {dom} at {hour}:{minute.zfill(2)}", "high"

    # Yearly / annually
    if dom != "*" and month != "*" and dow == "*":
        return "yearly", "specific-date", f"Runs yearly in month {month} on day {dom}", "high"

    # Weekdays only
    if dow in ("1-5", "1,2,3,4,5") and dom == "*" and month == "*":
        return "weekly", "weekdays", f"Runs on weekdays at {hour}:{minute.zfill(2)}", "medium"

    return "custom", None, "Custom or complex schedule", "low"


def classify(expression: str) -> ClassifyResult:
    """Classify a crontab expression into a schedule category."""
    result = lint(expression)
    if not result.is_valid:
        return ClassifyResult(
            expression=expression,
            is_valid=False,
            category=None,
            subcategory=None,
            description="Invalid expression",
            confidence="high",
        )

    norm = normalize(expression)
    normalized_expr = norm.normalized if norm.normalized else expression
    category, subcategory, description, confidence = _classify_normalized(normalized_expr)

    return ClassifyResult(
        expression=expression,
        is_valid=True,
        category=category,
        subcategory=subcategory,
        description=description,
        confidence=confidence,
    )
