"""Tests for crontab_lint.schedule."""

from datetime import datetime

import pytest

from crontab_lint.schedule import next_runs, _matches_field


# ---------------------------------------------------------------------------
# Unit tests for _matches_field
# ---------------------------------------------------------------------------

def test_matches_wildcard():
    assert _matches_field(30, "*", 0, 59) is True


def test_matches_exact():
    assert _matches_field(5, "5", 0, 59) is True
    assert _matches_field(6, "5", 0, 59) is False


def test_matches_range():
    assert _matches_field(3, "1-5", 0, 59) is True
    assert _matches_field(6, "1-5", 0, 59) is False


def test_matches_step():
    assert _matches_field(0, "*/15", 0, 59) is True
    assert _matches_field(15, "*/15", 0, 59) is True
    assert _matches_field(30, "*/15", 0, 59) is True
    assert _matches_field(7, "*/15", 0, 59) is False


def test_matches_list():
    assert _matches_field(1, "1,3,5", 0, 59) is True
    assert _matches_field(3, "1,3,5", 0, 59) is True
    assert _matches_field(2, "1,3,5", 0, 59) is False


def test_matches_range_step():
    # 10-40/10 => 10, 20, 30, 40
    assert _matches_field(10, "10-40/10", 0, 59) is True
    assert _matches_field(20, "10-40/10", 0, 59) is True
    assert _matches_field(15, "10-40/10", 0, 59) is False


# ---------------------------------------------------------------------------
# Integration tests for next_runs
# ---------------------------------------------------------------------------

ANCHOR = datetime(2024, 1, 1, 0, 0, 0)  # Monday midnight


def test_next_runs_returns_correct_count():
    runs = next_runs("* * * * *", after=ANCHOR)
    assert len(runs) == 5


def test_next_runs_every_minute_are_consecutive():
    runs = next_runs("* * * * *", after=ANCHOR, count=3)
    assert runs[1] - runs[0].replace() == runs[2] - runs[1]


def test_next_runs_top_of_hour():
    runs = next_runs("0 * * * *", after=ANCHOR, count=3)
    for dt in runs:
        assert dt.minute == 0


def test_next_runs_specific_time():
    # Every day at 09:30
    runs = next_runs("30 9 * * *", after=ANCHOR, count=3)
    for dt in runs:
        assert dt.hour == 9
        assert dt.minute == 30


def test_next_runs_step_minutes():
    runs = next_runs("*/15 * * * *", after=ANCHOR, count=4)
    for dt in runs:
        assert dt.minute % 15 == 0


def test_next_runs_after_is_exclusive():
    anchor = datetime(2024, 6, 15, 12, 0, 0)
    runs = next_runs("0 12 * * *", after=anchor, count=1)
    # Next match should be the following day, not the same minute.
    assert runs[0] > anchor
    assert runs[0].day == 16


def test_next_runs_default_after_does_not_raise():
    runs = next_runs("0 0 * * *", count=2)
    assert len(runs) == 2
