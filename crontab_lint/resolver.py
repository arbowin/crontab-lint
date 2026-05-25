"""Resolve a crontab expression to the next N run times as human-readable strings."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from .linter import lint
from .schedule import next_runs


@dataclass
class ResolveResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    runs: List[str] = field(default_factory=list)

    def has_runs(self) -> bool:
        return len(self.runs) > 0


def resolve(
    expression: str,
    count: int = 5,
    after: Optional[datetime] = None,
    fmt: str = "%Y-%m-%d %H:%M",
) -> ResolveResult:
    """Return the next *count* scheduled run times for *expression*.

    Parameters
    ----------
    expression:
        A five-field crontab expression (or shorthand like ``@daily``).
    count:
        How many future run times to compute (1–50).
    after:
        Compute runs after this moment.  Defaults to ``datetime.now()``.
    fmt:
        ``strftime`` format used to render each run time.
    """
    count = max(1, min(count, 50))
    result = lint(expression)

    if not result.is_valid:
        first_error = result.issues[0].message if result.issues else "invalid expression"
        return ResolveResult(expression=expression, is_valid=False, error=first_error)

    start = after or datetime.now()
    datetimes = next_runs(expression, count=count, after=start)
    formatted = [dt.strftime(fmt) for dt in datetimes]
    return ResolveResult(expression=expression, is_valid=True, error=None, runs=formatted)


def format_resolve_result(result: ResolveResult) -> str:
    """Return a human-readable multi-line string for *result*."""
    lines: List[str] = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    lines.append(f"Next runs  ({len(result.runs)}):")
    for i, run in enumerate(result.runs, 1):
        lines.append(f"  {i:>2}. {run}")
    return "\n".join(lines)
