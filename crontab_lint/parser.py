"""Crontab expression parser module.

Parses a crontab expression string into its individual fields
and validates the basic structure.
"""

from dataclasses import dataclass
from typing import Optional


CRONTAB_FIELDS = ["minute", "hour", "day_of_month", "month", "day_of_week"]

FIELD_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 7),
}

MONTH_ALIASES = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4,
    "may": 5, "jun": 6, "jul": 7, "aug": 8,
    "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

WEEKDAY_ALIASES = {
    "sun": 0, "mon": 1, "tue": 2, "wed": 3,
    "thu": 4, "fri": 5, "sat": 6,
}


@dataclass
class CronField:
    name: str
    raw: str
    min_val: int
    max_val: int


@dataclass
class ParsedCron:
    raw: str
    fields: list[CronField]
    command: Optional[str] = None


class ParseError(ValueError):
    """Raised when a crontab expression cannot be parsed."""


def parse(expression: str) -> ParsedCron:
    """Parse a crontab expression into a ParsedCron object.

    Args:
        expression: A crontab expression string (5 or 6 tokens).

    Returns:
        A ParsedCron instance with individual field data.

    Raises:
        ParseError: If the expression does not have the expected structure.
    """
    expression = expression.strip()
    if not expression:
        raise ParseError("Expression must not be empty.")

    tokens = expression.split()
    if len(tokens) < 5:
        raise ParseError(
            f"Expected at least 5 fields, got {len(tokens)}: '{expression}'"
        )

    field_tokens = tokens[:5]
    command = " ".join(tokens[5:]) if len(tokens) > 5 else None

    fields = [
        CronField(
            name=CRONTAB_FIELDS[i],
            raw=_normalize_aliases(field_tokens[i], CRONTAB_FIELDS[i]),
            min_val=FIELD_RANGES[CRONTAB_FIELDS[i]][0],
            max_val=FIELD_RANGES[CRONTAB_FIELDS[i]][1],
        )
        for i in range(5)
    ]

    return ParsedCron(raw=expression, fields=fields, command=command)


def _normalize_aliases(value: str, field_name: str) -> str:
    """Replace textual aliases with their numeric equivalents."""
    aliases = MONTH_ALIASES if field_name == "month" else WEEKDAY_ALIASES
    lower = value.lower()
    for alias, num in aliases.items():
        lower = lower.replace(alias, str(num))
    return lower
