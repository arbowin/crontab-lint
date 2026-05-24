"""Score crontab expressions by complexity and readability."""

from dataclasses import dataclass, field
from typing import List

from .parser import parse, ParseError
from .validator import validate


@dataclass
class ScoreResult:
    expression: str
    score: int  # 0 (worst) to 100 (best)
    grade: str
    penalties: List[str] = field(default_factory=list)
    is_valid: bool = True


def _grade(score: int) -> str:
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score >= 60:
        return "C"
    if score >= 40:
        return "D"
    return "F"


def _count_parts(value: str) -> int:
    """Count distinct parts in a field (commas = list complexity)."""
    return len(value.split(","))


def score(expression: str) -> ScoreResult:
    """Score a crontab expression from 0 to 100."""
    penalties: List[str] = []

    try:
        parsed = parse(expression)
    except ParseError as exc:
        return ScoreResult(
            expression=expression,
            score=0,
            grade="F",
            penalties=[str(exc)],
            is_valid=False,
        )

    result = validate(parsed)
    if not result.valid:
        msgs = [i.message for i in result.issues if i.severity == "error"]
        return ScoreResult(
            expression=expression,
            score=0,
            grade="F",
            penalties=msgs,
            is_valid=False,
        )

    deduction = 0

    # Penalise validation warnings
    warning_count = sum(1 for i in result.issues if i.severity == "warning")
    if warning_count:
        deduction += warning_count * 10
        penalties.append(f"{warning_count} validation warning(s)")

    fields = [parsed.minute, parsed.hour, parsed.day_of_month, parsed.month, parsed.day_of_week]
    for f_obj in fields:
        parts = _count_parts(f_obj.raw)
        if parts > 5:
            deduction += 10
            penalties.append(f"Field '{f_obj.name}' has many list items ({parts})")
        if "/" in f_obj.raw and f_obj.raw.startswith("*/"):
            pass  # clean step — no penalty
        elif "/" in f_obj.raw:
            deduction += 5
            penalties.append(f"Field '{f_obj.name}' uses non-standard step syntax")

    final_score = max(0, min(100, 100 - deduction))
    return ScoreResult(
        expression=expression,
        score=final_score,
        grade=_grade(final_score),
        penalties=penalties,
        is_valid=True,
    )


def format_score_result(result: ScoreResult) -> str:
    lines = [
        f"Expression : {result.expression}",
        f"Score      : {result.score}/100 (Grade {result.grade})",
    ]
    if result.penalties:
        lines.append("Penalties  :")
        for p in result.penalties:
            lines.append(f"  - {p}")
    else:
        lines.append("Penalties  : none")
    return "\n".join(lines)
