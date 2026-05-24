"""Merge multiple crontab files into a single deduplicated, validated output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import LintResult, lint
from .normalizer import normalize


@dataclass
class MergeEntry:
    expression: str
    source: Optional[str]
    result: LintResult
    duplicate_of: Optional[str] = None

    @property
    def is_duplicate(self) -> bool:
        return self.duplicate_of is not None


@dataclass
class MergeResult:
    entries: List[MergeEntry] = field(default_factory=list)

    @property
    def unique_entries(self) -> List[MergeEntry]:
        return [e for e in self.entries if not e.is_duplicate]

    @property
    def duplicate_entries(self) -> List[MergeEntry]:
        return [e for e in self.entries if e.is_duplicate]

    @property
    def has_errors(self) -> bool:
        return any(not e.result.valid for e in self.entries)


def _canonical(expression: str) -> str:
    """Return a normalized form of expression for deduplication."""
    result = normalize(expression)
    return result.normalized if result.normalized else expression.strip()


def merge(sources: List[tuple[str, str]]) -> MergeResult:
    """Merge expressions from multiple sources.

    Args:
        sources: List of (expression, source_label) tuples.

    Returns:
        MergeResult with all entries annotated for duplicates.
    """
    seen: dict[str, str] = {}  # canonical -> original expression
    entries: List[MergeEntry] = []

    for expression, source in sources:
        result = lint(expression)
        canonical = _canonical(expression)
        duplicate_of = seen.get(canonical)

        if duplicate_of is None and result.valid:
            seen[canonical] = expression

        entries.append(MergeEntry(
            expression=expression,
            source=source,
            result=result,
            duplicate_of=duplicate_of,
        ))

    return MergeResult(entries=entries)


def format_merge_result(result: MergeResult, verbose: bool = False) -> str:
    """Format a MergeResult as human-readable text."""
    lines: List[str] = []
    total = len(result.entries)
    unique = len(result.unique_entries)
    dupes = len(result.duplicate_entries)

    lines.append(f"Merge summary: {total} total, {unique} unique, {dupes} duplicate(s)")

    for entry in result.entries:
        tag = "[DUPLICATE]" if entry.is_duplicate else ("[INVALID]" if not entry.result.valid else "[OK]")
        src = f" (from {entry.source})" if entry.source else ""
        lines.append(f"  {tag} {entry.expression}{src}")
        if verbose and entry.is_duplicate:
            lines.append(f"         duplicate of: {entry.duplicate_of}")

    return "\n".join(lines)
