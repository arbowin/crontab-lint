"""Diff two crontab expressions and summarize what changed."""

from dataclasses import dataclass
from typing import List

from .parser import ParsedCron, parse, ParseError
from .explainer import _explain_field


@dataclass
class FieldDiff:
    field: str
    old_value: str
    new_value: str
    old_explanation: str
    new_explanation: str

    def summary(self) -> str:
        return (
            f"{self.field}: '{self.old_value}' -> '{self.new_value}'\n"
            f"  was: {self.old_explanation}\n"
            f"  now: {self.new_explanation}"
        )


@dataclass
class DiffResult:
    old_expression: str
    new_expression: str
    command_changed: bool
    field_diffs: List[FieldDiff]

    @property
    def has_changes(self) -> bool:
        return self.command_changed or bool(self.field_diffs)

    def summary(self) -> str:
        if not self.has_changes:
            return "No changes detected."
        lines = []
        if self.command_changed:
            lines.append(
                f"command: '{self.old_expression.split(None, 5)[-1]}'"
                f" -> '{self.new_expression.split(None, 5)[-1]}'"
            )
        for diff in self.field_diffs:
            lines.append(diff.summary())
        return "\n".join(lines)


def diff(old: str, new: str) -> DiffResult:
    """Compare two crontab expression strings and return a DiffResult.

    Raises ParseError if either expression cannot be parsed.
    """
    old_parsed: ParsedCron = parse(old)
    new_parsed: ParsedCron = parse(new)

    field_diffs: List[FieldDiff] = []
    for old_field, new_field in zip(old_parsed.fields, new_parsed.fields):
        if old_field.raw != new_field.raw:
            field_diffs.append(
                FieldDiff(
                    field=old_field.name,
                    old_value=old_field.raw,
                    new_value=new_field.raw,
                    old_explanation=_explain_field(old_field),
                    new_explanation=_explain_field(new_field),
                )
            )

    old_cmd = old_parsed.command or ""
    new_cmd = new_parsed.command or ""

    return DiffResult(
        old_expression=old,
        new_expression=new,
        command_changed=old_cmd != new_cmd,
        field_diffs=field_diffs,
    )
