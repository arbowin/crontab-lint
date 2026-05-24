"""Snapshot module: capture and compare lint states over time."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import List, Optional

from .linter import LintResult, lint


@dataclass
class SnapshotEntry:
    expression: str
    is_valid: bool
    error_count: int
    warning_count: int
    explanation: str

    def to_dict(self) -> dict:
        return {
            "expression": self.expression,
            "is_valid": self.is_valid,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "explanation": self.explanation,
        }

    @staticmethod
    def from_dict(d: dict) -> "SnapshotEntry":
        return SnapshotEntry(
            expression=d["expression"],
            is_valid=d["is_valid"],
            error_count=d["error_count"],
            warning_count=d["warning_count"],
            explanation=d["explanation"],
        )


@dataclass
class Snapshot:
    timestamp: str
    entries: List[SnapshotEntry] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "timestamp": self.timestamp,
            "entries": [e.to_dict() for e in self.entries],
        }

    @staticmethod
    def from_dict(d: dict) -> "Snapshot":
        return Snapshot(
            timestamp=d["timestamp"],
            entries=[SnapshotEntry.from_dict(e) for e in d.get("entries", [])],
        )


@dataclass
class SnapshotDiff:
    added: List[str]
    removed: List[str]
    changed: List[str]

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def take_snapshot(expressions: List[str]) -> Snapshot:
    """Lint each expression and capture a snapshot of the current state."""
    timestamp = datetime.now(timezone.utc).isoformat()
    entries: List[SnapshotEntry] = []
    for expr in expressions:
        result: LintResult = lint(expr)
        entries.append(SnapshotEntry(
            expression=expr,
            is_valid=result.is_valid,
            error_count=len([i for i in result.issues if i.severity == "error"]),
            warning_count=len([i for i in result.issues if i.severity == "warning"]),
            explanation=result.explanation or "",
        ))
    return Snapshot(timestamp=timestamp, entries=entries)


def diff_snapshots(old: Snapshot, new: Snapshot) -> SnapshotDiff:
    """Compare two snapshots and return what changed."""
    old_map = {e.expression: e for e in old.entries}
    new_map = {e.expression: e for e in new.entries}

    added = [expr for expr in new_map if expr not in old_map]
    removed = [expr for expr in old_map if expr not in new_map]
    changed = [
        expr for expr in old_map
        if expr in new_map and old_map[expr].to_dict() != new_map[expr].to_dict()
    ]
    return SnapshotDiff(added=added, removed=removed, changed=changed)


def save_snapshot(snapshot: Snapshot, path: str) -> None:
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(snapshot.to_dict(), fh, indent=2)


def load_snapshot(path: str) -> Optional[Snapshot]:
    try:
        with open(path, "r", encoding="utf-8") as fh:
            return Snapshot.from_dict(json.load(fh))
    except (FileNotFoundError, KeyError, json.JSONDecodeError):
        return None
