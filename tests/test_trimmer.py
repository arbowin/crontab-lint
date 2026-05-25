"""Tests for crontab_lint.trimmer."""

import pytest
from crontab_lint.trimmer import trim, format_trim_result, TrimResult


def test_trim_returns_trim_result():
    result = trim("* * * * *")
    assert isinstance(result, TrimResult)


def test_trim_valid_expression_is_valid():
    result = trim("0 6 * * *")
    assert result.is_valid is True
    assert result.error is None


def test_trim_invalid_expression_is_not_valid():
    result = trim("invalid")
    assert result.is_valid is False
    assert result.error is not None


def test_trim_no_redundancy_unchanged():
    result = trim("0 6 * * *")
    assert result.changed is False
    assert result.trimmed == "0 6 * * *"


def test_trim_step_of_one_simplified():
    result = trim("*/1 * * * *")
    assert result.is_valid is True
    assert result.trimmed.startswith("*")
    assert "*/1" not in result.trimmed
    assert result.changed is True


def test_trim_step_of_one_in_hour_field():
    result = trim("0 */1 * * *")
    assert result.is_valid is True
    assert "*/1" not in result.trimmed
    assert result.changed is True


def test_trim_step_of_two_not_simplified():
    result = trim("*/2 * * * *")
    assert "*/2" in result.trimmed
    assert result.changed is False


def test_trim_duplicate_list_items_removed():
    result = trim("1,1,2 * * * *")
    assert result.is_valid is True
    assert "1,1" not in result.trimmed
    assert result.changed is True


def test_trim_duplicate_list_reason_reported():
    result = trim("1,1,2 * * * *")
    assert len(result.removed_redundancy) >= 1
    assert any("deduplicated" in r for r in result.removed_redundancy)


def test_trim_step_one_reason_reported():
    result = trim("*/1 * * * *")
    assert any("redundant" in r for r in result.removed_redundancy)


def test_trim_wildcard_unchanged():
    result = trim("* * * * *")
    assert result.changed is False
    assert result.trimmed == "* * * * *"


def test_trim_preserves_command():
    result = trim("*/1 * * * * /usr/bin/backup")
    assert "/usr/bin/backup" in result.trimmed


def test_trim_out_of_range_is_not_valid():
    result = trim("99 * * * *")
    assert result.is_valid is False


def test_trim_expression_field_preserved():
    expr = "5 4 * * 1"
    result = trim(expr)
    assert result.expression == expr


def test_format_trim_result_valid():
    result = trim("0 6 * * *")
    output = format_trim_result(result)
    assert "Expression" in output
    assert "Trimmed" in output


def test_format_trim_result_invalid():
    result = trim("bad expression")
    output = format_trim_result(result)
    assert "Error" in output


def test_format_trim_result_shows_changes():
    result = trim("*/1 * * * *")
    output = format_trim_result(result)
    assert "yes" in output
    assert "Changes" in output


def test_format_trim_result_no_changes():
    result = trim("0 0 * * *")
    output = format_trim_result(result)
    assert "no" in output
