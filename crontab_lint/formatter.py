"""Format lint results and (optionally) upcoming schedule for human output."""

from __future__ import annotations

from typing import List

from .linter import LintResult
from .validator import ValidationIssue


def _format_issue(issue: ValidationIssue) -> str:
    level = issue.level.upper()
    return f"  [{level}] {issue.message}"


def format_result(result: LintResult, verbose: bool = False, show_next: int = 0) -> str:
    """Return a human-readable string describing *result*.

    Parameters
    ----------
    result:
        A ``LintResult`` produced by :func:`crontab_lint.linter.lint`.
    verbose:
        When *True*, always print the explanation even if there are no issues.
    show_next:
        If greater than 0, append the next *show_next* scheduled run times.
        Requires the expression to be valid; silently skipped otherwise.
    """
    lines: List[str] = []
    lines.append(f"Expression : {result.expression}")

    if result.explanation:
        lines.append(f"Explanation: {result.explanation}")

    if not result.issues:
        if verbose:
            lines.append("Status     : OK")
    else:
        for issue in result.issues:
            lines.append(_format_issue(issue))

    if show_next > 0 and result.valid:
        try:
            from .schedule import next_runs  # local import to keep module optional

            runs = next_runs(result.expression, count=show_next)
            lines.append(f"Next {show_next} run(s):")
            for dt in runs:
                lines.append(f"  {dt.strftime('%Y-%m-%d %H:%M')}")
        except Exception:  # pragma: no cover
            pass

    return "\n".join(lines)


def format_many(results: List[LintResult], verbose: bool = False, show_next: int = 0) -> str:
    """Format multiple lint results separated by blank lines."""
    sections = [format_result(r, verbose=verbose, show_next=show_next) for r in results]
    return "\n\n".join(sections)
