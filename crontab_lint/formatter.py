"""Human-readable formatting for lint results."""

from crontab_lint.linter import LintResult
from crontab_lint.validator import ValidationIssue


SEVERITY_ICONS = {
    "error": "✗",
    "warning": "⚠",
    "info": "ℹ",
}

SEVERITY_LABELS = {
    "error": "ERROR",
    "warning": "WARNING",
    "info": "INFO",
}


def _format_issue(issue: ValidationIssue) -> str:
    icon = SEVERITY_ICONS.get(issue.severity, "?")
    label = SEVERITY_LABELS.get(issue.severity, issue.severity.upper())
    return f"  {icon} [{label}] {issue.message}"


def format_result(result: LintResult, verbose: bool = False) -> str:
    """Format a single LintResult into a human-readable string."""
    lines = []
    lines.append(f"Expression: {result.expression}")

    if result.explanation:
        lines.append(f"Meaning:    {result.explanation}")

    if result.issues:
        lines.append("Issues:")
        for issue in result.issues:
            lines.append(_format_issue(issue))
    elif verbose:
        lines.append("  ✓ No issues found")

    status = "INVALID" if result.has_errors else ("WARNING" if result.has_warnings else "OK")
    lines.append(f"Status:     {status}")

    return "\n".join(lines)


def format_many(results: list[LintResult], verbose: bool = False) -> str:
    """Format multiple LintResults into a summary report."""
    if not results:
        return "No expressions to lint."

    sections = []
    for i, result in enumerate(results, start=1):
        header = f"[{i}/{len(results)}] "
        body = format_result(result, verbose=verbose)
        indented = "\n".join(
            (header + line if j == 0 else "       " + line)
            for j, line in enumerate(body.splitlines())
        )
        sections.append(indented)

    total = len(results)
    errors = sum(1 for r in results if r.has_errors)
    warnings = sum(1 for r in results if r.has_warnings and not r.has_errors)
    ok = total - errors - warnings

    summary_lines = [
        "-" * 50,
        f"Summary: {total} expression(s) — {ok} OK, {warnings} warning(s), {errors} error(s)",
    ]

    return "\n\n".join(sections) + "\n" + "\n".join(summary_lines)
