"""Tests for crontab_lint.mapper."""
import pytest

from crontab_lint.mapper import MapEntry, MapResult, format_map_result, map_expression


def test_map_expression_returns_map_result():
    result = map_expression("* * * * * /bin/true")
    assert isinstance(result, MapResult)


def test_map_valid_expression_is_valid():
    result = map_expression("0 * * * * /bin/true")
    assert result.is_valid is True


def test_map_invalid_expression_is_not_valid():
    result = map_expression("not a cron")
    assert result.is_valid is False


def test_map_invalid_has_error():
    result = map_expression("not a cron")
    assert result.error is not None
    assert len(result.error) > 0


def test_map_invalid_has_no_entries():
    result = map_expression("not a cron")
    assert result.entries == []


def test_map_every_minute_has_1440_entries():
    result = map_expression("* * * * * /bin/true")
    assert result.total() == 1440


def test_map_hourly_has_24_entries():
    result = map_expression("0 * * * * /bin/true")
    assert result.total() == 24


def test_map_daily_midnight_has_1_entry():
    result = map_expression("0 0 * * * /bin/true")
    assert result.total() == 1


def test_map_daily_midnight_entry_values():
    result = map_expression("0 0 * * * /bin/true")
    assert result.entries[0].hour == 0
    assert result.entries[0].minute == 0


def test_map_specific_time_entry():
    result = map_expression("30 14 * * * /bin/true")
    assert result.total() == 1
    assert result.entries[0].hour == 14
    assert result.entries[0].minute == 30


def test_map_every_five_minutes_has_288_entries():
    result = map_expression("*/5 * * * * /bin/true")
    assert result.total() == 288


def test_map_hours_covered_wildcard():
    result = map_expression("0 * * * * /bin/true")
    assert result.hours_covered() == list(range(24))


def test_map_hours_covered_specific_hour():
    result = map_expression("0 9 * * * /bin/true")
    assert result.hours_covered() == [9]


def test_map_entry_str_format():
    entry = MapEntry(hour=9, minute=5)
    assert str(entry) == "09:05"


def test_map_entry_to_dict():
    entry = MapEntry(hour=14, minute=30)
    d = entry.to_dict()
    assert d["hour"] == 14
    assert d["minute"] == 30


def test_map_to_dict_valid():
    result = map_expression("0 0 * * * /bin/true")
    d = result.to_dict()
    assert d["is_valid"] is True
    assert d["total"] == 1
    assert len(d["entries"]) == 1


def test_format_map_result_valid():
    result = map_expression("0 0 * * * /bin/true")
    output = format_map_result(result)
    assert "0 0 * * *" in output
    assert "1 per day" in output


def test_format_map_result_invalid():
    result = map_expression("bad expr")
    output = format_map_result(result)
    assert "Error" in output


def test_format_map_result_shows_sample_times():
    result = map_expression("0 * * * * /bin/true")
    output = format_map_result(result)
    assert ":00" in output
