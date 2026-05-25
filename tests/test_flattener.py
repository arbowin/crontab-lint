"""Tests for crontab_lint.flattener."""

import pytest
from crontab_lint.flattener import flatten, format_flatten_result, FlattenResult


def test_flatten_returns_flatten_result():
    result = flatten("0 * * * * echo hi")
    assert isinstance(result, FlattenResult)


def test_flatten_valid_expression_is_valid():
    result = flatten("0 * * * * echo hi")
    assert result.is_valid


def test_flatten_invalid_expression_is_not_valid():
    result = flatten("bad expression")
    assert not result.is_valid


def test_flatten_invalid_has_error_message():
    result = flatten("bad expression")
    assert result.error != ""


def test_flatten_invalid_has_no_pairs():
    result = flatten("bad expression")
    assert result.pairs == []


def test_flatten_top_of_every_hour_gives_24_pairs():
    result = flatten("0 * * * * echo")
    assert len(result.pairs) == 24


def test_flatten_every_minute_gives_1440_pairs():
    result = flatten("* * * * * echo")
    assert len(result.pairs) == 1440


def test_flatten_midnight_gives_one_pair():
    result = flatten("0 0 * * * echo")
    assert result.pairs == [(0, 0)]


def test_flatten_specific_minute_and_hour():
    result = flatten("30 14 * * * echo")
    assert result.pairs == [(30, 14)]


def test_flatten_step_minutes():
    result = flatten("*/15 * * * * echo")
    assert len(result.pairs) == 4 * 24


def test_flatten_step_hours():
    result = flatten("0 */6 * * * echo")
    assert len(result.pairs) == 4
    hours = [h for _, h in result.pairs]
    assert hours == [0, 6, 12, 18]


def test_flatten_range_minutes():
    result = flatten("0-4 0 * * * echo")
    assert len(result.pairs) == 5
    assert result.pairs[0] == (0, 0)
    assert result.pairs[-1] == (4, 0)


def test_flatten_list_hours():
    result = flatten("0 8,12,18 * * * echo")
    assert len(result.pairs) == 3
    hours = [h for _, h in result.pairs]
    assert hours == [8, 12, 18]


def test_flatten_pairs_are_sorted_by_hour_then_minute():
    result = flatten("0,30 8,9 * * * echo")
    expected = [(0, 8), (30, 8), (0, 9), (30, 9)]
    assert result.pairs == expected


def test_format_flatten_result_valid():
    result = flatten("0 0 * * * echo")
    output = format_flatten_result(result)
    assert "Expression" in output
    assert "00:00" in output


def test_format_flatten_result_invalid():
    result = flatten("not a cron")
    output = format_flatten_result(result)
    assert "Error" in output


def test_format_flatten_result_limit_respected():
    result = flatten("* * * * * echo")
    output = format_flatten_result(result, limit=5)
    assert "more" in output


def test_format_flatten_result_total_shown():
    result = flatten("0 * * * * echo")
    output = format_flatten_result(result)
    assert "24" in output
