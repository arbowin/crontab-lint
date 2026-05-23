"""Export lint results to structured formats (JSON, CSV)."""

from __future__ import annotations

import csv
import io
import json
from typing import List

from crontab_lint.linter import LintResult


def _result_to_dict(result: LintResult) -> dict:
    """Convert a LintResult to a plain dictionary."""
    issues = [
        {
            "severity": issue.severity,
            "message": issue.message,
            "field": issue.field,
        }
        for issue in result.validation.issues
    ]
    return {
        "expression": result.expression,
        "valid": result.validation.valid,
        "explanation": result.explanation,
        "issues": issues,
    }


def to_json(results: List[LintResult], indent: int = 2) -> str:
    """Serialize a list of LintResults to a JSON string."""
    data = [_result_to_dict(r) for r in results]
    return json.dumps(data, indent=indent)


def to_csv(results: List[LintResult]) -> str:
    """Serialize a list of LintResults to CSV.

    Each row contains: expression, valid, explanation, severity, field, message.
    Expressions with no issues produce a single row with empty issue columns.
    """
    output = io.StringIO()
    fieldnames = ["expression", "valid", "explanation", "severity", "field", "message"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for result in results:
        base = {
            "expression": result.expression,
            "valid": result.validation.valid,
            "explanation": result.explanation,
        }
        if result.validation.issues:
            for issue in result.validation.issues:
                writer.writerow(
                    {
                        **base,
                        "severity": issue.severity,
                        "field": issue.field or "",
                        "message": issue.message,
                    }
                )
        else:
            writer.writerow({**base, "severity": "", "field": "", "message": ""})

    return output.getvalue()
