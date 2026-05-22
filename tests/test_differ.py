"""Tests for crontab_lint.differ."""

import pytest
from crontab_lint.differ import diff, DiffResult, FieldDiff
from crontab_lint.parser import ParseError


def test_identical_expressions_no_changes():
    result = diff("0 * * * * /bin/foo", "0 * * * * /bin/foo")
    assert not result.has_changes


def test_identical_summary_message():
    result = diff("0 * * * * /bin/foo", "0 * * * * /bin/foo")
    assert result.summary() == "No changes detected."


def test_minute_field_change_detected():
    result = diff("0 * * * * /bin/foo", "30 * * * * /bin/foo")
    assert result.has_changes
    assert len(result.field_diffs) == 1
    assert result.field_diffs[0].field == "minute"
    assert result.field_diffs[0].old_value == "0"
    assert result.field_diffs[0].new_value == "30"


def test_hour_field_change_detected():
    result = diff("0 6 * * * /bin/foo", "0 12 * * * /bin/foo")
    assert len(result.field_diffs) == 1
    assert result.field_diffs[0].field == "hour"


def test_multiple_field_changes():
    result = diff("0 6 * * * /bin/foo", "30 12 * * * /bin/foo")
    assert len(result.field_diffs) == 2
    fields = [d.field for d in result.field_diffs]
    assert "minute" in fields
    assert "hour" in fields


def test_command_change_detected():
    result = diff("0 * * * * /bin/foo", "0 * * * * /bin/bar")
    assert result.command_changed
    assert not result.field_diffs


def test_command_and_field_both_changed():
    result = diff("0 * * * * /bin/foo", "5 * * * * /bin/bar")
    assert result.command_changed
    assert len(result.field_diffs) == 1


def test_field_diff_has_explanations():
    result = diff("0 * * * * /bin/foo", "*/5 * * * * /bin/foo")
    diff_item = result.field_diffs[0]
    assert diff_item.old_explanation
    assert diff_item.new_explanation
    assert diff_item.old_explanation != diff_item.new_explanation


def test_field_diff_summary_contains_field_name():
    result = diff("0 * * * * /bin/foo", "30 * * * * /bin/foo")
    summary = result.field_diffs[0].summary()
    assert "minute" in summary
    assert "0" in summary
    assert "30" in summary


def test_summary_includes_all_changed_fields():
    result = diff("0 6 * * * /bin/foo", "30 12 * * * /bin/foo")
    summary = result.summary()
    assert "minute" in summary
    assert "hour" in summary


def test_invalid_old_expression_raises():
    with pytest.raises(ParseError):
        diff("not valid", "0 * * * * /bin/foo")


def test_invalid_new_expression_raises():
    with pytest.raises(ParseError):
        diff("0 * * * * /bin/foo", "bad")


def test_result_stores_original_expressions():
    result = diff("0 * * * * /bin/a", "5 * * * * /bin/b")
    assert result.old_expression == "0 * * * * /bin/a"
    assert result.new_expression == "5 * * * * /bin/b"
