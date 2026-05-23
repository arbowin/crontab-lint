"""Annotator module: attach inline comments to crontab expressions."""

from dataclasses import dataclass
from typing import List

from crontab_lint.linter import LintResult, lint
from crontab_lint.explainer import explain


@dataclass
class AnnotatedLine:
    """A crontab line paired with an inline annotation comment."""

    original: str
    annotation: str
    is_comment: bool = False
    is_blank: bool = False

    def render(self, column: int = 60) -> str:
        """Render the line with the annotation aligned to *column*."""
        if self.is_blank:
            return ""
        if self.is_comment:
            return self.original
        padding = max(1, column - len(self.original))
        return f"{self.original}{' ' * padding}# {self.annotation}"


def _annotation_for(result: LintResult) -> str:
    """Build a short annotation string from a LintResult."""
    if result.parsed is None:
        issues = "; ".join(i.message for i in result.issues)
        return f"ERROR: {issues}"
    errors = [i for i in result.issues if i.severity == "error"]
    warnings = [i for i in result.issues if i.severity == "warning"]
    parts: List[str] = []
    if errors:
        parts.append("ERROR: " + "; ".join(e.message for e in errors))
    elif warnings:
        parts.append("WARN: " + "; ".join(w.message for w in warnings))
    if result.parsed is not None and not errors:
        parts.append(explain(result.parsed))
    return " | ".join(parts) if parts else "OK"


def annotate_lines(lines: List[str], column: int = 60) -> List[AnnotatedLine]:
    """Return an AnnotatedLine for every input line."""
    annotated: List[AnnotatedLine] = []
    for raw in lines:
        stripped = raw.strip()
        if stripped == "":
            annotated.append(AnnotatedLine(original=raw, annotation="", is_blank=True))
            continue
        if stripped.startswith("#"):
            annotated.append(AnnotatedLine(original=raw, annotation="", is_comment=True))
            continue
        result = lint(stripped)
        annotation = _annotation_for(result)
        annotated.append(AnnotatedLine(original=raw, annotation=annotation))
    return annotated


def render_annotated(lines: List[str], column: int = 60) -> str:
    """Annotate *lines* and return the full rendered block as a string."""
    return "\n".join(al.render(column) for al in annotate_lines(lines, column))
