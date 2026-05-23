"""Summarize multiple crontab expressions into a grouped report."""

from dataclasses import dataclass, field
from typing import Dict, List

from crontab_lint.linter import LintResult, lint_many


@dataclass
class SummaryReport:
    total: int = 0
    valid: int = 0
    warnings: int = 0
    errors: int = 0
    by_severity: Dict[str, List[str]] = field(default_factory=lambda: {
        "valid": [],
        "warning": [],
        "error": [],
    })

    def severity_for(self, result: LintResult) -> str:
        if result.errors:
            return "error"
        if result.warnings:
            return "warning"
        return "valid"


def summarize(expressions: List[str]) -> SummaryReport:
    """Lint all expressions and return an aggregated SummaryReport."""
    results = lint_many(expressions)
    report = SummaryReport(total=len(results))

    for result in results:
        severity = report.severity_for(result)
        expr = result.expression
        report.by_severity[severity].append(expr)
        if severity == "error":
            report.errors += 1
        elif severity == "warning":
            report.warnings += 1
        else:
            report.valid += 1

    return report


def format_summary(report: SummaryReport) -> str:
    """Return a human-readable summary string for a SummaryReport."""
    lines = [
        f"Crontab Lint Summary",
        f"====================",
        f"Total expressions : {report.total}",
        f"Valid             : {report.valid}",
        f"Warnings          : {report.warnings}",
        f"Errors            : {report.errors}",
    ]

    if report.by_severity["error"]:
        lines.append("\nExpressions with errors:")
        for expr in report.by_severity["error"]:
            lines.append(f"  - {expr}")

    if report.by_severity["warning"]:
        lines.append("\nExpressions with warnings:")
        for expr in report.by_severity["warning"]:
            lines.append(f"  - {expr}")

    return "\n".join(lines)
