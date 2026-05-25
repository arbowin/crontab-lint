"""Cap (limit) cron expressions to a maximum run frequency per day."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import lint
from .profiler import profile


@dataclass
class CapResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    runs_per_day: int
    cap: int
    exceeds_cap: bool
    suggested: Optional[str]

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "is_valid": self.is_valid,
            "error": self.error,
            "runs_per_day": self.runs_per_day,
            "cap": self.cap,
            "exceeds_cap": self.exceeds_cap,
            "suggested": self.suggested,
        }


def _suggest_for_cap(runs_per_day: int, cap: int) -> Optional[str]:
    """Return a simple suggested expression that stays within the cap."""
    if cap <= 0:
        return None
    # Target: evenly distribute runs within a day
    # runs_per_day = 60 * 24 / step_minutes  =>  step_minutes = 1440 / cap
    step = max(1, 1440 // cap)
    if step == 1:
        return "* * * * *"
    if step < 60:
        return f"*/{step} * * * *"
    step_hours = step // 60
    if step_hours == 1:
        return "0 * * * *"
    if step_hours < 24:
        return f"0 */{step_hours} * * *"
    return "0 0 * * *"


def cap(expression: str, max_runs_per_day: int = 96) -> CapResult:
    """Analyse *expression* and flag it if it exceeds *max_runs_per_day*."""
    lint_result = lint(expression)
    if not lint_result.valid:
        first_error = (
            lint_result.issues[0].message if lint_result.issues else "invalid expression"
        )
        return CapResult(
            expression=expression,
            is_valid=False,
            error=first_error,
            runs_per_day=0,
            cap=max_runs_per_day,
            exceeds_cap=False,
            suggested=None,
        )

    p = profile(expression)
    runs = p.runs_per_day
    exceeds = runs > max_runs_per_day
    suggested = _suggest_for_cap(runs, max_runs_per_day) if exceeds else None

    return CapResult(
        expression=expression,
        is_valid=True,
        error=None,
        runs_per_day=runs,
        cap=max_runs_per_day,
        exceeds_cap=exceeds,
        suggested=suggested,
    )


def format_cap_result(result: CapResult) -> str:
    lines: List[str] = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    lines.append(f"Runs/day   : {result.runs_per_day}")
    lines.append(f"Cap        : {result.cap}")
    status = "EXCEEDS CAP" if result.exceeds_cap else "within cap"
    lines.append(f"Status     : {status}")
    if result.suggested:
        lines.append(f"Suggested  : {result.suggested}")
    return "\n".join(lines)
