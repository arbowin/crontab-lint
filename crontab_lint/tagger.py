"""Tag crontab expressions with descriptive labels based on their schedule pattern."""

from dataclasses import dataclass, field
from typing import List

from .linter import lint, LintResult
from .parser import ParsedCron


@dataclass
class TagResult:
    expression: str
    tags: List[str]
    is_valid: bool

    def has_tag(self, tag: str) -> bool:
        return tag in self.tags


def _tags_for(parsed: ParsedCron) -> List[str]:
    tags: List[str] = []

    minute = parsed.minute.raw
    hour = parsed.hour.raw
    dom = parsed.day_of_month.raw
    month = parsed.month.raw
    dow = parsed.day_of_week.raw

    # Frequency tags
    if minute == "*" and hour == "*":
        tags.append("frequent")
    elif minute.startswith("*/"):
        tags.append("interval")
    elif minute == "0" and hour == "*":
        tags.append("hourly")
    elif minute == "0" and hour == "0":
        tags.append("daily")
        if dom == "*" and month == "*" and dow == "1":
            tags.append("weekly")
        elif dom == "1" and month == "*":
            tags.append("monthly")
        elif dom == "1" and month == "1":
            tags.append("yearly")

    # Day-of-week tags
    if dow in ("1-5", "1,2,3,4,5"):
        tags.append("weekdays")
    elif dow in ("6,0", "0,6", "6-7", "0,7"):
        tags.append("weekends")

    # Midnight tag
    if minute == "0" and hour == "0":
        tags.append("midnight")

    # Wildcard
    if all(f == "*" for f in [minute, hour, dom, month, dow]):
        tags.append("every-minute")

    return tags


def tag(expression: str) -> TagResult:
    """Tag a crontab expression with descriptive labels."""
    result: LintResult = lint(expression)
    if not result.is_valid or result.parsed is None:
        return TagResult(expression=expression, tags=[], is_valid=False)
    tags = _tags_for(result.parsed)
    return TagResult(expression=expression, tags=tags, is_valid=True)


def format_tag_result(result: TagResult) -> str:
    """Return a human-readable string for a TagResult."""
    if not result.is_valid:
        return f"{result.expression}  [invalid — no tags]"
    if not result.tags:
        return f"{result.expression}  [no tags]"
    label = ", ".join(result.tags)
    return f"{result.expression}  [{label}]"
