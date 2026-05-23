"""Tests for crontab_lint.normalizer."""

import pytest
from crontab_lint.normalizer import normalize, NormalizeResult, _normalize_field


def test_normalize_simple_expression():
    result = normalize("0 * * * * /usr/bin/backup")
    assert result.ok
    assert result.normalized == "0 * * * * /usr/bin/backup"
    assert result.was_shorthand is False


def test_normalize_strips_leading_zeros():
    result = normalize("05 08 * * * /bin/run")
    assert result.ok
    assert result.normalized == "5 8 * * * /bin/run"


def test_normalize_shorthand_daily():
    result = normalize("@daily /bin/cleanup")
    assert result.ok
    assert result.normalized == "0 0 * * * /bin/cleanup"
    assert result.was_shorthand is True


def test_normalize_shorthand_hourly():
    result = normalize("@hourly")
    assert result.ok
    assert result.normalized == "0 * * * *"
    assert result.was_shorthand is True


def test_normalize_shorthand_yearly():
    result = normalize("@yearly /bin/report")
    assert result.ok
    assert result.normalized == "0 0 1 1 * /bin/report"
    assert result.was_shorthand is True


def test_normalize_shorthand_annually_same_as_yearly():
    r1 = normalize("@yearly")
    r2 = normalize("@annually")
    assert r1.normalized == r2.normalized


def test_normalize_shorthand_midnight_same_as_daily():
    r1 = normalize("@midnight")
    r2 = normalize("@daily")
    assert r1.normalized == r2.normalized


def test_normalize_range_field():
    result = normalize("0 09-17 * * 1-5 /bin/workday")
    assert result.ok
    assert result.normalized == "0 9-17 * * 1-5 /bin/workday"


def test_normalize_step_field():
    result = normalize("*/05 * * * * /bin/frequent")
    assert result.ok
    assert result.normalized == "*/5 * * * * /bin/frequent"


def test_normalize_list_field():
    result = normalize("0 08,12,18 * * * /bin/meals")
    assert result.ok
    assert result.normalized == "0 8,12,18 * * * /bin/meals"


def test_normalize_invalid_expression_returns_error():
    result = normalize("not a cron")
    assert not result.ok
    assert result.normalized is None
    assert result.error is not None


def test_normalize_result_original_preserved():
    expr = "05 08 * * * /bin/run"
    result = normalize(expr)
    assert result.original == expr


def test_normalize_field_wildcard():
    assert _normalize_field("*") == "*"


def test_normalize_field_single_number():
    assert _normalize_field("07") == "7"


def test_normalize_field_range():
    assert _normalize_field("01-05") == "1-5"


def test_normalize_field_step():
    assert _normalize_field("*/05") == "*/5"


def test_normalize_field_list():
    assert _normalize_field("1,02,3") == "1,2,3"
