"""Tests for crontab_lint.snapshotter."""

import json
import os
import tempfile

import pytest

from crontab_lint.snapshotter import (
    SnapshotEntry,
    Snapshot,
    SnapshotDiff,
    take_snapshot,
    diff_snapshots,
    save_snapshot,
    load_snapshot,
)


def test_take_snapshot_returns_snapshot():
    result = take_snapshot(["* * * * * echo hi"])
    assert isinstance(result, Snapshot)


def test_take_snapshot_has_timestamp():
    result = take_snapshot(["* * * * * echo hi"])
    assert result.timestamp


def test_take_snapshot_entry_count_matches_input():
    exprs = ["* * * * * cmd", "0 * * * * cmd", "0 0 * * * cmd"]
    result = take_snapshot(exprs)
    assert len(result.entries) == 3


def test_take_snapshot_valid_expression():
    result = take_snapshot(["0 12 * * * run"])
    assert result.entries[0].is_valid is True


def test_take_snapshot_invalid_expression():
    result = take_snapshot(["99 99 99 99 99 bad"])
    assert result.entries[0].is_valid is False


def test_take_snapshot_error_count_for_invalid():
    result = take_snapshot(["99 * * * * cmd"])
    assert result.entries[0].error_count >= 1


def test_take_snapshot_explanation_present():
    result = take_snapshot(["0 9 * * 1 cmd"])
    assert isinstance(result.entries[0].explanation, str)


def test_snapshot_entry_to_dict_keys():
    entry = SnapshotEntry(
        expression="* * * * * x",
        is_valid=True,
        error_count=0,
        warning_count=0,
        explanation="every minute",
    )
    d = entry.to_dict()
    assert set(d.keys()) == {"expression", "is_valid", "error_count", "warning_count", "explanation"}


def test_snapshot_entry_roundtrip():
    entry = SnapshotEntry("* * * * * x", True, 0, 1, "every minute")
    assert SnapshotEntry.from_dict(entry.to_dict()) == entry


def test_snapshot_to_dict_has_entries():
    snap = take_snapshot(["* * * * * x"])
    d = snap.to_dict()
    assert "entries" in d
    assert "timestamp" in d


def test_snapshot_roundtrip():
    snap = take_snapshot(["0 0 * * * x", "* * * * * y"])
    restored = Snapshot.from_dict(snap.to_dict())
    assert restored.timestamp == snap.timestamp
    assert len(restored.entries) == 2


def test_diff_no_changes():
    snap = take_snapshot(["* * * * * x"])
    diff = diff_snapshots(snap, snap)
    assert not diff.has_changes


def test_diff_detects_added():
    old = take_snapshot(["* * * * * x"])
    new = take_snapshot(["* * * * * x", "0 0 * * * y"])
    diff = diff_snapshots(old, new)
    assert "0 0 * * * y" in diff.added


def test_diff_detects_removed():
    old = take_snapshot(["* * * * * x", "0 0 * * * y"])
    new = take_snapshot(["* * * * * x"])
    diff = diff_snapshots(old, new)
    assert "0 0 * * * y" in diff.removed


def test_save_and_load_snapshot(tmp_path):
    path = str(tmp_path / "snap.json")
    snap = take_snapshot(["0 6 * * * morning"])
    save_snapshot(snap, path)
    loaded = load_snapshot(path)
    assert loaded is not None
    assert loaded.timestamp == snap.timestamp


def test_load_snapshot_missing_file(tmp_path):
    result = load_snapshot(str(tmp_path / "nonexistent.json"))
    assert result is None
