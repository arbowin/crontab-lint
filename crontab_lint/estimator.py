"""Estimate the average interval between runs for a cron expression."""

from dataclasses import dataclass, field
from typing import Optional

from .linter import lint
from .schedule import next_runs


@dataclass
class EstimateResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    interval_seconds: Optional[int]
    interval_human: Optional[str]
    runs_per_day: Optional[int]


def _human_interval(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds} second(s)"
    minutes = seconds // 60
    if minutes < 60:
        return f"{minutes} minute(s)"
    hours = minutes // 60
    rem_min = minutes % 60
    if rem_min == 0:
        return f"{hours} hour(s)"
    return f"{hours} hour(s) {rem_min} minute(s)"


def estimate(expression: str) -> EstimateResult:
    """Estimate the average interval between runs."""
    result = lint(expression)
    if not result.valid:
        msg = result.issues[0].message if result.issues else "Invalid expression"
        return EstimateResult(
            expression=expression,
            is_valid=False,
            error=msg,
            interval_seconds=None,
            interval_human=None,
            runs_per_day=None,
        )

    from datetime import datetime
    anchor = datetime(2024, 1, 1, 0, 0, 0)
    runs = next_runs(expression, anchor, count=48)

    if len(runs) < 2:
        return EstimateResult(
            expression=expression,
            is_valid=True,
            error=None,
            interval_seconds=None,
            interval_human="Unable to estimate",
            runs_per_day=None,
        )

    deltas = [
        int((runs[i + 1] - runs[i]).total_seconds())
        for i in range(len(runs) - 1)
    ]
    avg_seconds = sum(deltas) // len(deltas)
    runs_per_day = 86400 // avg_seconds if avg_seconds > 0 else 0

    return EstimateResult(
        expression=expression,
        is_valid=True,
        error=None,
        interval_seconds=avg_seconds,
        interval_human=_human_interval(avg_seconds),
        runs_per_day=runs_per_day,
    )


def format_estimate_result(result: EstimateResult) -> str:
    lines = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    lines.append(f"Interval   : {result.interval_human}")
    lines.append(f"Runs/day   : {result.runs_per_day}")
    return "\n".join(lines)
