"""Balancer: detect uneven load distribution across hours/days for a set of cron expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict

from .linter import lint
from .schedule import _matches_field
from .parser import parse, ParseError


@dataclass
class BalanceResult:
    expressions: List[str]
    is_valid: bool
    error: str
    hourly_load: Dict[int, int]  # hour -> run count across all expressions
    peak_hour: int
    min_hour: int
    peak_load: int
    min_load: int
    imbalance_ratio: float  # peak / min, or 0.0 if min==0
    verdict: str


def _runs_in_hour(expr: str, hour: int) -> int:
    """Count how many minutes in a given hour a parsed expression fires."""
    try:
        parsed = parse(expr)
    except ParseError:
        return 0
    count = 0
    for minute in range(60):
        if _matches_field(parsed.minute.raw, minute, 0, 59) and \
           _matches_field(parsed.hour.raw, hour, 0, 23):
            count += 1
    return count


def balance(expressions: List[str]) -> BalanceResult:
    """Analyse load balance across 24 hours for a collection of cron expressions."""
    if not expressions:
        return BalanceResult(
            expressions=[],
            is_valid=False,
            error="No expressions provided.",
            hourly_load={},
            peak_hour=0,
            min_hour=0,
            peak_load=0,
            min_load=0,
            imbalance_ratio=0.0,
            verdict="no data",
        )

    invalid = []
    for expr in expressions:
        result = lint(expr)
        if result.has_errors:
            invalid.append(expr)

    if invalid:
        return BalanceResult(
            expressions=expressions,
            is_valid=False,
            error=f"Invalid expression(s): {', '.join(invalid)}",
            hourly_load={},
            peak_hour=0,
            min_hour=0,
            peak_load=0,
            min_load=0,
            imbalance_ratio=0.0,
            verdict="invalid",
        )

    hourly_load: Dict[int, int] = {h: 0 for h in range(24)}
    for expr in expressions:
        for hour in range(24):
            hourly_load[hour] += _runs_in_hour(expr, hour)

    peak_hour = max(hourly_load, key=lambda h: hourly_load[h])
    min_hour = min(hourly_load, key=lambda h: hourly_load[h])
    peak_load = hourly_load[peak_hour]
    min_load = hourly_load[min_hour]
    ratio = round(peak_load / min_load, 2) if min_load > 0 else 0.0

    if ratio == 0.0 or ratio <= 1.5:
        verdict = "balanced"
    elif ratio <= 4.0:
        verdict = "slightly unbalanced"
    else:
        verdict = "highly unbalanced"

    return BalanceResult(
        expressions=expressions,
        is_valid=True,
        error="",
        hourly_load=hourly_load,
        peak_hour=peak_hour,
        min_hour=min_hour,
        peak_load=peak_load,
        min_load=min_load,
        imbalance_ratio=ratio,
        verdict=verdict,
    )


def format_balance_result(result: BalanceResult) -> str:
    lines = []
    if not result.is_valid:
        lines.append(f"ERROR: {result.error}")
        return "\n".join(lines)
    lines.append(f"Expressions analysed : {len(result.expressions)}")
    lines.append(f"Peak hour            : {result.peak_hour:02d}:00 ({result.peak_load} runs)")
    lines.append(f"Quietest hour        : {result.min_hour:02d}:00 ({result.min_load} runs)")
    lines.append(f"Imbalance ratio      : {result.imbalance_ratio}")
    lines.append(f"Verdict              : {result.verdict}")
    return "\n".join(lines)
