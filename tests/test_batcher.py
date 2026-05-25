"""Tests for crontab_lint.batcher."""
import pytest

from crontab_lint.batcher import (
    BatchEntry,
    BatchResult,
    batch,
    format_batch_result,
)


def test_batch_returns_batch_result():
    result = batch(["* * * * * echo hi"])
    assert isinstance(result, BatchResult)


def test_batch_empty_list():
    result = batch([])
    assert result.total == 0
    assert result.valid_count == 0
    assert result.invalid_count == 0


def test_batch_single_valid_expression():
    result = batch(["0 * * * * echo hi"])
    assert result.total == 1
    assert result.valid_count == 1
    assert result.invalid_count == 0


def test_batch_single_invalid_expression():
    result = batch(["bad expression"])
    assert result.total == 1
    assert result.invalid_count == 1


def test_batch_mixed_expressions():
    exprs = ["* * * * * echo hi", "bad", "0 12 * * * echo noon"]
    result = batch(exprs)
    assert result.total == 3
    assert result.valid_count == 2
    assert result.invalid_count == 1


def test_batch_entries_have_correct_indices():
    exprs = ["* * * * * echo", "0 * * * * echo"]
    result = batch(exprs)
    assert result.entries[0].index == 0
    assert result.entries[1].index == 1


def test_batch_entry_expression_preserved():
    expr = "30 6 * * 1 echo monday"
    result = batch([expr])
    assert result.entries[0].expression == expr


def test_batch_stop_on_error_halts_after_first_failure():
    exprs = ["* * * * * echo", "bad", "0 * * * * echo"]
    result = batch(exprs, stop_on_error=True)
    assert result.total == 2


def test_batch_stop_on_error_no_error_processes_all():
    exprs = ["* * * * * echo", "0 * * * * echo"]
    result = batch(exprs, stop_on_error=True)
    assert result.total == 2


def test_batch_valid_entries_filter():
    exprs = ["* * * * * echo", "bad", "0 * * * * echo"]
    result = batch(exprs)
    assert len(result.valid_entries()) == 2


def test_batch_invalid_entries_filter():
    exprs = ["* * * * * echo", "bad"]
    result = batch(exprs)
    assert len(result.invalid_entries()) == 1


def test_batch_entry_to_dict_keys():
    result = batch(["* * * * * echo"])
    d = result.entries[0].to_dict()
    assert "index" in d
    assert "expression" in d
    assert "valid" in d
    assert "error_count" in d
    assert "warning_count" in d


def test_format_batch_result_returns_string():
    result = batch(["* * * * * echo"])
    output = format_batch_result(result)
    assert isinstance(output, str)


def test_format_batch_result_contains_expression():
    expr = "0 12 * * * echo noon"
    result = batch([expr])
    output = format_batch_result(result)
    assert expr in output


def test_format_batch_result_shows_ok_for_valid():
    result = batch(["* * * * * echo"])
    output = format_batch_result(result)
    assert "OK" in output


def test_format_batch_result_shows_fail_for_invalid():
    result = batch(["bad"])
    output = format_batch_result(result)
    assert "FAIL" in output
