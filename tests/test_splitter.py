"""Tests for crontab_lint.splitter."""

import pytest
from crontab_lint.splitter import split, format_split_result, SplitResult


def test_split_returns_split_result():
    result = split(["* * * * * echo hi"])
    assert isinstance(result, SplitResult)


def test_split_empty_list():
    result = split([])
    assert result.total == 0
    assert result.valid_count == 0
    assert result.invalid_count == 0


def test_split_single_valid_expression():
    result = split(["0 * * * * echo hi"])
    assert result.valid_count == 1
    assert result.invalid_count == 0


def test_split_single_invalid_expression():
    result = split(["99 * * * * echo hi"])
    assert result.valid_count == 0
    assert result.invalid_count == 1


def test_split_mixed_expressions():
    result = split(["0 * * * * echo hi", "99 * * * * echo hi", "*/5 * * * * echo hi"])
    assert result.valid_count == 2
    assert result.invalid_count == 1


def test_split_total_equals_input_length():
    exprs = ["0 * * * * echo hi", "99 * * * * echo hi"]
    result = split(exprs)
    assert result.total == len(exprs)


def test_split_valid_entries_have_lint_results():
    from crontab_lint.linter import LintResult
    result = split(["0 0 * * * echo hi"])
    assert all(isinstance(lr, LintResult) for lr in result.valid)


def test_split_invalid_entries_have_lint_results():
    from crontab_lint.linter import LintResult
    result = split(["invalid"])
    assert all(isinstance(lr, LintResult) for lr in result.invalid)


def test_format_split_result_contains_total():
    result = split(["0 * * * * echo hi"])
    output = format_split_result(result)
    assert "Total" in output
    assert "1" in output


def test_format_split_result_lists_valid_expressions():
    result = split(["0 0 * * * echo hi"])
    output = format_split_result(result)
    assert "0 0 * * * echo hi" in output


def test_format_split_result_lists_invalid_expressions():
    result = split(["99 99 * * * echo hi"])
    output = format_split_result(result)
    assert "99 99 * * * echo hi" in output


def test_format_split_result_shows_issue_for_invalid():
    result = split(["99 * * * * echo hi"])
    output = format_split_result(result)
    assert "[" in output


def test_split_all_valid_invalid_count_zero():
    exprs = ["0 * * * * cmd", "*/5 * * * * cmd", "0 0 * * * cmd"]
    result = split(exprs)
    assert result.invalid_count == 0
