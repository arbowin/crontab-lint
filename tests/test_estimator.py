"""Tests for crontab_lint.estimator."""

import pytest
from crontab_lint.estimator import estimate, format_estimate_result, EstimateResult


def test_estimate_returns_estimate_result():
    result = estimate("* * * * * /bin/true")
    assert isinstance(result, EstimateResult)


def test_estimate_valid_expression_is_valid():
    result = estimate("* * * * * /bin/true")
    assert result.is_valid is True


def test_estimate_invalid_expression_is_not_valid():
    result = estimate("bad")
    assert result.is_valid is False


def test_estimate_invalid_has_error():
    result = estimate("bad")
    assert result.error is not None
    assert len(result.error) > 0


def test_estimate_invalid_has_no_interval():
    result = estimate("bad")
    assert result.interval_seconds is None
    assert result.interval_human is None
    assert result.runs_per_day is None


def test_estimate_every_minute_interval_is_60():
    result = estimate("* * * * * /bin/true")
    assert result.interval_seconds == 60


def test_estimate_every_minute_runs_per_day_is_1440():
    result = estimate("* * * * * /bin/true")
    assert result.runs_per_day == 1440


def test_estimate_hourly_interval_is_3600():
    result = estimate("0 * * * * /bin/true")
    assert result.interval_seconds == 3600


def test_estimate_hourly_runs_per_day_is_24():
    result = estimate("0 * * * * /bin/true")
    assert result.runs_per_day == 24


def test_estimate_every_five_minutes_interval_is_300():
    result = estimate("*/5 * * * * /bin/true")
    assert result.interval_seconds == 300


def test_estimate_expression_preserved():
    expr = "*/10 * * * * /bin/true"
    result = estimate(expr)
    assert result.expression == expr


def test_human_interval_minutes():
    result = estimate("*/5 * * * * /bin/true")
    assert "minute" in result.interval_human


def test_human_interval_hours():
    result = estimate("0 * * * * /bin/true")
    assert "hour" in result.interval_human


def test_format_estimate_result_valid():
    result = estimate("* * * * * /bin/true")
    output = format_estimate_result(result)
    assert "Expression" in output
    assert "Interval" in output
    assert "Runs/day" in output


def test_format_estimate_result_invalid():
    result = estimate("bad")
    output = format_estimate_result(result)
    assert "Error" in output
    assert "Interval" not in output
