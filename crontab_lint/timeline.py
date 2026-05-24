"""Timeline module: generate a chronological view of when multiple cron expressions fire."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Tuple

from .linter import lint
from .schedule import next_runs


@dataclass
class TimelineEntry:
    expression: str
    fires_at: datetime
    is_valid: bool

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "fires_at": self.fires_at.isoformat(),
            "is_valid": self.is_valid,
        }


@dataclass
class TimelineResult:
    entries: List[TimelineEntry] = field(default_factory=list)
    invalid_expressions: List[str] = field(default_factory=list)

    @property
    def has_invalid(self) -> bool:
        return len(self.invalid_expressions) > 0


def build_timeline(
    expressions: List[str],
    start: datetime,
    count: int = 5,
) -> TimelineResult:
    """Return a merged, sorted timeline of the next *count* fires for each expression."""
    entries: List[TimelineEntry] = []
    invalid: List[str] = []

    for expr in expressions:
        result = lint(expr)
        if not result.is_valid:
            invalid.append(expr)
            continue
        runs = next_runs(result.parsed, start=start, n=count)
        for dt in runs:
            entries.append(TimelineEntry(expression=expr, fires_at=dt, is_valid=True))

    entries.sort(key=lambda e: e.fires_at)
    return TimelineResult(entries=entries, invalid_expressions=invalid)


def format_timeline(result: TimelineResult) -> str:
    """Render a TimelineResult as a human-readable string."""
    lines: List[str] = []

    if result.has_invalid:
        for expr in result.invalid_expressions:
            lines.append(f"  [invalid] {expr}")

    if not result.entries:
        lines.append("No scheduled runs found.")
        return "\n".join(lines)

    for entry in result.entries:
        ts = entry.fires_at.strftime("%Y-%m-%d %H:%M")
        lines.append(f"  {ts}  {entry.expression}")

    return "\n".join(lines)
