"""Stack multiple cron expressions and report overlapping run times."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict, Tuple

from .linter import lint
from .schedule import next_runs

import datetime


@dataclass
class OverlapEntry:
    timestamp: datetime.datetime
    expressions: List[str]

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp.isoformat(),
            "expressions": self.expressions,
        }


@dataclass
class StackResult:
    expressions: List[str]
    valid_expressions: List[str]
    invalid_expressions: List[str]
    overlaps: List[OverlapEntry]
    is_valid: bool
    error: str = ""

    def overlap_count(self) -> int:
        return len(self.overlaps)

    def has_overlaps(self) -> bool:
        return len(self.overlaps) > 0


def stack(
    expressions: List[str],
    hours: int = 24,
    start: datetime.datetime | None = None,
) -> StackResult:
    """Find overlapping run times across multiple cron expressions."""
    if start is None:
        start = datetime.datetime(2024, 1, 1, 0, 0)

    valid_exprs: List[str] = []
    invalid_exprs: List[str] = []

    for expr in expressions:
        result = lint(expr)
        if result.is_valid:
            valid_exprs.append(expr)
        else:
            invalid_exprs.append(expr)

    if not valid_exprs:
        return StackResult(
            expressions=expressions,
            valid_expressions=valid_exprs,
            invalid_expressions=invalid_exprs,
            overlaps=[],
            is_valid=False,
            error="No valid expressions to stack.",
        )

    end = start + datetime.timedelta(hours=hours)
    runs_by_expr: Dict[str, List[datetime.datetime]] = {}

    for expr in valid_exprs:
        runs = next_runs(expr, count=hours * 60, start=start)
        runs_by_expr[expr] = [r for r in runs if r < end]

    timestamp_map: Dict[datetime.datetime, List[str]] = {}
    for expr, runs in runs_by_expr.items():
        for run in runs:
            timestamp_map.setdefault(run, []).append(expr)

    overlaps = [
        OverlapEntry(timestamp=ts, expressions=exprs)
        for ts, exprs in sorted(timestamp_map.items())
        if len(exprs) > 1
    ]

    return StackResult(
        expressions=expressions,
        valid_expressions=valid_exprs,
        invalid_expressions=invalid_exprs,
        overlaps=overlaps,
        is_valid=True,
    )


def format_stack_result(result: StackResult) -> str:
    lines = []
    lines.append(f"Expressions stacked: {len(result.expressions)}")
    lines.append(f"Valid: {len(result.valid_expressions)}  Invalid: {len(result.invalid_expressions)}")
    if not result.is_valid:
        lines.append(f"Error: {result.error}")
        return "\n".join(lines)
    if result.has_overlaps():
        lines.append(f"Overlapping run times: {result.overlap_count()}")
        for entry in result.overlaps:
            exprs = ", ".join(entry.expressions)
            lines.append(f"  {entry.timestamp.strftime('%Y-%m-%d %H:%M')}  [{exprs}]")
    else:
        lines.append("No overlapping run times found.")
    return "\n".join(lines)
