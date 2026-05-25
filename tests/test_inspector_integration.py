"""Integration tests for the inspector module."""
import pytest
from crontab_lint.inspector import inspect


STANDARD_EXPRESSIONS = [
    ("* * * * * /bin/true", "every_minute"),
    ("0 * * * * /bin/true", "hourly"),
    ("0 0 * * * /bin/true", "daily_midnight"),
    ("0 9 * * 1-5 /bin/true", "weekdays"),
    ("*/15 * * * * /bin/true", "every_15_min"),
    ("0 6,12,18 * * * /bin/true", "three_times_daily"),
]


@pytest.mark.parametrize("expr,label", STANDARD_EXPRESSIONS)
def test_standard_expressions_are_valid(expr, label):
    result = inspect(expr)
    assert result.is_valid, f"{label}: {result.error}"


@pytest.mark.parametrize("expr,label", STANDARD_EXPRESSIONS)
def test_standard_expressions_have_five_fields(expr, label):
    result = inspect(expr)
    assert len(result.fields) == 5, label


def test_every_minute_all_wildcards():
    result = inspect("* * * * * /bin/true")
    assert all(f.kind == "wildcard" for f in result.fields)


def test_step_field_correct_values():
    result = inspect("*/10 * * * * /bin/true")
    minute = result.fields[0]
    assert minute.values == [0, 10, 20, 30, 40, 50]


def test_range_field_correct_values():
    result = inspect("0 9-11 * * * /bin/true")
    hour = result.fields[1]
    assert hour.values == [9, 10, 11]


def test_list_field_correct_values():
    result = inspect("0 6,12,18 * * * /bin/true")
    hour = result.fields[1]
    assert hour.values == [6, 12, 18]


def test_weekday_range_values():
    result = inspect("0 9 * * 1-5 /bin/true")
    dow = result.fields[4]
    assert dow.kind == "range"
    assert dow.values == [1, 2, 3, 4, 5]


def test_to_dict_roundtrip():
    result = inspect("0 9 * * * /bin/true")
    d = result.to_dict()
    assert d["is_valid"] is True
    assert len(d["fields"]) == 5
    assert d["fields"][0]["kind"] == "value"
    assert d["fields"][0]["values"] == [0]
