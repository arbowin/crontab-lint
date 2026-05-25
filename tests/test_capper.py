"""Tests for crontab_lint.capper."""
import pytest

from crontab_lint.capper import CapResult, cap, format_cap_result


def test_cap_returns_cap_result():
    result = cap("* * * * *")
    assert isinstance(result, CapResult)


def test_cap_valid_expression_is_valid():
    result = cap("0 * * * *")
    assert result.is_valid is True
    assert result.error is None


def test_cap_invalid_expression_is_not_valid():
    result = cap("not a cron")
    assert result.is_valid is False
    assert result.error is not None


def test_cap_invalid_has_no_runs():
    result = cap("not a cron")
    assert result.runs_per_day == 0


def test_cap_every_minute_exceeds_default_cap():
    # default cap is 96; every-minute = 1440 runs/day
    result = cap("* * * * *")
    assert result.exceeds_cap is True


def test_cap_hourly_within_default_cap():
    # 24 runs/day < 96
    result = cap("0 * * * *")
    assert result.exceeds_cap is False


def test_cap_daily_within_default_cap():
    result = cap("0 0 * * *")
    assert result.exceeds_cap is False


def test_cap_stores_cap_value():
    result = cap("* * * * *", max_runs_per_day=200)
    assert result.cap == 200


def test_cap_custom_low_cap_hourly_exceeds():
    # hourly = 24 runs/day; cap = 10 => exceeds
    result = cap("0 * * * *", max_runs_per_day=10)
    assert result.exceeds_cap is True


def test_cap_exceeds_has_suggestion():
    result = cap("* * * * *")
    assert result.suggested is not None
    assert "*" in result.suggested


def test_cap_within_cap_has_no_suggestion():
    result = cap("0 0 * * *")
    assert result.suggested is None


def test_cap_runs_per_day_every_minute():
    result = cap("* * * * *")
    assert result.runs_per_day == 1440


def test_cap_runs_per_day_hourly():
    result = cap("0 * * * *")
    assert result.runs_per_day == 24


def test_cap_to_dict_keys():
    result = cap("0 * * * *")
    d = result.to_dict()
    for key in ("expression", "is_valid", "error", "runs_per_day", "cap", "exceeds_cap", "suggested"):
        assert key in d


def test_format_cap_result_valid():
    result = cap("0 * * * *")
    text = format_cap_result(result)
    assert "0 * * * *" in text
    assert "Runs/day" in text
    assert "within cap" in text


def test_format_cap_result_exceeds_shows_label():
    result = cap("* * * * *")
    text = format_cap_result(result)
    assert "EXCEEDS CAP" in text


def test_format_cap_result_exceeds_shows_suggestion():
    result = cap("* * * * *")
    text = format_cap_result(result)
    assert "Suggested" in text


def test_format_cap_result_invalid_shows_error():
    result = cap("bad expression")
    text = format_cap_result(result)
    assert "Error" in text
