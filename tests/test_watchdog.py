"""Tests for crontab_lint.watchdog."""

from __future__ import annotations

import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

from crontab_lint.watchdog import WatchEvent, _file_hash, _read_expressions, watch


# ---------------------------------------------------------------------------
# _file_hash
# ---------------------------------------------------------------------------

def test_file_hash_returns_string_for_existing_file(tmp_path):
    f = tmp_path / "crontab"
    f.write_text("* * * * * echo hi\n")
    h = _file_hash(f)
    assert isinstance(h, str) and len(h) == 32


def test_file_hash_returns_empty_string_for_missing_file(tmp_path):
    assert _file_hash(tmp_path / "nonexistent") == ""


def test_file_hash_changes_when_content_changes(tmp_path):
    f = tmp_path / "crontab"
    f.write_text("* * * * * echo hi")
    h1 = _file_hash(f)
    f.write_text("0 * * * * echo hi")
    h2 = _file_hash(f)
    assert h1 != h2


# ---------------------------------------------------------------------------
# _read_expressions
# ---------------------------------------------------------------------------

def test_read_expressions_skips_comments(tmp_path):
    f = tmp_path / "crontab"
    f.write_text("# a comment\n* * * * * echo hi\n")
    assert _read_expressions(f) == ["* * * * * echo hi"]


def test_read_expressions_skips_blank_lines(tmp_path):
    f = tmp_path / "crontab"
    f.write_text("\n* * * * * echo hi\n\n")
    assert _read_expressions(f) == ["* * * * * echo hi"]


def test_read_expressions_returns_empty_for_missing_file(tmp_path):
    assert _read_expressions(tmp_path / "no_file") == []


# ---------------------------------------------------------------------------
# WatchEvent
# ---------------------------------------------------------------------------

def test_watch_event_has_errors_false_when_results_empty():
    event = WatchEvent(path="/tmp/crontab", changed=True, results=[])
    assert event.has_errors is False


def test_watch_event_has_errors_true_when_invalid_result():
    from crontab_lint.linter import lint
    result = lint("bad expression")
    event = WatchEvent(path="/tmp/crontab", changed=True, results=[result])
    assert event.has_errors is True


# ---------------------------------------------------------------------------
# watch()
# ---------------------------------------------------------------------------

def test_watch_calls_on_event_when_file_changes(tmp_path):
    f = tmp_path / "crontab"
    f.write_text("* * * * * echo hello\n")

    events = []
    watch(str(f), interval=0, max_cycles=1, on_event=events.append)

    assert len(events) == 1
    assert events[0].changed is True
    assert events[0].path == str(f)


def test_watch_does_not_call_on_event_when_unchanged(tmp_path):
    f = tmp_path / "crontab"
    f.write_text("* * * * * echo hello\n")

    events = []
    # First cycle detects change; second cycle — same hash — should not fire.
    watch(str(f), interval=0, max_cycles=2, on_event=events.append)

    assert len(events) == 1


def test_watch_event_contains_lint_results(tmp_path):
    f = tmp_path / "crontab"
    f.write_text("0 * * * * /usr/bin/backup\n")

    events = []
    watch(str(f), interval=0, max_cycles=1, on_event=events.append)

    assert events[0].results
    assert events[0].error is None
