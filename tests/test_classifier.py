"""Tests for crontab_lint.classifier."""

import pytest
from crontab_lint.classifier import classify, ClassifyResult


def test_classify_returns_classify_result():
    result = classify("* * * * * /bin/true")
    assert isinstance(result, ClassifyResult)


def test_classify_invalid_expression_is_not_valid():
    result = classify("not a cron")
    assert result.is_valid is False
    assert result.category is None
    assert result.description == "Invalid expression"


def test_classify_every_minute():
    result = classify("* * * * * /cmd")
    assert result.is_valid is True
    assert result.category == "frequent"
    assert result.subcategory == "every-minute"
    assert "every minute" in result.description.lower()
    assert result.confidence == "high"


def test_classify_every_five_minutes():
    result = classify("*/5 * * * * /cmd")
    assert result.category == "frequent"
    assert result.subcategory == "interval"
    assert "5" in result.description


def test_classify_hourly():
    result = classify("0 * * * * /cmd")
    assert result.category == "hourly"
    assert result.subcategory == "every-hour"
    assert result.confidence == "high"


def test_classify_every_two_hours():
    result = classify("0 */2 * * * /cmd")
    assert result.category == "hourly"
    assert result.subcategory == "interval"
    assert "2" in result.description


def test_classify_daily_midnight():
    result = classify("0 0 * * * /cmd")
    assert result.category == "daily"
    assert result.subcategory == "every-day"
    assert result.confidence == "high"


def test_classify_daily_specific_time():
    result = classify("30 6 * * * /cmd")
    assert result.category == "daily"
    assert "6" in result.description
    assert "30" in result.description


def test_classify_weekly():
    result = classify("0 9 * * 1 /cmd")
    assert result.category == "weekly"
    assert result.subcategory == "specific-day"
    assert "Monday" in result.description


def test_classify_weekly_sunday():
    result = classify("0 0 * * 0 /cmd")
    assert result.category == "weekly"
    assert "Sunday" in result.description


def test_classify_monthly():
    result = classify("0 0 1 * * /cmd")
    assert result.category == "monthly"
    assert result.subcategory == "specific-dom"
    assert "1" in result.description


def test_classify_yearly():
    result = classify("0 0 1 1 * /cmd")
    assert result.category == "yearly"
    assert result.subcategory == "specific-date"


def test_classify_shorthand_daily():
    result = classify("@daily")
    assert result.is_valid is True
    assert result.category == "daily"


def test_classify_shorthand_hourly():
    result = classify("@hourly")
    assert result.is_valid is True
    assert result.category == "hourly"


def test_classify_expression_preserved():
    expr = "15 3 * * 5 /backup.sh"
    result = classify(expr)
    assert result.expression == expr
