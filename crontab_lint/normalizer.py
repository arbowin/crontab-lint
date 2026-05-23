"""Normalize crontab expressions to a canonical form."""

from dataclasses import dataclass
from typing import Optional

from crontab_lint.parser import ParsedCron, parse, ParseError

# Map common shorthand expressions to their canonical equivalents
_SHORTHANDS: dict[str, str] = {
    "@yearly": "0 0 1 1 *",
    "@annually": "0 0 1 1 *",
    "@monthly": "0 0 1 * *",
    "@weekly": "0 0 * * 0",
    "@daily": "0 0 * * *",
    "@midnight": "0 0 * * *",
    "@hourly": "0 * * * *",
}


@dataclass
class NormalizeResult:
    original: str
    normalized: Optional[str]
    was_shorthand: bool
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None


def _expand_shorthand(expression: str) -> tuple[str, bool]:
    """Expand a shorthand expression if recognized, return (expr, was_shorthand)."""
    parts = expression.strip().split()
    if len(parts) >= 1 and parts[0].lower() in _SHORTHANDS:
        expanded = _SHORTHANDS[parts[0].lower()]
        # Preserve command if present
        if len(parts) > 1:
            expanded = expanded + " " + " ".join(parts[1:])
        return expanded, True
    return expression, False


def _normalize_field(value: str) -> str:
    """Normalize a single cron field value."""
    if value == "*":
        return value
    # Remove leading zeros from numbers in lists and ranges
    parts = value.split(",")
    normalized_parts = []
    for part in parts:
        if "/" in part:
            base, step = part.split("/", 1)
            base = "-".join(str(int(x)) for x in base.split("-")) if base != "*" else base
            normalized_parts.append(f"{base}/{int(step)}")
        elif "-" in part:
            start, end = part.split("-", 1)
            normalized_parts.append(f"{int(start)}-{int(end)}")
        else:
            normalized_parts.append(str(int(part)))
    return ",".join(normalized_parts)


def normalize(expression: str) -> NormalizeResult:
    """Normalize a crontab expression to its canonical form."""
    expanded, was_shorthand = _expand_shorthand(expression)

    try:
        parsed: ParsedCron = parse(expanded)
    except ParseError as exc:
        return NormalizeResult(
            original=expression,
            normalized=None,
            was_shorthand=was_shorthand,
            error=str(exc),
        )

    normalized_fields = [
        _normalize_field(field.raw)
        for field in [
            parsed.minute,
            parsed.hour,
            parsed.day_of_month,
            parsed.month,
            parsed.day_of_week,
        ]
    ]
    normalized_expr = " ".join(normalized_fields)
    if parsed.command:
        normalized_expr = f"{normalized_expr} {parsed.command}"

    return NormalizeResult(
        original=expression,
        normalized=normalized_expr,
        was_shorthand=was_shorthand,
    )
