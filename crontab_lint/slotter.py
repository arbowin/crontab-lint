"""Slot analyzer: divides a day into N equal time slots and counts runs per slot."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .linter import lint
from .schedule import _matches_field
from .parser import parse, ParseError


@dataclass
class Slot:
    label: str
    start_hour: int
    end_hour: int  # exclusive
    run_count: int

    def to_dict(self) -> dict:
        return {
            "label": self.label,
            "start_hour": self.start_hour,
            "end_hour": self.end_hour,
            "run_count": self.run_count,
        }


@dataclass
class SlotResult:
    expression: str
    is_valid: bool
    error: str
    slots: List[Slot] = field(default_factory=list)

    @property
    def total_runs(self) -> int:
        return sum(s.run_count for s in self.slots)

    @property
    def busiest_slot(self) -> Slot | None:
        if not self.slots:
            return None
        return max(self.slots, key=lambda s: s.run_count)


def _slot_label(start: int, end: int) -> str:
    return f"{start:02d}:00-{end:02d}:00"


def slot(expression: str, n: int = 4) -> SlotResult:
    """Divide a day into *n* equal slots and count how many times the job fires in each."""
    if n < 1:
        n = 1

    result = lint(expression)
    if not result.is_valid:
        msg = result.issues[0].message if result.issues else "Invalid expression"
        return SlotResult(expression=expression, is_valid=False, error=msg)

    try:
        parsed = parse(expression)
    except ParseError as exc:
        return SlotResult(expression=expression, is_valid=False, error=str(exc))

    minute_field = parsed.fields[0].raw
    hour_field = parsed.fields[1].raw

    hours_per_slot = 24 // n
    slots: List[Slot] = []

    for i in range(n):
        start_h = i * hours_per_slot
        end_h = start_h + hours_per_slot if i < n - 1 else 24
        count = 0
        for h in range(start_h, end_h):
            if _matches_field(hour_field, h, 0, 23):
                for m in range(60):
                    if _matches_field(minute_field, m, 0, 59):
                        count += 1
        slots.append(Slot(label=_slot_label(start_h, end_h), start_hour=start_h, end_hour=end_h, run_count=count))

    return SlotResult(expression=expression, is_valid=True, error="", slots=slots)


def format_slot_result(result: SlotResult) -> str:
    if not result.is_valid:
        return f"ERROR: {result.error}"
    lines = [f"Expression : {result.expression}"]
    for s in result.slots:
        bar = "#" * min(s.run_count, 40)
        lines.append(f"  {s.label}  {s.run_count:>5}  {bar}")
    lines.append(f"Total runs : {result.total_runs}")
    if result.busiest_slot:
        lines.append(f"Busiest    : {result.busiest_slot.label} ({result.busiest_slot.run_count} runs)")
    return "\n".join(lines)
