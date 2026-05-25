"""Syntax highlighter for crontab expressions using ANSI color codes."""
from __future__ import annotations
from dataclasses import dataclass
from typing import List

from .parser import parse, ParseError
from .validator import validate

_COLORS = [
    "\033[36m",  # cyan   - minute
    "\033[33m",  # yellow - hour
    "\033[32m",  # green  - day of month
    "\033[35m",  # magenta - month
    "\033[34m",  # blue   - day of week
]
_RESET = "\033[0m"
_RED = "\033[31m"
_BOLD = "\033[1m"

FIELD_LABELS = ["minute", "hour", "dom", "month", "dow"]


@dataclass
class HighlightResult:
    expression: str
    highlighted: str
    is_valid: bool
    legend: List[str]


def has_errors(result: HighlightResult) -> bool:
    return not result.is_valid


def highlight(expression: str) -> HighlightResult:
    """Return an ANSI-colored version of the crontab expression."""
    try:
        parsed = parse(expression)
    except ParseError:
        return HighlightResult(
            expression=expression,
            highlighted=f"{_RED}{expression}{_RESET}",
            is_valid=False,
            legend=[],
        )

    result = validate(expression)
    is_valid = not any(i.severity == "error" for i in result.issues)

    raw_fields = expression.split()
    cron_fields = raw_fields[:5]
    command_parts = raw_fields[5:]

    colored_fields = [
        f"{_COLORS[i]}{field}{_RESET}"
        for i, field in enumerate(cron_fields)
    ]
    command_str = " ".join(command_parts)
    parts = colored_fields + ([command_str] if command_str else [])
    highlighted = " ".join(parts)

    legend = [
        f"{_COLORS[i]}{_BOLD}{FIELD_LABELS[i]}{_RESET}"
        for i in range(len(cron_fields))
    ]

    return HighlightResult(
        expression=expression,
        highlighted=highlighted,
        is_valid=is_valid,
        legend=legend,
    )


def format_highlight_result(result: HighlightResult) -> str:
    """Return a human-readable highlighted output with legend."""
    lines = [result.highlighted]
    if result.legend:
        lines.append("  Legend: " + "  ".join(result.legend))
    if not result.is_valid:
        lines.append(f"{_RED}  (expression has errors){_RESET}")
    return "\n".join(lines)
