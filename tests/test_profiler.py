"""Tests for crontab_lint.profiler."""

import pytest
from crontab_lint.profiler import profile, ProfileResult


def test_profile_returns_profile_result():
    result = profile("0 * * * * /cmd")
    assert isinstance(result, ProfileResult)


def test_profile_valid_expression_is_valid():
    result = profile("0 * * * * /cmd")
    assert result.is_valid is True


def test_profile_invalid_expression_is_not_valid():
    result = profile("not_a_cron")
    assert result.is_valid is False


def test_profile_invalid_has_warnings():
    result = profile("bad expr")
    assert len(result.warnings) > 0


def test_profile_every_minute_runs_per_day():
    result = profile("* * * * * /cmd")
    assert result.runs_per_day == pytest.approx(1440.0, rel=0.01)


def test_profile_every_minute_label():
    result = profile("* * * * * /cmd")
    assert result.frequency_label == "every-minute"


def test_profile_top_of_every_hour_runs_per_day():
    result = profile("0 * * * * /cmd")
    assert result.runs_per_day == pytest.approx(24.0, rel=0.01)


def test_profile_top_of_every_hour_label():
    result = profile("0 * * * * /cmd")
    assert result.frequency_label == "frequent"


def test_profile_daily_runs_per_day():
    result = profile("0 6 * * * /cmd")
    assert result.runs_per_day == pytest.approx(1.0, rel=0.01)


def test_profile_daily_label():
    result = profile("0 6 * * * /cmd")
    assert result.frequency_label == "daily"


def test_profile_step_minutes_runs_per_hour():
    result = profile("*/15 * * * * /cmd")
    assert result.runs_per_day == pytest.approx(96.0, rel=0.01)


def test_profile_step_hours_runs_per_day():
    result = profile("0 */6 * * * /cmd")
    assert result.runs_per_day == pytest.approx(4.0, rel=0.01)


def test_profile_comma_minutes():
    result = profile("0,30 * * * * /cmd")
    assert result.runs_per_day == pytest.approx(48.0, rel=0.01)


def test_profile_comma_hours():
    result = profile("0 6,12,18 * * * /cmd")
    assert result.runs_per_day == pytest.approx(3.0, rel=0.01)


def test_profile_very_frequent_has_warning():
    result = profile("* * * * * /cmd")
    assert any("frequently" in w for w in result.warnings)


def test_profile_runs_per_week_is_seven_times_per_day():
    result = profile("0 6 * * * /cmd")
    assert result.runs_per_week == pytest.approx(result.runs_per_day * 7, rel=0.01)


def test_profile_expression_preserved():
    expr = "30 8 * * 1 /backup"
    result = profile(expr)
    assert result.expression == expr
