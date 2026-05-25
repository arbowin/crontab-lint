"""Tests for crontab_lint.expander."""

import pytest
from crontab_lint.expander import expand, format_expand_result, ExpandResult


def test_expand_returns_expand_result():
    result = expand("0 * * * * /cmd")
    assert isinstance(result, ExpandResult)


def test_expand_valid_expression_is_valid():
    result = expand("0 * * * * /cmd")
    assert result.is_valid is True


def test_expand_invalid_expression_is_not_valid():
    result = expand("bad expression")
    assert result.is_valid is False


def test_expand_invalid_has_error():
    result = expand("bad expression")
    assert result.error is not None
    assert len(result.error) > 0


def test_expand_invalid_has_no_pairs():
    result = expand("bad expression")
    assert result.pairs == []


def test_expand_top_of_every_hour_has_24_pairs():
    # 0 * * * * fires at minute 0 of each of 24 hours
    result = expand("0 * * * * /cmd")
    assert result.is_valid
    assert len(result.pairs) == 24


def test_expand_top_of_every_hour_all_minute_zero():
    result = expand("0 * * * * /cmd")
    assert all(m == 0 for m, h in result.pairs)


def test_expand_every_minute_has_1440_pairs():
    result = expand("* * * * * /cmd")
    assert result.is_valid
    assert len(result.pairs) == 1440


def test_expand_midnight_only_has_one_pair():
    result = expand("0 0 * * * /cmd")
    assert result.is_valid
    assert result.pairs == [(0, 0)]


def test_expand_step_minutes_correct_count():
    # */15 * means minutes 0,15,30,45 across 24 hours => 96 pairs
    result = expand("*/15 * * * * /cmd")
    assert result.is_valid
    assert len(result.pairs) == 96


def test_expand_specific_hours_correct_count():
    # 0 9,17 means minute 0 at hour 9 and 17 => 2 pairs
    result = expand("0 9,17 * * * /cmd")
    assert result.is_valid
    assert len(result.pairs) == 2
    assert (0, 9) in result.pairs
    assert (0, 17) in result.pairs


def test_expand_range_hours():
    # 0 8-10 means minute 0 at hours 8,9,10 => 3 pairs
    result = expand("0 8-10 * * * /cmd")
    assert result.is_valid
    assert len(result.pairs) == 3


def test_expand_expression_preserved():
    expr = "30 6 * * * /cmd"
    result = expand(expr)
    assert result.expression == expr


def test_format_expand_result_valid():
    result = expand("0 0 * * * /cmd")
    output = format_expand_result(result)
    assert "00:00" in output
    assert "Total" in output


def test_format_expand_result_invalid():
    result = expand("not valid")
    output = format_expand_result(result)
    assert "ERROR" in output


def test_format_expand_result_limit():
    result = expand("* * * * * /cmd")
    output = format_expand_result(result, limit=5)
    assert "more" in output
