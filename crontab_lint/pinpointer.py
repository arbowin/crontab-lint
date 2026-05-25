"""Pinpointer: identify which field(s) in a cron expression contain issues."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import ParsedCron, ParseError, parse
from .validator import validate, ValidationIssue

FIELD_NAMES = ["minute", "hour", "day_of_month", "month", "day_of_week"]


@dataclass
class FieldPin:
    field_name: str
    field_index: int  # 0-based
    raw_value: str
    issues: List[ValidationIssue]

    def has_errors(self) -> bool:
        return any(i.severity == "error" for i in self.issues)

    def has_warnings(self) -> bool:
        return any(i.severity == "warning" for i in self.issues)


@dataclass
class PinpointResult:
    expression: str
    is_valid: bool
    parse_error: Optional[str]
    pins: List[FieldPin]

    def fields_with_issues(self) -> List[FieldPin]:
        return [p for p in self.pins if p.issues]

    def fields_with_errors(self) -> List[FieldPin]:
        return [p for p in self.pins if p.has_errors()]

    def fields_with_warnings(self) -> List[FieldPin]:
        return [p for p in self.pins if p.has_warnings()]


def pinpoint(expression: str) -> PinpointResult:
    """Analyse each cron field individually and return per-field issue pins."""
    try:
        parsed: ParsedCron = parse(expression)
    except ParseError as exc:
        return PinpointResult(
            expression=expression,
            is_valid=False,
            parse_error=str(exc),
            pins=[],
        )

    result = validate(expression)
    cron_fields = [
        parsed.minute,
        parsed.hour,
        parsed.day_of_month,
        parsed.month,
        parsed.day_of_week,
    ]

    pins: List[FieldPin] = []
    for idx, (name, cron_field) in enumerate(zip(FIELD_NAMES, cron_fields)):
        field_issues = [
            issue
            for issue in result.issues
            if issue.field == name
        ]
        pins.append(
            FieldPin(
                field_name=name,
                field_index=idx,
                raw_value=cron_field.raw,
                issues=field_issues,
            )
        )

    return PinpointResult(
        expression=expression,
        is_valid=result.valid,
        parse_error=None,
        pins=pins,
    )


def format_pinpoint_result(result: PinpointResult) -> str:
    """Return a human-readable summary of per-field issues."""
    lines = [f"Expression : {result.expression}"]
    if result.parse_error:
        lines.append(f"Parse error: {result.parse_error}")
        return "\n".join(lines)

    status = "valid" if result.is_valid else "invalid"
    lines.append(f"Status     : {status}")
    problematic = result.fields_with_issues()
    if not problematic:
        lines.append("No per-field issues found.")
    else:
        for pin in problematic:
            for issue in pin.issues:
                lines.append(
                    f"  [{issue.severity.upper()}] {pin.field_name} "
                    f"('{pin.raw_value}'): {issue.message}"
                )
    return "\n".join(lines)
