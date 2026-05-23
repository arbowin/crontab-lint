"""Suggest fixes or alternatives for invalid or problematic crontab expressions."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import ParseError, parse
from .validator import validate, ValidationIssue


@dataclass
class Suggestion:
    message: str
    suggested_expression: Optional[str] = None


@dataclass
class SuggestionResult:
    original: str
    suggestions: List[Suggestion] = field(default_factory=list)

    def has_suggestions(self) -> bool:
        return len(self.suggestions) > 0


_SHORTHAND_MAP = {
    "0 0 * * *": "@daily",
    "0 * * * *": "@hourly",
    "0 0 * * 0": "@weekly",
    "0 0 1 * *": "@monthly",
    "0 0 1 1 *": "@yearly",
    "* * * * *": "@reboot",
}


def _normalize_whitespace(expression: str) -> str:
    parts = expression.strip().split()
    if len(parts) >= 6:
        fields = parts[:5]
        return " ".join(fields)
    return " ".join(parts)


def _suggest_shorthand(expression: str) -> Optional[Suggestion]:
    key = _normalize_whitespace(expression)
    shorthand = _SHORTHAND_MAP.get(key)
    if shorthand:
        return Suggestion(
            message=f"This expression can be written as the shorthand '{shorthand}'.",
            suggested_expression=shorthand,
        )
    return None


def _suggest_fixes_for_issues(issues: List[ValidationIssue], expression: str) -> List[Suggestion]:
    suggestions = []
    for issue in issues:
        if "out of range" in issue.message.lower():
            suggestions.append(
                Suggestion(
                    message=f"Fix: {issue.message} — check the valid range for the '{issue.field}' field."
                )
            )
        elif "both" in issue.message.lower() and "day-of-month" in issue.message.lower():
            suggestions.append(
                Suggestion(
                    message="Consider using only day-of-month OR day-of-week to avoid ambiguous scheduling."
                )
            )
        else:
            suggestions.append(Suggestion(message=f"Issue in '{issue.field}': {issue.message}"))
    return suggestions


def suggest(expression: str) -> SuggestionResult:
    """Analyse an expression and return actionable suggestions."""
    result = SuggestionResult(original=expression)

    try:
        parsed = parse(expression)
    except ParseError as exc:
        result.suggestions.append(Suggestion(message=f"Parse error: {exc}"))
        return result

    validation = validate(parsed)
    if not validation.valid:
        result.suggestions.extend(
            _suggest_fixes_for_issues(validation.issues, expression)
        )
        return result

    shorthand = _suggest_shorthand(expression)
    if shorthand:
        result.suggestions.append(shorthand)

    return result
