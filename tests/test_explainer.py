"""Tests for the human-readable explainer module."""

import pytest
from crontab_lint.parser import parse
from crontab_lint.explainer import explain


def test_every_minute():
    result = explain(parse("* * * * * /bin/job"))
    assert result == "Runs every minute."


def test_top_of_every_hour():
    result = explain(parse("0 * * * * /bin/job"))
    assert result == "Runs at the start of every hour."


def test_midnight():
    result = explain(parse("0 0 * * * /bin/job"))
    assert result == "Runs at midnight."


def test_specific_hour_and_minute():
    result = explain(parse("30 9 * * * /bin/job"))
    assert "hour 9" in result
    assert "minute 30" in result


def test_step_minutes():
    result = explain(parse("*/15 * * * * /bin/job"))
    assert "every 15 minutes" in result


def test_specific_day_of_month():
    result = explain(parse("0 0 1 * * /bin/job"))
    assert "1st day" in result


def test_specific_month():
    result = explain(parse("0 0 * 6 * /bin/job"))
    assert "June" in result


def test_specific_day_of_week():
    result = explain(parse("0 9 * * 1 /bin/job"))
    assert "Monday" in result


def test_range_of_days():
    result = explain(parse("0 9 * * 1-5 /bin/job"))
    assert "Monday" in result
    assert "Friday" in result


def test_comma_separated_months():
    result = explain(parse("0 0 1 1,7 * /bin/job"))
    assert "January" in result
    assert "July" in result


def test_result_starts_with_runs():
    result = explain(parse("*/5 * * * * /bin/check"))
    assert result.startswith("Runs ")


def test_result_ends_with_period():
    result = explain(parse("0 12 * * * /bin/job"))
    assert result.endswith(".")


def test_step_hours():
    result = explain(parse("0 */6 * * * /bin/job"))
    assert "every 6 hours" in result


def test_day_of_month_ordinal_2nd():
    result = explain(parse("0 0 2 * * /bin/job"))
    assert "2nd day" in result


def test_day_of_month_ordinal_3rd():
    result = explain(parse("0 0 3 * * /bin/job"))
    assert "3rd day" in result
