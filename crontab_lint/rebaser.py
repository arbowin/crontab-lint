"""Rebaser: shift cron expression fields by a fixed offset."""

from dataclasses import dataclass, field
from typing import Optional

from .parser import parse, ParseError
from .validator import validate


@dataclass
class RebaseResult:
    expression: str
    rebased: Optional[str]
    is_valid: bool
    error: Optional[str] = None
    minute_offset: int = 0
    hour_offset: int = 0


def _shift_field(raw: str, offset: int, lo: int, hi: int) -> str:
    """Shift each concrete value in a field by offset, wrapping within [lo, hi]."""
    if offset == 0 or raw == "*":
        return raw

    span = hi - lo + 1
    parts = raw.split(",")
    result = []

    for part in parts:
        if "-" in part and not part.startswith("-"):
            a, b = part.split("-", 1)
            new_a = lo + (int(a) - lo + offset) % span
            new_b = lo + (int(b) - lo + offset) % span
            result.append(f"{new_a}-{new_b}")
        elif "/" in part:
            base, step = part.split("/", 1)
            if base == "*":
                result.append(part)
            else:
                new_base = lo + (int(base) - lo + offset) % span
                result.append(f"{new_base}/{step}")
        else:
            new_val = lo + (int(part) - lo + offset) % span
            result.append(str(new_val))

    return ",".join(result)


def rebase(
    expression: str,
    minute_offset: int = 0,
    hour_offset: int = 0,
) -> RebaseResult:
    """Return a new cron expression with minute/hour fields shifted by the given offsets."""
    try:
        parsed = parse(expression)
    except ParseError as exc:
        return RebaseResult(
            expression=expression,
            rebased=None,
            is_valid=False,
            error=str(exc),
            minute_offset=minute_offset,
            hour_offset=hour_offset,
        )

    result = validate(expression)
    if not result.valid:
        first_error = result.issues[0].message if result.issues else "invalid expression"
        return RebaseResult(
            expression=expression,
            rebased=None,
            is_valid=False,
            error=first_error,
            minute_offset=minute_offset,
            hour_offset=hour_offset,
        )

    fields = [f.raw for f in parsed.fields]
    fields[0] = _shift_field(fields[0], minute_offset, 0, 59)
    fields[1] = _shift_field(fields[1], hour_offset, 0, 23)

    rebased_expr = " ".join(fields) + " " + parsed.command

    return RebaseResult(
        expression=expression,
        rebased=rebased_expr.strip(),
        is_valid=True,
        error=None,
        minute_offset=minute_offset,
        hour_offset=hour_offset,
    )


def format_rebase_result(result: RebaseResult) -> str:
    lines = [f"Expression : {result.expression}"]
    if result.is_valid:
        lines.append(f"Rebased    : {result.rebased}")
        lines.append(f"Offsets    : minute={result.minute_offset}, hour={result.hour_offset}")
    else:
        lines.append(f"Error      : {result.error}")
    return "\n".join(lines)
