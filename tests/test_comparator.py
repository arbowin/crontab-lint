"""Tests for crontab_lint.comparator module."""

import pytest
from crontab_lint.comparator import compare, format_comparison, ComparisonGroup, ComparisonResult


def test_compare_empty_list():
    result = compare([])
    assert result.groups == []
    assert result.unresolvable == []
    assert result.total_expressions() == 0


def test_compare_single_expression():
    result = compare(["0 * * * * echo hi"])
    assert len(result.groups) == 1
    assert result.groups[0].size() == 1
    assert not result.has_duplicates()


def test_compare_two_identical_expressions():
    result = compare(["0 * * * * echo hi", "0 * * * * echo hello"])
    assert len(result.groups) == 1
    assert result.groups[0].size() == 2
    assert result.has_duplicates()


def test_compare_two_different_expressions():
    result = compare(["0 * * * * cmd", "30 * * * * cmd"])
    assert len(result.groups) == 2
    assert not result.has_duplicates()


def test_compare_shorthand_and_explicit_are_equivalent():
    result = compare(["@daily /bin/backup", "0 0 * * * /bin/backup"])
    assert len(result.groups) == 1
    assert result.groups[0].size() == 2
    assert result.has_duplicates()


def test_compare_invalid_expression_goes_to_unresolvable():
    result = compare(["not-a-cron"])
    assert len(result.unresolvable) == 1
    assert result.unresolvable[0] == "not-a-cron"
    assert len(result.groups) == 0


def test_compare_mixed_valid_and_invalid():
    result = compare(["0 * * * * cmd", "bad expression"])
    assert len(result.groups) == 1
    assert len(result.unresolvable) == 1
    assert result.total_expressions() == 2


def test_duplicate_groups_returns_only_duplicates():
    result = compare(["0 * * * * a", "0 * * * * b", "5 * * * * c"])
    dupes = result.duplicate_groups()
    assert len(dupes) == 1
    assert dupes[0].size() == 2


def test_format_comparison_no_duplicates():
    result = compare(["0 * * * * cmd"])
    output = format_comparison(result)
    assert "No duplicate schedules found" in output


def test_format_comparison_with_duplicates():
    result = compare(["0 0 * * * a", "0 0 * * * b"])
    output = format_comparison(result)
    assert "Duplicate schedules detected" in output


def test_format_comparison_empty():
    result = compare([])
    output = format_comparison(result)
    assert "No expressions to compare" in output


def test_format_comparison_shows_unresolvable():
    result = compare(["bad"])
    output = format_comparison(result)
    assert "Could not normalize" in output
    assert "bad" in output


def test_total_expressions_counts_valid_and_invalid():
    """total_expressions() should include both grouped and unresolvable entries."""
    result = compare(["0 * * * * a", "0 * * * * b", "invalid1", "invalid2"])
    assert result.total_expressions() == 4
    assert len(result.unresolvable) == 2
    assert len(result.groups) == 1
    assert result.groups[0].size() == 2
