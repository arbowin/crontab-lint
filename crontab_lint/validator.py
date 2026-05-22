from dataclasses import dataclass
from typing import List, Optional
from .parser import ParsedCron, CronField, ParseError, parse


@dataclass
class ValidationIssue:
    field: str
    message: str
    severity: str  # 'error' or 'warning'


@dataclass
class ValidationResult:
    valid: bool
    issues: List[ValidationIssue]

    def has_errors(self) -> bool:
        return any(i.severity == 'error' for i in self.issues)

    def has_warnings(self) -> bool:
        return any(i.severity == 'warning' for i in self.issues)


FIELD_RANGES = {
    'minute':     (0, 59),
    'hour':       (0, 23),
    'day_of_month': (1, 31),
    'month':      (1, 12),
    'day_of_week': (0, 7),
}


def _check_field(field: CronField) -> List[ValidationIssue]:
    issues = []
    name = field.name
    raw = field.raw
    lo, hi = FIELD_RANGES[name]

    if raw == '*':
        return issues

    parts = raw.split(',')
    for part in parts:
        if '/' in part:
            base, step_str = part.split('/', 1)
            try:
                step = int(step_str)
                if step <= 0:
                    issues.append(ValidationIssue(name, f"Step value must be >= 1, got {step}", 'error'))
                elif step > (hi - lo):
                    issues.append(ValidationIssue(name, f"Step {step} exceeds field range ({lo}-{hi})", 'warning'))
            except ValueError:
                issues.append(ValidationIssue(name, f"Invalid step value: '{step_str}'", 'error'))
            part = base

        if part == '*':
            continue

        if '-' in part:
            bounds = part.split('-', 1)
            try:
                a, b = int(bounds[0]), int(bounds[1])
                if a > b:
                    issues.append(ValidationIssue(name, f"Range start {a} > end {b}", 'error'))
                if not (lo <= a <= hi) or not (lo <= b <= hi):
                    issues.append(ValidationIssue(name, f"Range {a}-{b} out of bounds ({lo}-{hi})", 'error'))
            except (ValueError, IndexError):
                issues.append(ValidationIssue(name, f"Invalid range: '{part}'", 'error'))
        else:
            try:
                val = int(part)
                if not (lo <= val <= hi):
                    issues.append(ValidationIssue(name, f"Value {val} out of bounds ({lo}-{hi})", 'error'))
            except ValueError:
                issues.append(ValidationIssue(name, f"Invalid value: '{part}'", 'error'))

    return issues


def validate(expression: str) -> ValidationResult:
    try:
        parsed = parse(expression)
    except ParseError as e:
        return ValidationResult(
            valid=False,
            issues=[ValidationIssue('expression', str(e), 'error')]
        )

    issues = []
    for field in [parsed.minute, parsed.hour, parsed.day_of_month, parsed.month, parsed.day_of_week]:
        issues.extend(_check_field(field))

    if parsed.day_of_month.raw != '*' and parsed.day_of_week.raw != '*':
        issues.append(ValidationIssue(
            'day_of_month/day_of_week',
            'Both day-of-month and day-of-week are specified; results may be platform-dependent',
            'warning'
        ))

    return ValidationResult(valid=not any(i.severity == 'error' for i in issues), issues=issues)
