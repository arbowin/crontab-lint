"""Compare multiple crontab expressions and group them by schedule equivalence."""

from dataclasses import dataclass, field
from typing import List, Dict

from .normalizer import normalize


@dataclass
class ComparisonGroup:
    canonical: str
    expressions: List[str]

    def size(self) -> int:
        return len(self.expressions)

    def is_duplicate(self) -> bool:
        return len(self.expressions) > 1


@dataclass
class ComparisonResult:
    groups: List[ComparisonGroup] = field(default_factory=list)
    unresolvable: List[str] = field(default_factory=list)

    def duplicate_groups(self) -> List[ComparisonGroup]:
        return [g for g in self.groups if g.is_duplicate()]

    def has_duplicates(self) -> bool:
        return any(g.is_duplicate() for g in self.groups)

    def total_expressions(self) -> int:
        return sum(g.size() for g in self.groups) + len(self.unresolvable)


def compare(expressions: List[str]) -> ComparisonResult:
    """Group expressions by their normalized (canonical) form."""
    canonical_map: Dict[str, List[str]] = {}
    unresolvable: List[str] = []

    for expr in expressions:
        result = normalize(expr)
        if result.normalized is None:
            unresolvable.append(expr)
            continue
        key = result.normalized
        canonical_map.setdefault(key, []).append(expr)

    groups = [
        ComparisonGroup(canonical=canonical, expressions=exprs)
        for canonical, exprs in canonical_map.items()
    ]

    return ComparisonResult(groups=groups, unresolvable=unresolvable)


def format_comparison(result: ComparisonResult) -> str:
    """Return a human-readable summary of the comparison result."""
    lines = []

    if not result.groups and not result.unresolvable:
        return "No expressions to compare."

    if result.has_duplicates():
        lines.append("Duplicate schedules detected:")
        for group in result.duplicate_groups():
            lines.append(f"  Canonical: {group.canonical}")
            for expr in group.expressions:
                lines.append(f"    - {expr}")
    else:
        lines.append("No duplicate schedules found.")

    if result.unresolvable:
        lines.append("Could not normalize:")
        for expr in result.unresolvable:
            lines.append(f"  - {expr}")

    return "\n".join(lines)
