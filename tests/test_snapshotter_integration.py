"""Integration tests for the snapshotter module."""

from crontab_lint.snapshotter import (
    take_snapshot,
    diff_snapshots,
    save_snapshot,
    load_snapshot,
)


STANDARD_EXPRESSIONS = [
    "* * * * * every_minute",
    "0 * * * * every_hour",
    "0 0 * * * daily",
    "0 0 * * 0 weekly",
    "0 0 1 * * monthly",
]


def test_all_standard_expressions_are_valid():
    snap = take_snapshot(STANDARD_EXPRESSIONS)
    assert all(e.is_valid for e in snap.entries)


def test_all_standard_expressions_have_zero_errors():
    snap = take_snapshot(STANDARD_EXPRESSIONS)
    assert all(e.error_count == 0 for e in snap.entries)


def test_snapshot_entry_count_matches():
    snap = take_snapshot(STANDARD_EXPRESSIONS)
    assert len(snap.entries) == len(STANDARD_EXPRESSIONS)


def test_roundtrip_preserves_all_expressions(tmp_path):
    path = str(tmp_path / "snap.json")
    snap = take_snapshot(STANDARD_EXPRESSIONS)
    save_snapshot(snap, path)
    loaded = load_snapshot(path)
    assert loaded is not None
    loaded_exprs = [e.expression for e in loaded.entries]
    for expr in STANDARD_EXPRESSIONS:
        assert expr in loaded_exprs


def test_diff_added_expression_detected():
    old = take_snapshot(STANDARD_EXPRESSIONS[:3])
    new = take_snapshot(STANDARD_EXPRESSIONS)
    diff = diff_snapshots(old, new)
    assert len(diff.added) == 2
    assert not diff.removed


def test_diff_removed_expression_detected():
    old = take_snapshot(STANDARD_EXPRESSIONS)
    new = take_snapshot(STANDARD_EXPRESSIONS[:3])
    diff = diff_snapshots(old, new)
    assert len(diff.removed) == 2
    assert not diff.added


def test_invalid_expression_recorded_correctly():
    snap = take_snapshot(["99 99 99 99 99 bad"])
    entry = snap.entries[0]
    assert not entry.is_valid
    assert entry.error_count > 0


def test_mixed_snapshot_separates_valid_and_invalid():
    snap = take_snapshot(["* * * * * good", "99 99 99 99 99 bad"])
    valid = [e for e in snap.entries if e.is_valid]
    invalid = [e for e in snap.entries if not e.is_valid]
    assert len(valid) == 1
    assert len(invalid) == 1
