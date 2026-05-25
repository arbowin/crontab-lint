"""Deduplicator: remove duplicate cron expressions from a list, preserving order."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .normalizer import normalize


@dataclass
class DeduplicateEntry:
    expression: str
    is_duplicate: bool
    first_seen_index: Optional[int]  # index of the canonical copy (None if this is the canonical)
    normalized: str

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "is_duplicate": self.is_duplicate,
            "first_seen_index": self.first_seen_index,
            "normalized": self.normalized,
        }


@dataclass
class DeduplicateResult:
    entries: List[DeduplicateEntry] = field(default_factory=list)

    @property
    def unique_expressions(self) -> List[str]:
        return [e.expression for e in self.entries if not e.is_duplicate]

    @property
    def duplicate_count(self) -> int:
        return sum(1 for e in self.entries if e.is_duplicate)

    @property
    def total(self) -> int:
        return len(self.entries)


def deduplicate(expressions: List[str]) -> DeduplicateResult:
    """Process a list of expressions and mark duplicates.

    Two expressions are considered duplicates if their normalized forms match.
    The first occurrence is kept; subsequent ones are marked as duplicates.
    """
    seen: dict[str, int] = {}  # normalized -> index of first occurrence
    entries: List[DeduplicateEntry] = []

    for expr in expressions:
        result = normalize(expr)
        if result.normalized is not None:
            norm = result.normalized
        else:
            # Invalid expressions: use the raw expression as the key
            norm = expr.strip()

        if norm in seen:
            entries.append(
                DeduplicateEntry(
                    expression=expr,
                    is_duplicate=True,
                    first_seen_index=seen[norm],
                    normalized=norm,
                )
            )
        else:
            seen[norm] = len(entries)
            entries.append(
                DeduplicateEntry(
                    expression=expr,
                    is_duplicate=False,
                    first_seen_index=None,
                    normalized=norm,
                )
            )

    return DeduplicateResult(entries=entries)


def format_deduplicate_result(result: DeduplicateResult) -> str:
    lines = []
    for i, entry in enumerate(result.entries):
        if entry.is_duplicate:
            lines.append(f"[{i}] DUPLICATE  {entry.expression!r}  (first seen at index {entry.first_seen_index})")
        else:
            lines.append(f"[{i}] UNIQUE     {entry.expression!r}")
    lines.append(f"\nTotal: {result.total}  Unique: {result.total - result.duplicate_count}  Duplicates: {result.duplicate_count}")
    return "\n".join(lines)
