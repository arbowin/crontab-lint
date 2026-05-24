"""Tests for crontab_lint.tagger."""

import pytest
from crontab_lint.tagger import tag, format_tag_result, TagResult


def test_tag_returns_tag_result():
    result = tag("0 0 * * *")
    assert isinstance(result, TagResult)


def test_tag_invalid_expression_is_not_valid():
    result = tag("not a cron")
    assert result.is_valid is False
    assert result.tags == []


def test_tag_every_minute():
    result = tag("* * * * *")
    assert result.is_valid is True
    assert result.has_tag("every-minute")
    assert result.has_tag("frequent")


def test_tag_hourly():
    result = tag("0 * * * * /bin/task")
    assert result.is_valid is True
    assert result.has_tag("hourly")


def test_tag_daily_midnight():
    result = tag("0 0 * * * /bin/task")
    assert result.is_valid is True
    assert result.has_tag("daily")
    assert result.has_tag("midnight")


def test_tag_weekly():
    result = tag("0 0 * * 1 /bin/task")
    assert result.is_valid is True
    assert result.has_tag("weekly")


def test_tag_monthly():
    result = tag("0 0 1 * * /bin/task")
    assert result.is_valid is True
    assert result.has_tag("monthly")


def test_tag_yearly():
    result = tag("0 0 1 1 * /bin/task")
    assert result.is_valid is True
    assert result.has_tag("yearly")


def test_tag_weekdays():
    result = tag("0 9 * * 1-5 /bin/task")
    assert result.is_valid is True
    assert result.has_tag("weekdays")


def test_tag_interval():
    result = tag("*/15 * * * * /bin/task")
    assert result.is_valid is True
    assert result.has_tag("interval")


def test_tag_no_matching_tags():
    result = tag("30 14 * * * /bin/task")
    assert result.is_valid is True
    assert result.tags == []


def test_has_tag_false_for_missing():
    result = tag("30 14 * * * /bin/task")
    assert result.has_tag("daily") is False


def test_format_tag_result_valid_with_tags():
    result = tag("0 0 * * * /bin/task")
    output = format_tag_result(result)
    assert "daily" in output
    assert "midnight" in output


def test_format_tag_result_no_tags():
    result = tag("30 14 * * * /bin/task")
    output = format_tag_result(result)
    assert "no tags" in output


def test_format_tag_result_invalid():
    result = tag("bad input")
    output = format_tag_result(result)
    assert "invalid" in output
