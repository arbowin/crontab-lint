import pytest
from crontab_lint.validator import validate, ValidationResult, ValidationIssue


def test_valid_expression_returns_valid():
    result = validate('*/5 * * * * /bin/task')
    assert result.valid is True
    assert result.issues == []


def test_invalid_structure_returns_error():
    result = validate('* * * *')
    assert result.valid is False
    assert result.has_errors()


def test_minute_out_of_range():
    result = validate('60 * * * * /bin/task')
    assert result.valid is False
    errors = [i for i in result.issues if i.severity == 'error']
    assert any('minute' in i.field for i in errors)


def test_hour_out_of_range():
    result = validate('0 24 * * * /bin/task')
    assert result.valid is False
    assert any(i.field == 'hour' for i in result.issues)


def test_day_of_month_out_of_range():
    result = validate('0 0 32 * * /bin/task')
    assert result.valid is False
    assert any(i.field == 'day_of_month' for i in result.issues)


def test_month_out_of_range():
    result = validate('0 0 1 13 * /bin/task')
    assert result.valid is False
    assert any(i.field == 'month' for i in result.issues)


def test_day_of_week_out_of_range():
    result = validate('0 0 * * 8 /bin/task')
    assert result.valid is False
    assert any(i.field == 'day_of_week' for i in result.issues)


def test_invalid_range_start_greater_than_end():
    result = validate('10-5 * * * * /bin/task')
    assert result.valid is False
    assert any('Range start' in i.message for i in result.issues)


def test_step_zero_is_error():
    result = validate('*/0 * * * * /bin/task')
    assert result.valid is False
    assert any('Step value' in i.message for i in result.issues)


def test_large_step_is_warning():
    result = validate('*/100 * * * * /bin/task')
    warnings = [i for i in result.issues if i.severity == 'warning']
    assert any('Step' in i.message for i in warnings)


def test_both_dom_and_dow_warning():
    result = validate('0 0 15 * 1 /bin/task')
    warnings = [i for i in result.issues if i.severity == 'warning']
    assert any('day-of-month' in i.message for i in warnings)


def test_has_errors_method():
    result = validate('99 * * * * /bin/task')
    assert result.has_errors() is True


def test_has_warnings_method():
    result = validate('0 0 15 * 1 /bin/task')
    assert result.has_warnings() is True


def test_comma_separated_valid_values():
    result = validate('0,15,30,45 * * * * /bin/task')
    assert result.valid is True


def test_comma_separated_with_invalid_value():
    result = validate('0,15,61 * * * * /bin/task')
    assert result.valid is False
