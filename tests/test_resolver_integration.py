"""Integration tests for resolver: verify run times are chronologically correct."""

from datetime import datetime, timedelta

import pytest

from crontab_lint.resolver import resolve

FIXED = datetime(2024, 3, 1, 0, 0, 0)  # Friday midnight


def test_runs_are_in_ascending_order():
    result = resolve("*/5 * * * * echo hi", count=10, after=FIXED)
    assert result.is_valid
    parsed = [datetime.strptime(r, "%Y-%m-%d %H:%M") for r in result.runs]
    assert parsed == sorted(parsed)


def test_every_minute_consecutive_runs_one_minute_apart():
    result = resolve("* * * * * echo hi", count=5, after=FIXED)
    parsed = [datetime.strptime(r, "%Y-%m-%d %H:%M") for r in result.runs]
    for a, b in zip(parsed, parsed[1:]):
        assert b - a == timedelta(minutes=1)


def test_hourly_runs_one_hour_apart():
    result = resolve("0 * * * * echo hi", count=4, after=FIXED)
    parsed = [datetime.strptime(r, "%Y-%m-%d %H:%M") for r in result.runs]
    for a, b in zip(parsed, parsed[1:]):
        assert b - a == timedelta(hours=1)


def test_daily_midnight_runs_one_day_apart():
    result = resolve("0 0 * * * echo hi", count=3, after=FIXED)
    parsed = [datetime.strptime(r, "%Y-%m-%d %H:%M") for r in result.runs]
    for a, b in zip(parsed, parsed[1:]):
        assert b - a == timedelta(days=1)


def test_weekday_only_runs_on_correct_days():
    # 0 9 * * 1 = every Monday at 09:00; FIXED is Friday 2024-03-01
    result = resolve("0 9 * * 1 echo hi", count=3, after=FIXED)
    parsed = [datetime.strptime(r, "%Y-%m-%d %H:%M") for r in result.runs]
    for dt in parsed:
        assert dt.weekday() == 0  # Monday
        assert dt.hour == 9


def test_all_runs_are_after_the_anchor():
    result = resolve("*/15 * * * * echo hi", count=8, after=FIXED)
    parsed = [datetime.strptime(r, "%Y-%m-%d %H:%M") for r in result.runs]
    for dt in parsed:
        assert dt > FIXED
