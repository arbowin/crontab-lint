"""Batch processor: run lint over multiple expressions and collect results by batch."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import LintResult, lint


@dataclass
class BatchEntry:
    index: int
    expression: str
    result: LintResult

    def is_valid(self) -> bool:
        return self.result.valid

    def to_dict(self) -> dict:
        return {
            "index": self.index,
            "expression": self.expression,
            "valid": self.is_valid(),
            "error_count": len([i for i in self.result.issues if i.severity == "error"]),
            "warning_count": len([i for i in self.result.issues if i.severity == "warning"]),
        }


@dataclass
class BatchResult:
    entries: List[BatchEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.is_valid())

    @property
    def invalid_count(self) -> int:
        return self.total - self.valid_count

    def valid_entries(self) -> List[BatchEntry]:
        return [e for e in self.entries if e.is_valid()]

    def invalid_entries(self) -> List[BatchEntry]:
        return [e for e in self.entries if not e.is_valid()]


def batch(expressions: List[str], stop_on_error: bool = False) -> BatchResult:
    """Lint a list of expressions and return a BatchResult.

    If *stop_on_error* is True, processing halts after the first invalid entry.
    """
    entries: List[BatchEntry] = []
    for idx, expr in enumerate(expressions):
        result = lint(expr)
        entry = BatchEntry(index=idx, expression=expr, result=result)
        entries.append(entry)
        if stop_on_error and not result.valid:
            break
    return BatchResult(entries=entries)


def format_batch_result(result: BatchResult) -> str:
    lines = [f"Batch: {result.total} expression(s), {result.valid_count} valid, {result.invalid_count} invalid."]
    for entry in result.entries:
        status = "OK" if entry.is_valid() else "FAIL"
        lines.append(f"  [{entry.index}] {status}  {entry.expression}")
        for issue in entry.result.issues:
            lines.append(f"        {issue.severity.upper()}: {issue.message}")
    return "\n".join(lines)
