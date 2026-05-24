"""Profiler module: analyze crontab expressions for frequency and load patterns."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import parse, ParseError


@dataclass
class ProfileResult:
    expression: str
    is_valid: bool
    runs_per_hour: float
    runs_per_day: float
    runs_per_week: float
    frequency_label: str
    warnings: List[str] = field(default_factory=list)


def _runs_per_hour(minute_spec: str) -> float:
    """Estimate how many times per hour the minute field fires."""
    if minute_spec == "*":
        return 60.0
    if "/" in minute_spec:
        try:
            step = int(minute_spec.split("/")[1])
            return 60.0 / step if step > 0 else 1.0
        except (ValueError, IndexError):
            return 1.0
    if "," in minute_spec:
        return float(len(minute_spec.split(",")))
    return 1.0


def _runs_per_day_from_hour(hour_spec: str) -> float:
    """Estimate how many distinct hours fire."""
    if hour_spec == "*":
        return 24.0
    if "/" in hour_spec:
        try:
            step = int(hour_spec.split("/")[1])
            return 24.0 / step if step > 0 else 1.0
        except (ValueError, IndexError):
            return 1.0
    if "," in hour_spec:
        return float(len(hour_spec.split(",")))
    return 1.0


def _frequency_label(runs_per_day: float) -> str:
    if runs_per_day >= 1440:
        return "every-minute"
    if runs_per_day >= 60:
        return "high-frequency"
    if runs_per_day >= 24:
        return "frequent"
    if runs_per_day >= 2:
        return "several-times-daily"
    if runs_per_day >= 1:
        return "daily"
    if runs_per_day >= 1 / 7:
        return "weekly"
    return "infrequent"


def profile(expression: str) -> ProfileResult:
    """Return a ProfileResult describing the run frequency of a cron expression."""
    warnings: List[str] = []
    try:
        parsed = parse(expression)
    except ParseError as exc:
        return ProfileResult(
            expression=expression,
            is_valid=False,
            runs_per_hour=0.0,
            runs_per_day=0.0,
            runs_per_week=0.0,
            frequency_label="invalid",
            warnings=[str(exc)],
        )

    rph = _runs_per_hour(parsed.fields[0].raw)
    hours_per_day = _runs_per_day_from_hour(parsed.fields[1].raw)
    rpd = rph * hours_per_day
    rpw = rpd * 7

    if rpd > 720:
        warnings.append("Expression fires very frequently (>720 times/day); verify intentional.")

    label = _frequency_label(rpd)
    return ProfileResult(
        expression=expression,
        is_valid=True,
        runs_per_hour=round(rph * hours_per_day / 24 * 24, 4),
        runs_per_day=round(rpd, 4),
        runs_per_week=round(rpw, 4),
        frequency_label=label,
        warnings=warnings,
    )
