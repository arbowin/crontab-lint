"""Predict whether a cron expression will run within a given time window."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import List, Optional

from .linter import lint
from .schedule import next_runs


@dataclass
class PredictResult:
    expression: str
    is_valid: bool
    window_start: datetime
    window_end: datetime
    runs_in_window: List[datetime] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def will_run(self) -> bool:
        return len(self.runs_in_window) > 0

    @property
    def run_count(self) -> int:
        return len(self.runs_in_window)


def predict(
    expression: str,
    window_start: Optional[datetime] = None,
    window_hours: int = 24,
) -> PredictResult:
    """Predict runs for *expression* within a time window.

    Args:
        expression: A cron expression string.
        window_start: Start of the prediction window (defaults to now).
        window_hours: Length of the window in hours (default 24).

    Returns:
        A PredictResult with all scheduled runs inside the window.
    """
    if window_start is None:
        window_start = datetime.now().replace(second=0, microsecond=0)

    window_end = window_start + timedelta(hours=window_hours)

    result = lint(expression)
    if not result.valid:
        msg = result.issues[0].message if result.issues else "Invalid expression"
        return PredictResult(
            expression=expression,
            is_valid=False,
            window_start=window_start,
            window_end=window_end,
            error=msg,
        )

    # Request enough runs to cover the window; cap at a safe limit.
    max_runs = window_hours * 60
    candidates = next_runs(expression, count=max_runs, start=window_start)
    in_window = [dt for dt in candidates if window_start <= dt < window_end]

    return PredictResult(
        expression=expression,
        is_valid=True,
        window_start=window_start,
        window_end=window_end,
        runs_in_window=in_window,
    )


def format_predict_result(result: PredictResult) -> str:
    """Return a human-readable summary of a PredictResult."""
    lines: List[str] = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    window_fmt = "%Y-%m-%d %H:%M"
    lines.append(f"Window     : {result.window_start.strftime(window_fmt)} – {result.window_end.strftime(window_fmt)}")
    lines.append(f"Will run   : {'yes' if result.will_run else 'no'}")
    lines.append(f"Run count  : {result.run_count}")
    if result.runs_in_window:
        lines.append("Next runs  :")
        for dt in result.runs_in_window[:5]:
            lines.append(f"  {dt.strftime(window_fmt)}")
        if result.run_count > 5:
            lines.append(f"  … and {result.run_count - 5} more")
    return "\n".join(lines)
