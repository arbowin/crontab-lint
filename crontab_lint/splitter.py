"""Split a list of cron expressions into valid and invalid buckets."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from .linter import lint, LintResult


@dataclass
class SplitResult:
    valid: List[LintResult] = field(default_factory=list)
    invalid: List[LintResult] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.valid) + len(self.invalid)

    @property
    def valid_count(self) -> int:
        return len(self.valid)

    @property
    def invalid_count(self) -> int:
        return len(self.invalid)


def split(expressions: List[str]) -> SplitResult:
    """Lint each expression and split into valid / invalid buckets."""
    result = SplitResult()
    for expr in expressions:
        lr = lint(expr)
        if lr.is_valid:
            result.valid.append(lr)
        else:
            result.invalid.append(lr)
    return result


def format_split_result(result: SplitResult) -> str:
    """Return a human-readable summary of the split result."""
    lines: List[str] = [
        f"Total : {result.total}",
        f"Valid : {result.valid_count}",
        f"Invalid: {result.invalid_count}",
    ]
    if result.valid:
        lines.append("\nValid expressions:")
        for lr in result.valid:
            lines.append(f"  {lr.expression}")
    if result.invalid:
        lines.append("\nInvalid expressions:")
        for lr in result.invalid:
            issues = "; ".join(i.message for i in lr.issues)
            lines.append(f"  {lr.expression}  [{issues}]")
    return "\n".join(lines)
