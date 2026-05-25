"""Trimmer: remove redundant or duplicate fields from crontab expressions."""

from dataclasses import dataclass, field
from typing import List, Optional

from .parser import parse, ParseError
from .validator import validate


@dataclass
class TrimResult:
    expression: str
    trimmed: str
    is_valid: bool
    error: Optional[str]
    removed_redundancy: List[str] = field(default_factory=list)
    changed: bool = False


def _is_redundant_step(value: str) -> bool:
    """Return True if a step value is redundant (e.g. */1)."""
    if value.startswith("*/"):
        try:
            return int(value[2:]) == 1
        except ValueError:
            return False
    return False


def _simplify_field(raw: str) -> tuple[str, Optional[str]]:
    """Return (simplified_value, reason) or (original, None) if no change."""
    stripped = raw.strip()
    if _is_redundant_step(stripped):
        return "*", f"'{stripped}' simplified to '*' (step of 1 is redundant)"
    # Collapse single-item lists
    if "," not in stripped and "-" not in stripped and "/" not in stripped:
        return stripped, None
    parts = stripped.split(",")
    if len(parts) == 1:
        return stripped, None
    deduped = list(dict.fromkeys(parts))
    if len(deduped) < len(parts):
        joined = ",".join(deduped)
        return joined, f"'{stripped}' deduplicated to '{joined}'"
    return stripped, None


def trim(expression: str) -> TrimResult:
    """Trim redundant constructs from a cron expression."""
    try:
        parsed = parse(expression)
    except ParseError as exc:
        return TrimResult(
            expression=expression,
            trimmed=expression,
            is_valid=False,
            error=str(exc),
        )

    result = validate(expression)
    if not result.valid:
        first_error = result.issues[0].message if result.issues else "invalid expression"
        return TrimResult(
            expression=expression,
            trimmed=expression,
            is_valid=False,
            error=first_error,
        )

    fields = [parsed.minute, parsed.hour, parsed.day_of_month, parsed.month, parsed.day_of_week]
    new_fields = []
    reasons: List[str] = []

    for f_val in fields:
        simplified, reason = _simplify_field(f_val)
        new_fields.append(simplified)
        if reason:
            reasons.append(reason)

    trimmed_expr = " ".join(new_fields)
    if parsed.command:
        trimmed_expr += f" {parsed.command}"

    changed = trimmed_expr != expression

    return TrimResult(
        expression=expression,
        trimmed=trimmed_expr,
        is_valid=True,
        error=None,
        removed_redundancy=reasons,
        changed=changed,
    )


def format_trim_result(result: TrimResult) -> str:
    """Format a TrimResult as a human-readable string."""
    lines = [f"Expression : {result.expression}"]
    if not result.is_valid:
        lines.append(f"Error      : {result.error}")
        return "\n".join(lines)
    lines.append(f"Trimmed    : {result.trimmed}")
    lines.append(f"Changed    : {'yes' if result.changed else 'no'}")
    if result.removed_redundancy:
        lines.append("Changes:")
        for note in result.removed_redundancy:
            lines.append(f"  - {note}")
    return "\n".join(lines)
