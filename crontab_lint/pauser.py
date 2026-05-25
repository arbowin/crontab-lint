"""Pauser: determine quiet windows where a cron expression does NOT run."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .validator import validate
from .schedule import _matches_field
from .parser import parse, ParseError


@dataclass
class QuietWindow:
    start_hour: int
    end_hour: int  # exclusive
    duration_hours: int

    def to_dict(self) -> dict:
        return {
            "start_hour": self.start_hour,
            "end_hour": self.end_hour,
            "duration_hours": self.duration_hours,
        }


@dataclass
class PauseResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    quiet_windows: List[QuietWindow] = field(default_factory=list)
    longest_pause_hours: int = 0

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "is_valid": self.is_valid,
            "error": self.error,
            "quiet_windows": [w.to_dict() for w in self.quiet_windows],
            "longest_pause_hours": self.longest_pause_hours,
        }


def _hours_active(expression: str) -> List[bool]:
    """Return a 24-element list indicating whether the expression fires in each hour."""
    try:
        parsed = parse(expression)
    except ParseError:
        return [False] * 24

    active = []
    for hour in range(24):
        fires = _matches_field(parsed.fields[1].raw, hour, 0, 23)
        active.append(fires)
    return active


def pause(expression: str) -> PauseResult:
    """Identify contiguous quiet windows (hours with no scheduled runs)."""
    result = validate(expression)
    if not result.valid:
        msg = result.issues[0].message if result.issues else "Invalid expression"
        return PauseResult(
            expression=expression,
            is_valid=False,
            error=msg,
            quiet_windows=[],
            longest_pause_hours=0,
        )

    active = _hours_active(expression)

    windows: List[QuietWindow] = []
    i = 0
    while i < 24:
        if not active[i]:
            start = i
            while i < 24 and not active[i]:
                i += 1
            duration = i - start
            windows.append(QuietWindow(start_hour=start, end_hour=i, duration_hours=duration))
        else:
            i += 1

    longest = max((w.duration_hours for w in windows), default=0)
    return PauseResult(
        expression=expression,
        is_valid=True,
        error=None,
        quiet_windows=windows,
        longest_pause_hours=longest,
    )


def format_pause_result(result: PauseResult) -> str:
    lines = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    if not result.quiet_windows:
        lines.append("Quiet windows: none (runs every hour)")
    else:
        lines.append(f"Longest pause: {result.longest_pause_hours}h")
        for w in result.quiet_windows:
            lines.append(f"  {w.start_hour:02d}:00 – {w.end_hour:02d}:00  ({w.duration_hours}h)")
    return "\n".join(lines)
