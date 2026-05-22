from dataclasses import dataclass
from typing import Optional
from .parser import parse, ParseError
from .explainer import explain
from .validator import validate, ValidationResult


@dataclass
class LintResult:
    expression: str
    command: Optional[str]
    valid: bool
    explanation: Optional[str]
    validation: ValidationResult

    def summary(self) -> str:
        lines = []
        status = '✓ valid' if self.valid else '✗ invalid'
        lines.append(f"[{status}] {self.expression}")

        if self.explanation:
            lines.append(f"  Schedule: {self.explanation}")

        if self.command:
            lines.append(f"  Command:  {self.command}")

        if self.validation.issues:
            lines.append("  Issues:")
            for issue in self.validation.issues:
                icon = '✗' if issue.severity == 'error' else '⚠'
                lines.append(f"    {icon} [{issue.field}] {issue.message}")

        return '\n'.join(lines)


def lint(expression: str) -> LintResult:
    validation = validate(expression)

    try:
        parsed = parse(expression)
        explanation = explain(parsed)
        command = parsed.command
    except ParseError:
        explanation = None
        command = None

    return LintResult(
        expression=expression,
        command=command,
        valid=validation.valid,
        explanation=explanation,
        validation=validation,
    )


def lint_many(expressions: list) -> list:
    return [lint(expr) for expr in expressions]
