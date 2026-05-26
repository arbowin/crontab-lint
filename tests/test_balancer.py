"""Tests for crontab_lint.balancer."""
import pytest
from crontab_lint.balancer import balance, format_balance_result, BalanceResult


def test_balance_returns_balance_result():
    result = balance(["* * * * * echo hi"])
    assert isinstance(result, BalanceResult)


def test_balance_empty_list_is_not_valid():
    result = balance([])
    assert result.is_valid is False


def test_balance_empty_list_has_error():
    result = balance([])
    assert result.error != ""


def test_balance_invalid_expression_is_not_valid():
    result = balance(["not a cron"])
    assert result.is_valid is False


def test_balance_invalid_expression_has_error():
    result = balance(["not a cron"])
    assert "Invalid" in result.error


def test_balance_every_minute_is_valid():
    result = balance(["* * * * * echo"])
    assert result.is_valid is True


def test_balance_every_minute_all_hours_equal():
    result = balance(["* * * * * echo"])
    loads = list(result.hourly_load.values())
    assert len(set(loads)) == 1


def test_balance_every_minute_peak_load_is_60():
    result = balance(["* * * * * echo"])
    assert result.peak_load == 60


def test_balance_every_minute_verdict_balanced():
    result = balance(["* * * * * echo"])
    assert result.verdict == "balanced"


def test_balance_hourly_verdict_balanced():
    result = balance(["0 * * * * echo"])
    assert result.verdict == "balanced"


def test_balance_hourly_load_is_one_per_hour():
    result = balance(["0 * * * * echo"])
    for h in range(24):
        assert result.hourly_load[h] == 1


def test_balance_specific_hour_only_loads_that_hour():
    result = balance(["0 3 * * * echo"])
    assert result.hourly_load[3] == 1
    for h in range(24):
        if h != 3:
            assert result.hourly_load[h] == 0


def test_balance_specific_hour_peak_is_that_hour():
    result = balance(["0 3 * * * echo"])
    assert result.peak_hour == 3


def test_balance_specific_hour_min_load_is_zero():
    result = balance(["0 3 * * * echo"])
    assert result.min_load == 0


def test_balance_specific_hour_ratio_is_zero():
    # min_load == 0, so ratio is 0.0
    result = balance(["0 3 * * * echo"])
    assert result.imbalance_ratio == 0.0


def test_balance_two_valid_expressions_accumulate():
    result = balance(["0 * * * * echo", "0 * * * * echo"])
    for h in range(24):
        assert result.hourly_load[h] == 2


def test_balance_hourly_load_has_24_entries():
    result = balance(["* * * * * echo"])
    assert len(result.hourly_load) == 24


def test_format_balance_result_valid_contains_verdict():
    result = balance(["* * * * * echo"])
    output = format_balance_result(result)
    assert "balanced" in output


def test_format_balance_result_invalid_contains_error():
    result = balance([])
    output = format_balance_result(result)
    assert "ERROR" in output


def test_format_balance_result_shows_peak_hour():
    result = balance(["0 * * * * echo"])
    output = format_balance_result(result)
    assert "Peak hour" in output
