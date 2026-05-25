"""Segment a crontab expression into labeled time windows (hour bands)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import lint
from .schedule import _matches_field


@dataclass
class Segment:
    label: str        # e.g. "night", "morning", "afternoon", "evening"
    hour_start: int   # inclusive
    hour_end: int     # exclusive
    run_count: int    # number of runs in this window per day

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "hour_start": self.hour_start,
            "hour_end": self.hour_end,
            "run_count": self.run_count,
        }


@dataclass
class SegmentResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    segments: List[Segment] = field(default_factory=list)

    def total_runs(self) -> int:
        return sum(s.run_count for s in self.segments)

    def busiest_segment(self) -> Optional[Segment]:
        if not self.segments:
            return None
        return max(self.segments, key=lambda s: s.run_count)


_BANDS = [
    ("night",     0,  6),
    ("morning",   6, 12),
    ("afternoon", 12, 18),
    ("evening",   18, 24),
]


def segment(expression: str) -> SegmentResult:
    result = lint(expression)
    if not result.is_valid:
        first_error = result.issues[0].message if result.issues else "invalid expression"
        return SegmentResult(expression=expression, is_valid=False, error=first_error)

    parsed = result.parsed
    minute_field = parsed.fields[0].raw
    hour_field   = parsed.fields[1].raw

    minutes = [m for m in range(60) if _matches_field(minute_field, m, 0, 59)]

    segments: List[Segment] = []
    for label, h_start, h_end in _BANDS:
        count = 0
        for h in range(h_start, h_end):
            if _matches_field(hour_field, h, 0, 23):
                count += len(minutes)
        segments.append(Segment(label=label, hour_start=h_start, hour_end=h_end, run_count=count))

    return SegmentResult(expression=expression, is_valid=True, error=None, segments=segments)


def format_segment_result(result: SegmentResult) -> str:
    lines = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    for seg in result.segments:
        bar = "#" * min(seg.run_count, 40)
        lines.append(f"  {seg.label:<12} ({seg.hour_start:02d}:00-{seg.hour_end:02d}:00)  {seg.run_count:>5} runs  {bar}")
    lines.append(f"  {'TOTAL':<12}                  {result.total_runs():>5} runs")
    busiest = result.busiest_segment()
    if busiest and busiest.run_count > 0:
        lines.append(f"  Busiest: {busiest.label}")
    return "\n".join(lines)
