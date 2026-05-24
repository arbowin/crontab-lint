"""Generate a 24x7 activity heatmap for crontab expressions."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .parser import parse, ParseError
from .schedule import _matches_field

DAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]


@dataclass
class HeatmapResult:
    expression: str
    is_valid: bool
    # grid[day_of_week][hour] = run count per hour (0-6, 0=Sun)
    grid: List[List[int]] = field(default_factory=lambda: [[0] * 24 for _ in range(7)])
    error: str = ""


def _is_valid(result: HeatmapResult) -> bool:
    return result.is_valid


def build_heatmap(expression: str) -> HeatmapResult:
    """Build a 7x24 heatmap grid for the given cron expression."""
    try:
        parsed = parse(expression)
    except ParseError as exc:
        return HeatmapResult(expression=expression, is_valid=False, error=str(exc))

    grid = [[0] * 24 for _ in range(7)]

    for dow in range(7):
        for hour in range(24):
            minute_hits = sum(
                1
                for minute in range(60)
                if _matches_field(parsed.minute.raw, minute, 0, 59)
            )
            if (
                _matches_field(parsed.hour.raw, hour, 0, 23)
                and _matches_field(parsed.day_of_week.raw, dow, 0, 6)
            ):
                grid[dow][hour] = minute_hits

    return HeatmapResult(expression=expression, is_valid=True, grid=grid)


def format_heatmap(result: HeatmapResult, use_color: bool = False) -> str:
    """Render the heatmap as a text table."""
    if not result.is_valid:
        return f"Invalid expression: {result.error}"

    hours_header = "     " + "".join(f"{h:3d}" for h in range(24))
    lines = [f"Heatmap for: {result.expression}", hours_header]

    for dow_idx, day in enumerate(DAYS):
        row = result.grid[dow_idx]
        cells = "".join(_cell(v, use_color) for v in row)
        lines.append(f"{day:4s} {cells}")

    return "\n".join(lines)


def _cell(value: int, use_color: bool) -> str:
    if value == 0:
        symbol = "  ."
    elif value < 10:
        symbol = f"  {value}"
    else:
        symbol = f" {value:2d}"
    if use_color and value > 0:
        return f"\033[92m{symbol}\033[0m"
    return symbol
