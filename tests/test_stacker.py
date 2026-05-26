"""Tests for crontab_lint.stacker."""

import datetime
import pytest

from crontab_lint.stacker import stack, format_stack_result, StackResult, OverlapEntry


START = datetime.datetime(2024, 1, 1, 0, 0)


def test_stack_returns_stack_result():
    result = stack(["* * * * * echo a", "* * * * * echo b"], start=START)
    assert isinstance(result, StackResult)


def test_stack_empty_list_is_not_valid():
    result = stack([], start=START)
    assert not result.is_valid


def test_stack_single_valid_expression_no_overlaps():
    result = stack(["0 * * * * echo a"], start=START)
    assert result.is_valid
    assert not result.has_overlaps()


def test_stack_two_identical_expressions_have_overlaps():
    result = stack(["0 * * * * echo a", "0 * * * * echo b"], start=START)
    assert result.is_valid
    assert result.has_overlaps()


def test_stack_two_non_overlapping_expressions_no_overlaps():
    result = stack(["0 * * * * echo a", "30 * * * * echo b"], start=START)
    assert result.is_valid
    assert not result.has_overlaps()


def test_stack_invalid_expression_recorded():
    result = stack(["bad expr", "0 * * * * echo ok"], start=START)
    assert "bad expr" in result.invalid_expressions
    assert result.is_valid  # at least one valid


def test_stack_all_invalid_is_not_valid():
    result = stack(["bad", "also bad"], start=START)
    assert not result.is_valid
    assert result.error != ""


def test_stack_overlap_entry_has_both_expressions():
    result = stack(["0 * * * * echo a", "0 * * * * echo b"], start=START)
    assert result.has_overlaps()
    first = result.overlaps[0]
    assert isinstance(first, OverlapEntry)
    assert len(first.expressions) == 2


def test_stack_overlap_count_matches():
    result = stack(["* * * * * echo a", "* * * * * echo b"], hours=1, start=START)
    assert result.overlap_count() == 60


def test_stack_valid_expressions_list_populated():
    result = stack(["0 * * * * echo a", "0 * * * * echo b"], start=START)
    assert len(result.valid_expressions) == 2


def test_overlap_entry_to_dict():
    ts = datetime.datetime(2024, 1, 1, 6, 0)
    entry = OverlapEntry(timestamp=ts, expressions=["a", "b"])
    d = entry.to_dict()
    assert d["timestamp"] == ts.isoformat()
    assert d["expressions"] == ["a", "b"]


def test_format_stack_result_valid_no_overlaps():
    result = stack(["0 * * * * echo a", "30 * * * * echo b"], start=START)
    text = format_stack_result(result)
    assert "No overlapping" in text


def test_format_stack_result_with_overlaps():
    result = stack(["0 * * * * echo a", "0 * * * * echo b"], start=START)
    text = format_stack_result(result)
    assert "Overlapping" in text


def test_format_stack_result_invalid():
    result = stack(["bad"], start=START)
    text = format_stack_result(result)
    assert "Error" in text
