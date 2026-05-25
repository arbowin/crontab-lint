"""Digest module: produce a compact fingerprint/summary dict for a cron expression."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .parser import parse, ParseError
from .validator import validate
from .explainer import explain
from .tagger import tag
from .profiler import profile


@dataclass
class DigestResult:
    expression: str
    is_valid: bool
    fingerprint: str
    explanation: str
    tags: list[str]
    runs_per_day: Optional[float]
    error: Optional[str]
    fields: dict[str, str]

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "is_valid": self.is_valid,
            "fingerprint": self.fingerprint,
            "explanation": self.explanation,
            "tags": self.tags,
            "runs_per_day": self.runs_per_day,
            "error": self.error,
            "fields": self.fields,
        }


def _make_fingerprint(expression: str) -> str:
    """Return a short stable fingerprint string for the expression."""
    import hashlib
    normalized = " ".join(expression.split())
    return hashlib.sha1(normalized.encode()).hexdigest()[:12]


def digest(expression: str) -> DigestResult:
    """Produce a DigestResult summarising all key facts about *expression*."""
    fingerprint = _make_fingerprint(expression)

    try:
        parsed = parse(expression)
    except ParseError as exc:
        return DigestResult(
            expression=expression,
            is_valid=False,
            fingerprint=fingerprint,
            explanation="",
            tags=[],
            runs_per_day=None,
            error=str(exc),
            fields={},
        )

    result = validate(expression)
    is_valid = not any(i.severity == "error" for i in result.issues)

    explanation = explain(parsed) if is_valid else ""

    tag_result = tag(expression)
    tags = list(tag_result.tags)

    prof = profile(expression)
    runs_per_day = prof.runs_per_day if is_valid else None

    fields = {
        f.name: f.raw
        for f in [
            parsed.minute,
            parsed.hour,
            parsed.day_of_month,
            parsed.month,
            parsed.day_of_week,
        ]
    }

    error = next((i.message for i in result.issues if i.severity == "error"), None)

    return DigestResult(
        expression=expression,
        is_valid=is_valid,
        fingerprint=fingerprint,
        explanation=explanation,
        tags=tags,
        runs_per_day=runs_per_day,
        error=error,
        fields=fields,
    )
