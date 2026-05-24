"""Rank a list of crontab expressions by complexity or frequency."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .linter import lint
from .profiler import profile


@dataclass
class RankedEntry:
    expression: str
    rank: int
    runs_per_day: float
    score: float
    is_valid: bool

    def to_dict(self) -> dict:
        return {
            "rank": self.rank,
            "expression": self.expression,
            "runs_per_day": self.runs_per_day,
            "score": self.score,
            "is_valid": self.is_valid,
        }


@dataclass
class RankResult:
    entries: List[RankedEntry] = field(default_factory=list)

    def by_rank(self) -> List[RankedEntry]:
        return sorted(self.entries, key=lambda e: e.rank)


def _runs_per_day(expression: str) -> float:
    """Return estimated runs per day for ranking purposes."""
    try:
        p = profile(expression)
        return float(p.runs_per_day) if p.is_valid else 0.0
    except Exception:
        return 0.0


def _complexity_score(expression: str) -> float:
    """Lower score = simpler expression. Based on unique part count."""
    parts = expression.strip().split()
    if len(parts) < 5:
        return 0.0
    cron_parts = parts[:5]
    wildcards = sum(1 for p in cron_parts if p == "*")
    return float(5 - wildcards)


def rank(
    expressions: List[str],
    key: str = "frequency",
) -> RankResult:
    """Rank expressions by 'frequency' (runs/day desc) or 'complexity' (asc).

    Args:
        expressions: List of raw crontab expression strings.
        key: Ranking strategy — 'frequency' or 'complexity'.

    Returns:
        RankResult with entries sorted and assigned rank numbers.
    """
    if key not in ("frequency", "complexity"):
        raise ValueError(f"Unknown ranking key: {key!r}. Use 'frequency' or 'complexity'.")

    entries = []
    for expr in expressions:
        result = lint(expr)
        rpd = _runs_per_day(expr)
        score = _complexity_score(expr)
        entries.append(
            RankedEntry(
                expression=expr,
                rank=0,
                runs_per_day=rpd,
                score=score,
                is_valid=result.is_valid,
            )
        )

    if key == "frequency":
        entries.sort(key=lambda e: e.runs_per_day, reverse=True)
    else:
        entries.sort(key=lambda e: e.score)

    for i, entry in enumerate(entries, start=1):
        entry.rank = i

    return RankResult(entries=entries)


def format_rank_result(result: RankResult) -> str:
    """Return a human-readable table of ranked expressions."""
    if not result.entries:
        return "No expressions to rank."
    lines = [f"{'Rank':<6} {'Runs/Day':<12} {'Valid':<7} Expression"]
    lines.append("-" * 50)
    for e in result.by_rank():
        valid_str = "yes" if e.is_valid else "no"
        lines.append(f"{e.rank:<6} {e.runs_per_day:<12.1f} {valid_str:<7} {e.expression}")
    return "\n".join(lines)
