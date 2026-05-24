"""Tests for crontab_lint.grouper."""

import pytest
from crontab_lint.grouper import (
    GroupResult,
    group,
    has_group,
    format_group_result,
)


def test_group_returns_group_result():
    result = group(["* * * * * cmd"])
    assert isinstance(result, GroupResult)


def test_group_empty_list():
    result = group([])
    assert result.groups == {}
    assert result.ungrouped == []


def test_group_by_tag_every_minute():
    result = group(["* * * * * cmd"], by="tag")
    assert has_group(result, "every_minute")
    assert "* * * * * cmd" in result.members("every_minute")


def test_group_by_tag_hourly():
    result = group(["0 * * * * cmd"], by="tag")
    assert has_group(result, "hourly")


def test_group_by_tag_daily():
    result = group(["0 0 * * * cmd"], by="tag")
    assert has_group(result, "daily")


def test_group_by_tag_weekly():
    result = group(["0 0 * * 0 cmd"], by="tag")
    assert has_group(result, "weekly")


def test_group_by_tag_monthly():
    result = group(["0 0 1 * * cmd"], by="tag")
    assert has_group(result, "monthly")


def test_group_by_tag_yearly():
    result = group(["0 0 1 1 * cmd"], by="tag")
    assert has_group(result, "yearly")


def test_group_by_validity_valid():
    result = group(["0 * * * * cmd"], by="validity")
    assert has_group(result, "valid")
    assert "0 * * * * cmd" in result.members("valid")


def test_group_by_validity_invalid():
    result = group(["not a cron"], by="validity")
    assert has_group(result, "invalid")


def test_group_invalid_expression_goes_to_ungrouped_by_tag():
    result = group(["not a cron"], by="tag")
    assert "not a cron" in result.ungrouped


def test_group_mixed_tags():
    exprs = ["* * * * * a", "0 * * * * b", "0 0 * * * c"]
    result = group(exprs, by="tag")
    assert has_group(result, "every_minute")
    assert has_group(result, "hourly")
    assert has_group(result, "daily")


def test_group_names_sorted():
    exprs = ["* * * * * a", "0 * * * * b"]
    result = group(exprs, by="tag")
    names = result.group_names()
    assert names == sorted(names)


def test_unknown_strategy_raises():
    with pytest.raises(ValueError, match="Unknown grouping strategy"):
        group(["* * * * * cmd"], by="unknown")


def test_format_group_result_contains_group_name():
    result = group(["0 * * * * cmd"], by="tag")
    output = format_group_result(result)
    assert "hourly" in output
    assert "0 * * * * cmd" in output


def test_format_group_result_shows_ungrouped():
    result = group(["bad expression"], by="tag")
    output = format_group_result(result)
    assert "ungrouped" in output
