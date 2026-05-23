"""Track and replay lint history for crontab expressions."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from crontab_lint.linter import LintResult, lint


@dataclass
class HistoryEntry:
    expression: str
    timestamp: str
    valid: bool
    error_count: int
    warning_count: int
    explanation: str

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "timestamp": self.timestamp,
            "valid": self.valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "explanation": self.explanation,
        }

    @staticmethod
    def from_dict(data: dict) -> "HistoryEntry":
        return HistoryEntry(
            expression=data["expression"],
            timestamp=data["timestamp"],
            valid=data["valid"],
            error_count=data["error_count"],
            warning_count=data["warning_count"],
            explanation=data["explanation"],
        )


@dataclass
class History:
    entries: List[HistoryEntry] = field(default_factory=list)

    def add(self, result: LintResult) -> HistoryEntry:
        entry = HistoryEntry(
            expression=result.expression,
            timestamp=datetime.now(timezone.utc).isoformat(),
            valid=result.valid,
            error_count=len([i for i in result.issues if i.severity == "error"]),
            warning_count=len([i for i in result.issues if i.severity == "warning"]),
            explanation=result.explanation or "",
        )
        self.entries.append(entry)
        return entry

    def filter_valid(self) -> List[HistoryEntry]:
        return [e for e in self.entries if e.valid]

    def filter_invalid(self) -> List[HistoryEntry]:
        return [e for e in self.entries if not e.valid]

    def last(self, n: int = 10) -> List[HistoryEntry]:
        return self.entries[-n:]


def save_history(history: History, path: str) -> None:
    data = [e.to_dict() for e in history.entries]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)


def load_history(path: str) -> History:
    if not os.path.exists(path):
        return History()
    with open(path, "r", encoding="utf-8") as fh:
        data = json.load(fh)
    return History(entries=[HistoryEntry.from_dict(d) for d in data])


def record(expression: str, history: Optional[History] = None) -> HistoryEntry:
    if history is None:
        history = History()
    result = lint(expression)
    return history.add(result)
