"""Tests for crontab_lint.labeler."""

import pytest
from crontab_lint.labeler import LabelResult, label, format_label_result


def test_label_returns_label_result():
    result = label("* * * * * /bin/true")
    assert isinstance(result, LabelResult)


def test_label_valid_expression_is_valid():
    result = label("0 * * * * /bin/true")
    assert result.is_valid is True
    assert result.error is None


def test_label_invalid_expression_is_not_valid():
    result = label("not a cron")
    assert result.is_valid is False
    assert result.label == "invalid"


def test_label_invalid_has_error():
    result = label("60 * * * * /cmd")
    assert result.error is not None
    assert len(result.error) > 0


def test_label_every_minute():
    result = label("* * * * * /cmd")
    assert result.label == "every-minute"


def test_label_hourly():
    result = label("0 * * * * /cmd")
    assert result.label == "hourly"


def test_label_daily_midnight():
    result = label("0 0 * * * /cmd")
    assert result.label == "daily"
    assert result.sublabel is not None
    assert "midnight" in result.sublabel


def test_label_daily_specific_hour():
    result = label("0 6 * * * /cmd")
    assert result.label == "daily"
    assert "6" in result.sublabel


def test_label_weekly():
    result = label("0 0 * * 1 /cmd")
    assert result.label == "weekly"
    assert result.sublabel is not None


def test_label_monthly():
    result = label("0 0 1 * * /cmd")
    assert result.label == "monthly"
    assert "1" in result.sublabel


def test_label_yearly():
    result = label("0 0 1 1 * /cmd")
    assert result.label == "yearly"


def test_label_frequent_step():
    result = label("*/5 * * * * /cmd")
    assert result.label == "frequent"
    assert "5" in result.sublabel


def test_label_expression_preserved():
    expr = "30 12 * * * /cmd"
    result = label(expr)
    assert result.expression == expr


def test_format_label_result_valid():
    result = label("0 * * * * /cmd")
    output = format_label_result(result)
    assert "hourly" in output
    assert "0 * * * *" in output or "0 * * * * /cmd" in output


def test_format_label_result_includes_sublabel():
    result = label("0 0 * * * /cmd")
    output = format_label_result(result)
    assert "midnight" in output or "daily" in output


def test_format_label_result_invalid_shows_error():
    result = label("bad expression")
    output = format_label_result(result)
    assert "invalid" in output


def test_label_sub_hourly():
    result = label("15 * * * * /cmd")
    assert result.label == "sub-hourly"
    assert "15" in result.sublabel
