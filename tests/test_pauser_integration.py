"""Integration tests for the pauser module."""

import pytest
from crontab_lint.pauser import pause

STANDARD = [
    ("* * * * *",   0,  "every minute fires every hour"),
    ("0 * * * *",   0,  "hourly fires every hour"),
    ("0 0 * * *",  23,  "daily midnight has 23h pause"),
    ("0 6 * * *",  23,  "daily 6am has 23h pause"),
    ("0 0,12 * * *", 12, "twice daily has 12h pause"),
    ("0 8-17 * * *", 14, "business hours has 14h pause"),
]


@pytest.mark.parametrize("expr,expected_longest,_desc", STANDARD)
def test_longest_pause(expr, expected_longest, _desc):
    result = pause(expr)
    assert result.is_valid
    assert result.longest_pause_hours == expected_longest


def test_every_minute_has_no_quiet_windows():
    result = pause("* * * * *")
    assert result.quiet_windows == []


def test_hourly_has_no_quiet_windows():
    result = pause("0 * * * *")
    assert result.quiet_windows == []


def test_business_hours_window_count():
    # 08:00-17:00 → active 8..17 (10 hours), quiet 0-8 and 18-24
    result = pause("0 8-17 * * *")
    assert len(result.quiet_windows) == 2


def test_quiet_window_durations_sum_to_inactive_hours():
    result = pause("0 0,6,12,18 * * *")
    total_quiet = sum(w.duration_hours for w in result.quiet_windows)
    assert total_quiet == 20  # 24 hours minus 4 active hours


def test_to_dict_roundtrip():
    result = pause("0 9 * * *")
    d = result.to_dict()
    assert d["expression"] == "0 9 * * *"
    assert d["is_valid"] is True
    assert isinstance(d["quiet_windows"], list)
    assert all("start_hour" in w for w in d["quiet_windows"])
