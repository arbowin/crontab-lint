"""Group crontab expressions by their schedule pattern or tag."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .linter import lint
from .tagger import tag


@dataclass
class GroupResult:
    groups: Dict[str, List[str]]
    ungrouped: List[str]

    def group_names(self) -> List[str]:
        return sorted(self.groups.keys())

    def members(self, group_name: str) -> List[str]:
        return self.groups.get(group_name, [])


def has_group(result: GroupResult, name: str) -> bool:
    return name in result.groups


def _primary_tag(expression: str) -> Optional[str]:
    """Return the most descriptive tag for an expression, or None if invalid."""
    tag_result = tag(expression)
    if not tag_result.valid:
        return None
    if not tag_result.tags:
        return "other"
    priority = ["yearly", "monthly", "weekly", "daily", "hourly", "every_minute"]
    for p in priority:
        if p in tag_result.tags:
            return p
    return tag_result.tags[0]


def group(expressions: List[str], by: str = "tag") -> GroupResult:
    """Group expressions by 'tag' (default) or 'validity'."""
    groups: Dict[str, List[str]] = {}
    ungrouped: List[str] = []

    for expr in expressions:
        if by == "validity":
            result = lint(expr)
            key = "valid" if result.valid else "invalid"
        elif by == "tag":
            key = _primary_tag(expr)
            if key is None:
                ungrouped.append(expr)
                continue
        else:
            raise ValueError(f"Unknown grouping strategy: {by!r}")

        groups.setdefault(key, []).append(expr)

    return GroupResult(groups=groups, ungrouped=ungrouped)


def format_group_result(result: GroupResult) -> str:
    lines = []
    for name in result.group_names():
        members = result.members(name)
        lines.append(f"[{name}] ({len(members)} expression(s))")
        for expr in members:
            lines.append(f"  {expr}")
    if result.ungrouped:
        lines.append(f"[ungrouped] ({len(result.ungrouped)} expression(s))")
        for expr in result.ungrouped:
            lines.append(f"  {expr}")
    return "\n".join(lines)
