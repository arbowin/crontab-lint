"""Template-based cron expression generator with named presets."""

from dataclasses import dataclass
from typing import Optional

from crontab_lint.linter import LintResult, lint


TEMPLATES: dict[str, tuple[str, str]] = {
    "every_minute": ("* * * * *", "Run every minute"),
    "every_hour": ("0 * * * *", "Run at the top of every hour"),
    "every_day": ("0 0 * * *", "Run once a day at midnight"),
    "every_week": ("0 0 * * 0", "Run once a week on Sunday at midnight"),
    "every_month": ("0 0 1 * *", "Run on the first day of every month"),
    "every_year": ("0 0 1 1 *", "Run once a year on January 1st"),
    "weekdays_9am": ("0 9 * * 1-5", "Run at 9am on weekdays"),
    "weekends_noon": ("0 12 * * 6,0", "Run at noon on weekends"),
    "every_15_minutes": ("*/15 * * * *", "Run every 15 minutes"),
    "every_6_hours": ("0 */6 * * *", "Run every 6 hours"),
    "nightly_backup": ("0 2 * * *", "Run nightly at 2am"),
    "monthly_report": ("0 8 1 * *", "Run on the 1st of each month at 8am"),
}


@dataclass
class TemplateResult:
    name: str
    expression: str
    description: str
    lint_result: LintResult


def list_templates() -> list[str]:
    """Return all available template names."""
    return list(TEMPLATES.keys())


def get_template(name: str) -> Optional[TemplateResult]:
    """Look up a template by name and return a linted TemplateResult, or None."""
    entry = TEMPLATES.get(name)
    if entry is None:
        return None
    expression, description = entry
    result = lint(expression)
    return TemplateResult(
        name=name,
        expression=expression,
        description=description,
        lint_result=result,
    )


def search_templates(keyword: str) -> list[TemplateResult]:
    """Search templates whose name or description contains the keyword."""
    keyword_lower = keyword.lower()
    results = []
    for name, (expression, description) in TEMPLATES.items():
        if keyword_lower in name or keyword_lower in description.lower():
            result = lint(expression)
            results.append(TemplateResult(
                name=name,
                expression=expression,
                description=description,
                lint_result=result,
            ))
    return results


def format_template(tmpl: TemplateResult) -> str:
    """Format a TemplateResult as a human-readable string."""
    lines = [
        f"Name:        {tmpl.name}",
        f"Expression:  {tmpl.expression}",
        f"Description: {tmpl.description}",
        f"Explanation: {tmpl.lint_result.explanation}",
    ]
    return "\n".join(lines)
