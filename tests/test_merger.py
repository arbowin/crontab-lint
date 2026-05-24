"""Tests for crontab_lint.merger."""

import pytest
from crontab_lint.merger import (
    MergeEntry,
    MergeResult,
    merge,
    format_merge_result,
    _canonical,
)


def test_merge_returns_merge_result():
    result = merge([("* * * * * echo hi", "fileA")])
    assert isinstance(result, MergeResult)


def test_merge_empty_list():
    result = merge([])
    assert result.entries == []
    assert result.unique_entries == []
    assert result.duplicate_entries == []


def test_merge_single_expression_is_unique():
    result = merge([("0 * * * * echo", "a")])
    assert len(result.unique_entries) == 1
    assert len(result.duplicate_entries) == 0


def test_merge_identical_expressions_second_is_duplicate():
    sources = [
        ("0 * * * * echo", "a"),
        ("0 * * * * echo", "b"),
    ]
    result = merge(sources)
    assert len(result.unique_entries) == 1
    assert len(result.duplicate_entries) == 1
    assert result.duplicate_entries[0].duplicate_of == "0 * * * * echo"


def test_merge_different_expressions_both_unique():
    sources = [
        ("0 * * * * echo", "a"),
        ("0 0 * * * echo", "b"),
    ]
    result = merge(sources)
    assert len(result.unique_entries) == 2
    assert len(result.duplicate_entries) == 0


def test_merge_shorthand_and_explicit_are_duplicates():
    sources = [
        ("@hourly echo", "a"),
        ("0 * * * * echo", "b"),
    ]
    result = merge(sources)
    assert len(result.duplicate_entries) == 1


def test_merge_invalid_expression_not_tracked_as_seen():
    sources = [
        ("bad expr", "a"),
        ("bad expr", "b"),
    ]
    result = merge(sources)
    # Both invalid — neither is stored as canonical seed
    assert all(not e.result.valid for e in result.entries)


def test_merge_has_errors_when_invalid_present():
    sources = [
        ("0 * * * * echo", "a"),
        ("not valid", "b"),
    ]
    result = merge(sources)
    assert result.has_errors is True


def test_merge_no_errors_all_valid():
    sources = [
        ("0 * * * * echo", "a"),
        ("30 6 * * * echo", "b"),
    ]
    result = merge(sources)
    assert result.has_errors is False


def test_format_merge_result_contains_summary():
    result = merge([("0 * * * * echo", "a")])
    output = format_merge_result(result)
    assert "Merge summary" in output
    assert "1 total" in output


def test_format_merge_result_marks_duplicate():
    sources = [("0 * * * * echo", "a"), ("0 * * * * echo", "b")]
    result = merge(sources)
    output = format_merge_result(result)
    assert "[DUPLICATE]" in output


def test_format_merge_result_verbose_shows_original():
    sources = [("0 * * * * echo", "a"), ("0 * * * * echo", "b")]
    result = merge(sources)
    output = format_merge_result(result, verbose=True)
    assert "duplicate of" in output


def test_canonical_normalizes_shorthand():
    assert _canonical("@hourly echo") == _canonical("0 * * * * echo")
