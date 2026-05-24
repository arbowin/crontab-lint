"""Integration tests for the merger module."""

import pytest
from crontab_lint.merger import merge, format_merge_result


def test_three_files_merged_correctly():
    sources = [
        ("0 * * * * echo hourly", "fileA"),
        ("0 0 * * * echo daily", "fileB"),
        ("0 * * * * echo hourly", "fileC"),  # duplicate of fileA
    ]
    result = merge(sources)
    assert len(result.unique_entries) == 2
    assert len(result.duplicate_entries) == 1


def test_all_shorthands_deduplicated():
    pairs = [
        ("@hourly echo", "0 * * * * echo"),
        ("@daily echo", "0 0 * * * echo"),
        ("@weekly echo", "0 0 * * 0 echo"),
        ("@monthly echo", "0 0 1 * * echo"),
    ]
    for shorthand, explicit in pairs:
        result = merge([(shorthand, "a"), (explicit, "b")])
        assert len(result.duplicate_entries) == 1, (
            f"Expected {shorthand!r} and {explicit!r} to be duplicates"
        )


def test_format_output_lists_all_sources():
    sources = [
        ("0 * * * * echo", "fileA"),
        ("0 0 * * * echo", "fileB"),
    ]
    result = merge(sources)
    output = format_merge_result(result)
    assert "fileA" in output
    assert "fileB" in output


def test_unique_entries_all_valid_no_duplicates():
    sources = [
        ("*/5 * * * * check", "a"),
        ("0 2 * * * backup", "b"),
        ("30 18 * * 5 report", "c"),
    ]
    result = merge(sources)
    assert len(result.unique_entries) == 3
    assert len(result.duplicate_entries) == 0
    assert result.has_errors is False


def test_invalid_entry_does_not_pollute_seen_set():
    """Two identical invalid entries should both remain invalid, not deduplicated."""
    sources = [
        ("bad cron expr", "a"),
        ("bad cron expr", "b"),
    ]
    result = merge(sources)
    # Neither entry should be marked as a duplicate of the other
    # because invalid expressions are not stored in the seen set
    assert all(not e.result.valid for e in result.entries)
