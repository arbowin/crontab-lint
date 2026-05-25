"""Inspector: deep field-level analysis of a cron expression."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .validator import validate


@dataclass
class FieldInspection:
    name: str
    raw: str
    kind: str          # 'wildcard' | 'value' | 'range' | 'step' | 'list' | 'unknown'
    values: List[int]  # concrete values implied by the field (empty if wildcard)
    note: str          # human-readable note about the field

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "raw": self.raw,
            "kind": self.kind,
            "values": self.values,
            "note": self.note,
        }


@dataclass
class InspectResult:
    expression: str
    is_valid: bool
    error: Optional[str]
    fields: List[FieldInspection] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "is_valid": self.is_valid,
            "error": self.error,
            "fields": [f.to_dict() for f in self.fields],
        }


_RANGES = {
    "minute": (0, 59),
    "hour": (0, 23),
    "day_of_month": (1, 31),
    "month": (1, 12),
    "day_of_week": (0, 6),
}


def _detect_kind(raw: str) -> str:
    if raw == "*":
        return "wildcard"
    if "," in raw:
        return "list"
    if "-" in raw and "/" not in raw:
        return "range"
    if "/" in raw:
        return "step"
    if raw.isdigit():
        return "value"
    return "unknown"


def _expand_values(raw: str, lo: int, hi: int) -> List[int]:
    """Return the sorted list of concrete integers the field token represents."""
    if raw == "*":
        return []
    results: set[int] = set()
    for part in raw.split(","):
        if "/" in part:
            base, step_str = part.split("/", 1)
            step = int(step_str)
            start, end = (lo, hi) if base == "*" else map(int, base.split("-")) if "-" in base else (int(base), hi)
            results.update(range(start, end + 1, step))
        elif "-" in part:
            a, b = part.split("-", 1)
            results.update(range(int(a), int(b) + 1))
        else:
            results.add(int(part))
    return sorted(results)


def _make_note(kind: str, name: str, values: List[int]) -> str:
    if kind == "wildcard":
        return f"Matches every {name.replace('_', ' ')}"
    if kind == "value":
        return f"Exactly {values[0]}"
    if kind == "range":
        return f"Range from {values[0]} to {values[-1]}"
    if kind == "step":
        return f"{len(values)} value(s) via step: {values}"
    if kind == "list":
        return f"Explicit list: {values}"
    return "Unrecognised pattern"


def inspect(expression: str) -> InspectResult:
    try:
        parsed = parse(expression)
    except ParseError as exc:
        return InspectResult(expression=expression, is_valid=False, error=str(exc))

    result = validate(expression)
    if result.has_errors():
        msg = "; ".join(i.message for i in result.issues if i.severity == "error")
        return InspectResult(expression=expression, is_valid=False, error=msg)

    inspections: List[FieldInspection] = []
    field_names = ["minute", "hour", "day_of_month", "month", "day_of_week"]
    cron_fields = [parsed.minute, parsed.hour, parsed.day_of_month, parsed.month, parsed.day_of_week]

    for name, cf in zip(field_names, cron_fields):
        lo, hi = _RANGES[name]
        kind = _detect_kind(cf.raw)
        values = _expand_values(cf.raw, lo, hi)
        note = _make_note(kind, name, values)
        inspections.append(FieldInspection(name=name, raw=cf.raw, kind=kind, values=values, note=note))

    return InspectResult(expression=expression, is_valid=True, error=None, fields=inspections)
