"""Audit a list of crontab expressions and produce a structured audit report."""

from dataclasses import dataclass, field
from typing import List

from .linter import lint, LintResult
from .tagger import tag
from .scorer import score
from .profiler import profile


@dataclass
class AuditEntry:
    expression: str
    lint_result: LintResult
    tags: List[str]
    grade: str
    frequency_label: str
    runs_per_day: int

    def is_valid(self) -> bool:
        return self.lint_result.valid

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "valid": self.is_valid(),
            "tags": self.tags,
            "grade": self.grade,
            "frequency_label": self.frequency_label,
            "runs_per_day": self.runs_per_day,
            "issues": [
                {"severity": i.severity, "message": i.message}
                for i in self.lint_result.issues
            ],
            "explanation": self.lint_result.explanation,
        }


@dataclass
class AuditReport:
    entries: List[AuditEntry] = field(default_factory=list)

    @property
    def total(self) -> int:
        return len(self.entries)

    @property
    def valid_count(self) -> int:
        return sum(1 for e in self.entries if e.is_valid())

    @property
    def invalid_count(self) -> int:
        return self.total - self.valid_count


def audit(expressions: List[str]) -> AuditReport:
    """Audit each expression and return a full AuditReport."""
    entries: List[AuditEntry] = []
    for expr in expressions:
        lr = lint(expr)
        tag_result = tag(expr)
        score_result = score(expr)
        profile_result = profile(expr)
        entry = AuditEntry(
            expression=expr,
            lint_result=lr,
            tags=tag_result.tags,
            grade=score_result.grade,
            frequency_label=profile_result.frequency_label,
            runs_per_day=profile_result.runs_per_day,
        )
        entries.append(entry)
    return AuditReport(entries=entries)


def format_audit_report(report: AuditReport) -> str:
    """Return a human-readable summary of the audit report."""
    lines = [
        f"Audit Report: {report.total} expression(s), "
        f"{report.valid_count} valid, {report.invalid_count} invalid.",
        "",
    ]
    for entry in report.entries:
        status = "OK" if entry.is_valid() else "INVALID"
        lines.append(f"  [{status}] {entry.expression}")
        lines.append(f"    Grade: {entry.grade}  Frequency: {entry.frequency_label}  Tags: {', '.join(entry.tags) or 'none'}")
        for issue in entry.lint_result.issues:
            lines.append(f"    [{issue.severity.upper()}] {issue.message}")
    return "\n".join(lines)
