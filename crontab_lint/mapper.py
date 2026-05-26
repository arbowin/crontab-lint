"""Maps crontab expressions to their canonical time-of-day run slots."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import lint
from .schedule import _matches_field


@dataclass
class MapEntry:
    hour: int
    minute: int

    def to_dict(self) -> dict:
        return {"hour": self.hour, "minute": self.minute}

    def __str__(self) -> str:
        return f"{self.hour:02d}:{self.minute:02d}"


@dataclass
class MapResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    entries: List[MapEntry] = field(default_factory=list)

    def total(self) -> int:
        return len(self.entries)

    def hours_covered(self) -> List[int]:
        return sorted({e.hour for e in self.entries})

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "is_valid": self.is_valid,
            "error": self.error,
            "entries": [e.to_dict() for e in self.entries],
            "total": self.total(),
        }


def map_expression(expression: str) -> MapResult:
    """Return every (hour, minute) pair that matches the expression in a 24h day."""
    result = lint(expression)
    if not result.is_valid:
        msg = result.issues[0].message if result.issues else "Invalid expression"
        return MapResult(expression=expression, is_valid=False, error=msg)

    parsed = result.parsed
    entries: List[MapEntry] = []
    for hour in range(24):
        for minute in range(60):
            if _matches_field(parsed.minute.raw, minute, 0, 59) and \
               _matches_field(parsed.hour.raw, hour, 0, 23):
                entries.append(MapEntry(hour=hour, minute=minute))

    return MapResult(
        expression=expression,
        is_valid=True,
        error=None,
        entries=entries,
    )


def format_map_result(result: MapResult) -> str:
    lines = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    lines.append(f"Total runs : {result.total()} per day")
    lines.append(f"Hours      : {result.hours_covered()}")
    if result.entries:
        sample = result.entries[:8]
        times = ", ".join(str(e) for e in sample)
        if result.total() > 8:
            times += f" ... (+{result.total() - 8} more)"
        lines.append(f"Runs at    : {times}")
    return "\n".join(lines)
