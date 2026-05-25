"""Tests for crontab_lint.streaker."""
import pytest
from crontab_lint.streaker import streak, format_streak_result, _max_consecutive, _expand_field


# --- unit helpers -----------------------------------------------------------

def test_max_consecutive_empty():
    assert _max_consecutive([], 24) == 0


def test_max_consecutive_single():
    assert _max_consecutive([5], 24) == 1


def test_max_consecutive_all_consecutive():
    assert _max_consecutive([0, 1, 2, 3], 24) == 4


def test_max_consecutive_gap():
    assert _max_consecutive([0, 1, 5, 6, 7], 24) == 3


def test_max_consecutive_wrap_around():
    # hours 22, 23, 0, 1 are consecutive mod 24
    assert _max_consecutive([0, 1, 22, 23], 24) == 4


def test_expand_field_wildcard():
    assert _expand_field("*", 0, 5) == [0, 1, 2, 3, 4, 5]


def test_expand_field_single():
    assert _expand_field("3", 0, 23) == [3]


def test_expand_field_range():
    assert _expand_field("2-4", 0, 23) == [2, 3, 4]


def test_expand_field_step():
    assert _expand_field("*/6", 0, 23) == [0, 6, 12, 18]


def test_expand_field_list():
    assert _expand_field("1,3,5", 0, 23) == [1, 3, 5]


# --- streak() ---------------------------------------------------------------

def test_streak_returns_streak_result():
    from crontab_lint.streaker import StreakResult
    r = streak("* * * * * /bin/true")
    assert isinstance(r, StreakResult)


def test_streak_valid_expression_is_valid():
    r = streak("0 * * * * /bin/true")
    assert r.is_valid is True
    assert r.error == ""


def test_streak_invalid_expression_is_not_valid():
    r = streak("not a cron")
    assert r.is_valid is False
    assert r.error != ""


def test_streak_every_minute_all_hours_active():
    r = streak("* * * * * /bin/true")
    assert r.active_hours == list(range(24))
    assert r.max_hour_streak == 24


def test_streak_every_minute_all_days_active():
    r = streak("* * * * * /bin/true")
    assert r.active_days == list(range(7))
    assert r.max_day_streak == 7


def test_streak_specific_hour():
    r = streak("0 9 * * * /bin/true")
    assert r.active_hours == [9]
    assert r.max_hour_streak == 1


def test_streak_hour_range():
    r = streak("0 9-17 * * * /bin/true")
    assert r.active_hours == list(range(9, 18))
    assert r.max_hour_streak == 9


def test_streak_weekday_only():
    r = streak("0 9 * * 1-5 /bin/true")
    assert r.active_days == [1, 2, 3, 4, 5]
    assert r.max_day_streak == 5


def test_streak_weekend_only():
    r = streak("0 9 * * 0,6 /bin/true")
    assert r.active_days == [0, 6]
    # 0 and 6 are adjacent mod 7
    assert r.max_day_streak == 2


def test_streak_invalid_has_empty_lists():
    r = streak("99 99 * * * /bin/true")
    assert r.active_hours == []
    assert r.active_days == []
    assert r.max_hour_streak == 0
    assert r.max_day_streak == 0


# --- format_streak_result() -------------------------------------------------

def test_format_streak_result_valid_contains_expression():
    r = streak("0 * * * * /bin/true")
    out = format_streak_result(r)
    assert "0 * * * * /bin/true" in out


def test_format_streak_result_valid_contains_streak_info():
    r = streak("0 * * * * /bin/true")
    out = format_streak_result(r)
    assert "streak" in out


def test_format_streak_result_invalid_shows_error():
    r = streak("bad expression")
    out = format_streak_result(r)
    assert "ERROR" in out
