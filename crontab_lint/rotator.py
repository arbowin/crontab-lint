"""Rotate a list of cron expressions by shifting their minute/hour offsets
to spread load across time slots."""

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import lint
from .parser import parse, ParseError


@dataclass
class RotateEntry:
    original: str
    rotated: str
    is_valid: bool
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "original": self.original,
            "rotated": self.rotated,
            "is_valid": self.is_valid,
            "error": self.error,
        }


@dataclass
class RotateResult:
    entries: List[RotateEntry] = field(default_factory=list)
    step: int = 1

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.is_valid)

    @property
    def invalid_count(self) -> int:
        return self.total - self.valid_count


def _shift_minute(value: str, offset: int) -> str:
    """Shift a minute field value by offset, wrapping at 60."""
    if value == "*":
        return value
    try:
        minute = int(value)
        return str((minute + offset) % 60)
    except ValueError:
        return value


def rotate(expressions: List[str], step: int = 5) -> RotateResult:
    """Rotate each expression's minute field by step * index to spread load."""
    result = RotateResult(step=step)
    for idx, expr in enumerate(expressions):
        offset = (idx * step) % 60
        try:
            parsed = parse(expr)
            parts = expr.split(None, 5)
            parts[0] = _shift_minute(parts[0], offset)
            rotated = " ".join(parts)
            entry = RotateEntry(
                original=expr,
                rotated=rotated,
                is_valid=True,
            )
        except ParseError as exc:
            entry = RotateEntry(
                original=expr,
                rotated=expr,
                is_valid=False,
                error=str(exc),
            )
        result.entries.append(entry)
    return result


def format_rotate_result(result: RotateResult) -> str:
    lines = [f"Rotated {result.total} expression(s) with step={result.step}:"]
    for entry in result.entries:
        if entry.is_valid:
            lines.append(f"  {entry.original!r:30s} -> {entry.rotated!r}")
        else:
            lines.append(f"  {entry.original!r:30s} [ERROR: {entry.error}]")
    return "\n".join(lines)
