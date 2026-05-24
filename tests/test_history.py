"""Tests for crontab_lint.history module."""

import json
import os
import tempfile

import pytest

from crontab_lint.history import (
    History,
    HistoryEntry,
    load_history,
    record,
    save_history,
)
from crontab_lint.linter import lint


def _make_entry(expression: str = "* * * * * echo hi") -> HistoryEntry:
    result = lint(expression)
    h = History()
    return h.add(result)


def test_history_add_returns_entry():
    result = lint("0 * * * * echo hi")
    h = History()
    entry = h.add(result)
    assert isinstance(entry, HistoryEntry)
    assert entry.expression == "0 * * * * echo hi"


def test_history_entry_valid_expression():
    entry = _make_entry("0 9 * * 1 run-job")
    assert entry.valid is True
    assert entry.error_count == 0


def test_history_entry_invalid_expression():
    entry = _make_entry("99 * * * * bad")
    assert entry.valid is False
    assert entry.error_count >= 1


def test_history_entry_has_timestamp():
    entry = _make_entry()
    assert entry.timestamp
    assert "T" in entry.timestamp  # ISO format


def test_history_filter_valid():
    h = History()
    h.add(lint("0 * * * * ok"))
    h.add(lint("99 * * * * bad"))
    valid = h.filter_valid()
    assert len(valid) == 1
    assert valid[0].valid is True


def test_history_filter_invalid():
    h = History()
    h.add(lint("0 * * * * ok"))
    h.add(lint("99 * * * * bad"))
    invalid = h.filter_invalid()
    assert len(invalid) == 1
    assert invalid[0].valid is False


def test_history_last_limits_results():
    h = History()
    for i in range(15):
        h.add(lint(f"0 {i % 24} * * * job{i}"))
    assert len(h.last(5)) == 5
    assert len(h.last(20)) == 15


def test_history_entry_round_trip():
    entry = _make_entry("30 6 * * * backup")
    d = entry.to_dict()
    restored = HistoryEntry.from_dict(d)
    assert restored.expression == entry.expression
    assert restored.valid == entry.valid
    assert restored.error_count == entry.error_count


def test_save_and_load_history():
    h = History()
    h.add(lint("0 * * * * job1"))
    h.add(lint("30 12 * * * job2"))
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        save_history(h, path)
        loaded = load_history(path)
        assert len(loaded.entries) == 2
        assert loaded.entries[0].expression == "0 * * * * job1"
    finally:
        os.unlink(path)


def test_save_history_produces_valid_json():
    """Ensure save_history writes valid JSON that can be parsed independently."""
    h = History()
    h.add(lint("0 * * * * job1"))
    with tempfile.NamedTemporaryFile(suffix=".json", delete=False) as f:
        path = f.name
    try:
        save_history(h, path)
        with open(path) as f:
            data = json.load(f)
        assert isinstance(data, list)
        assert len(data) == 1
        assert "expression" in data[0]
    finally:
        os.unlink(path)


def test_load_history_missing_file_returns_empty():
    h = load_history("/tmp/does_not_exist_crontab_lint_xyz.json")
    assert h.entries == []


def test_record_convenience_function():
    h = History()
    entry = record("0 0 * * * nightly", h)
    assert entry.expression == "0 0 * * * nightly"
    assert len(h.entries) == 1
