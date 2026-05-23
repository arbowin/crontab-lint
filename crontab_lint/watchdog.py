"""Watchdog module: monitor a crontab file for changes and re-lint on update."""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

from crontab_lint.linter import LintResult, lint_many
from crontab_lint.formatter import format_many


@dataclass
class WatchEvent:
    """Represents a single watch cycle result."""

    path: str
    changed: bool
    results: List[LintResult] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def has_errors(self) -> bool:
        return any(r.is_valid is False for r in self.results)


def _file_hash(path: Path) -> str:
    """Return MD5 hex digest of file contents."""
    try:
        return hashlib.md5(path.read_bytes()).hexdigest()
    except OSError:
        return ""


def _read_expressions(path: Path) -> List[str]:
    """Read non-blank, non-comment lines from a crontab file."""
    lines: List[str] = []
    try:
        for line in path.read_text().splitlines():
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                lines.append(stripped)
    except OSError:
        pass
    return lines


def watch(
    filepath: str,
    interval: float = 2.0,
    max_cycles: Optional[int] = None,
    on_event: Optional[Callable[[WatchEvent], None]] = None,
) -> None:
    """Poll *filepath* every *interval* seconds and re-lint when it changes.

    Args:
        filepath:   Path to the crontab file to watch.
        interval:   Seconds between polls.
        max_cycles: Stop after this many cycles (``None`` = run forever).
        on_event:   Callback invoked with a :class:`WatchEvent` on every cycle
                    where the file changed (or on the first cycle).
    """
    path = Path(filepath)
    last_hash = ""
    cycles = 0

    while max_cycles is None or cycles < max_cycles:
        current_hash = _file_hash(path)
        changed = current_hash != last_hash

        if changed:
            last_hash = current_hash
            expressions = _read_expressions(path)
            if not path.exists():
                event = WatchEvent(path=filepath, changed=True, error=f"File not found: {filepath}")
            else:
                results = lint_many(expressions)
                event = WatchEvent(path=filepath, changed=True, results=results)

            if on_event:
                on_event(event)

        cycles += 1
        if max_cycles is None or cycles < max_cycles:
            time.sleep(interval)
