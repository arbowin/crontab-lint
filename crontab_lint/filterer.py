"""Filter a list of crontab expressions based on criteria such as validity,
tag, frequency label, or field pattern."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from .linter import lint
from .tagger import tag
from .profiler import profile


@dataclass
class FilterResult:
    """Result of a filter operation over a list of expressions."""

    matched: List[str]
    excluded: List[str]
    criteria: dict

    @property
    def match_count(self) -> int:
        return len(self.matched)

    @property
    def excluded_count(self) -> int:
        return len(self.excluded)


def _matches_validity(expression: str, only_valid: bool, only_invalid: bool) -> bool:
    """Return True if the expression satisfies the validity filter."""
    if not only_valid and not only_invalid:
        return True
    result = lint(expression)
    is_valid = not result.has_errors
    if only_valid:
        return is_valid
    if only_invalid:
        return not is_valid
    return True


def _matches_tag(expression: str, required_tag: Optional[str]) -> bool:
    """Return True if the expression carries the required tag."""
    if required_tag is None:
        return True
    tag_result = tag(expression)
    return required_tag in tag_result.tags


def _matches_frequency(expression: str, frequency: Optional[str]) -> bool:
    """Return True if the expression's frequency label matches."""
    if frequency is None:
        return True
    prof = profile(expression)
    if not prof.is_valid:
        return False
    return prof.frequency_label.lower() == frequency.lower()


def _matches_field_pattern(expression: str, field_index: int, pattern: str) -> bool:
    """Return True if the specified cron field (0-4) equals the given pattern."""
    parts = expression.strip().split()
    if len(parts) < 5:
        return False
    return parts[field_index] == pattern


def filter_expressions(
    expressions: List[str],
    *,
    only_valid: bool = False,
    only_invalid: bool = False,
    required_tag: Optional[str] = None,
    frequency: Optional[str] = None,
    minute: Optional[str] = None,
    hour: Optional[str] = None,
    day_of_month: Optional[str] = None,
    month: Optional[str] = None,
    day_of_week: Optional[str] = None,
) -> FilterResult:
    """Filter *expressions* according to the supplied criteria.

    Parameters
    ----------
    expressions:
        Raw crontab expression strings to filter.
    only_valid:
        Keep only syntactically valid expressions.
    only_invalid:
        Keep only expressions that fail validation.
    required_tag:
        Keep only expressions that carry this tag (e.g. ``"hourly"``).
    frequency:
        Keep only expressions whose frequency label matches (case-insensitive).
    minute / hour / day_of_month / month / day_of_week:
        Keep only expressions where the respective field equals the given value.
    """
    if only_valid and only_invalid:
        raise ValueError("only_valid and only_invalid are mutually exclusive")

    field_filters = [
        (0, minute),
        (1, hour),
        (2, day_of_month),
        (3, month),
        (4, day_of_week),
    ]

    criteria = {
        "only_valid": only_valid,
        "only_invalid": only_invalid,
        "required_tag": required_tag,
        "frequency": frequency,
        "minute": minute,
        "hour": hour,
        "day_of_month": day_of_month,
        "month": month,
        "day_of_week": day_of_week,
    }

    matched: List[str] = []
    excluded: List[str] = []

    for expr in expressions:
        keep = True

        if not _matches_validity(expr, only_valid, only_invalid):
            keep = False

        if keep and not _matches_tag(expr, required_tag):
            keep = False

        if keep and not _matches_frequency(expr, frequency):
            keep = False

        if keep:
            for idx, pattern in field_filters:
                if pattern is not None and not _matches_field_pattern(expr, idx, pattern):
                    keep = False
                    break

        if keep:
            matched.append(expr)
        else:
            excluded.append(expr)

    return FilterResult(matched=matched, excluded=excluded, criteria=criteria)


def format_filter_result(result: FilterResult) -> str:
    """Return a human-readable summary of the filter result."""
    lines = [
        f"Matched : {result.match_count}",
        f"Excluded: {result.excluded_count}",
    ]
    if result.matched:
        lines.append("")
        lines.append("Matched expressions:")
        for expr in result.matched:
            lines.append(f"  {expr}")
    return "\n".join(lines)
