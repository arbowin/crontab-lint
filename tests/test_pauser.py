"""Tests for crontab_lint.pauser."""

import pytest
from crontab_lint.pauser import pause, format_pause_result, PauseResult, QuietWindow


def test_pause_returns_pause_result():
    result = pause("0 9 * * *")
    assert isinstance(result, PauseResult)


def test_pause_valid_expression_is_valid():
    result = pause("0 9 * * *")
    assert result.is_valid is True
    assert result.error is None


def test_pause_invalid_expression_is_not_valid():
    result = pause("not a cron")
    assert result.is_valid is False


def test_pause_invalid_has_error():
    result = pause("not a cron")
    assert result.error is not None
    assert len(result.error) > 0


def test_pause_invalid_has_no_windows():
    result = pause("not a cron")
    assert result.quiet_windows == []
    assert result.longest_pause_hours == 0


def test_pause_every_minute_no_quiet_windows():
    result = pause("* * * * *")
    assert result.is_valid is True
    assert result.quiet_windows == []
    assert result.longest_pause_hours == 0


def test_pause_daily_midnight_has_quiet_windows():
    result = pause("0 0 * * *")
    assert result.is_valid is True
    assert len(result.quiet_windows) > 0


def test_pause_daily_midnight_longest_pause_is_23():
    result = pause("0 0 * * *")
    assert result.longest_pause_hours == 23


def test_pause_twice_daily_has_two_windows():
    # runs at 00:00 and 12:00 only
    result = pause("0 0,12 * * *")
    assert result.is_valid is True
    assert len(result.quiet_windows) == 2


def test_pause_twice_daily_longest_pause_is_12():
    result = pause("0 0,12 * * *")
    assert result.longest_pause_hours == 12


def test_pause_quiet_window_fields():
    result = pause("0 0 * * *")
    w = result.quiet_windows[0]
    assert isinstance(w, QuietWindow)
    assert w.start_hour >= 0
    assert w.end_hour <= 24
    assert w.duration_hours == w.end_hour - w.start_hour


def test_pause_to_dict_valid():
    result = pause("0 9 * * *")
    d = result.to_dict()
    assert d["is_valid"] is True
    assert "quiet_windows" in d
    assert "longest_pause_hours" in d


def test_pause_to_dict_invalid():
    result = pause("bad expr")
    d = result.to_dict()
    assert d["is_valid"] is False
    assert d["error"] is not None


def test_format_pause_result_valid():
    result = pause("0 0 * * *")
    text = format_pause_result(result)
    assert "0 0 * * *" in text
    assert "Longest pause" in text


def test_format_pause_result_invalid():
    result = pause("bad")
    text = format_pause_result(result)
    assert "Error" in text


def test_format_pause_result_no_windows():
    result = pause("* * * * *")
    text = format_pause_result(result)
    assert "none" in text
