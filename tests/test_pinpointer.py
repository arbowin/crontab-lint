"""Tests for crontab_lint.pinpointer."""

import pytest
from crontab_lint.pinpointer import (
    FieldPin,
    PinpointResult,
    pinpoint,
    format_pinpoint_result,
    FIELD_NAMES,
)


def test_pinpoint_returns_pinpoint_result():
    result = pinpoint("* * * * * echo hi")
    assert isinstance(result, PinpointResult)


def test_pinpoint_valid_expression_is_valid():
    result = pinpoint("0 9 * * 1 echo hi")
    assert result.is_valid is True
    assert result.parse_error is None


def test_pinpoint_valid_expression_has_five_pins():
    result = pinpoint("* * * * * echo hi")
    assert len(result.pins) == 5


def test_pinpoint_pin_field_names_match_expected():
    result = pinpoint("* * * * * echo hi")
    names = [p.field_name for p in result.pins]
    assert names == FIELD_NAMES


def test_pinpoint_pin_raw_values_captured():
    result = pinpoint("5 10 * * * echo hi")
    assert result.pins[0].raw_value == "5"
    assert result.pins[1].raw_value == "10"


def test_pinpoint_valid_expression_no_issues():
    result = pinpoint("*/5 * * * * echo hi")
    assert result.fields_with_issues() == []


def test_pinpoint_invalid_minute_has_error_on_minute_field():
    result = pinpoint("99 * * * * echo hi")
    assert result.is_valid is False
    errored = result.fields_with_errors()
    assert any(p.field_name == "minute" for p in errored)


def test_pinpoint_invalid_hour_has_error_on_hour_field():
    result = pinpoint("0 25 * * * echo hi")
    assert result.is_valid is False
    errored = result.fields_with_errors()
    assert any(p.field_name == "hour" for p in errored)


def test_pinpoint_parse_error_returns_empty_pins():
    result = pinpoint("* * *")
    assert result.is_valid is False
    assert result.parse_error is not None
    assert result.pins == []


def test_pinpoint_parse_error_no_valid_fields():
    result = pinpoint("bad")
    assert result.fields_with_issues() == []
    assert result.fields_with_errors() == []


def test_pinpoint_field_index_is_zero_based():
    result = pinpoint("* * * * * echo hi")
    for i, pin in enumerate(result.pins):
        assert pin.field_index == i


def test_format_pinpoint_result_valid_expression():
    result = pinpoint("0 0 * * * echo hi")
    text = format_pinpoint_result(result)
    assert "valid" in text
    assert "0 0 * * * echo hi" in text


def test_format_pinpoint_result_shows_field_name_for_error():
    result = pinpoint("99 * * * * echo hi")
    text = format_pinpoint_result(result)
    assert "minute" in text
    assert "ERROR" in text


def test_format_pinpoint_result_parse_error_shown():
    result = pinpoint("* * *")
    text = format_pinpoint_result(result)
    assert "Parse error" in text


def test_format_pinpoint_no_issues_message():
    result = pinpoint("*/10 * * * * echo hi")
    text = format_pinpoint_result(result)
    assert "No per-field issues" in text
