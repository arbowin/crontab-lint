"""Tests for crontab_lint.rotator."""

import pytest
from crontab_lint.rotator import rotate, format_rotate_result, RotateResult, RotateEntry


def test_rotate_returns_rotate_result():
    result = rotate(["0 * * * * /bin/true"])
    assert isinstance(result, RotateResult)


def test_rotate_empty_list():
    result = rotate([])
    assert result.total == 0
    assert result.valid_count == 0


def test_rotate_single_expression_no_shift():
    result = rotate(["10 * * * * /bin/true"], step=5)
    assert result.entries[0].rotated == "10 * * * * /bin/true"


def test_rotate_second_expression_shifted():
    result = rotate(["0 * * * * /a", "0 * * * * /b"], step=5)
    assert result.entries[1].rotated.startswith("5 ")


def test_rotate_wraps_at_60():
    result = rotate(["0 * * * * /a"] * 13, step=5)
    # index 12 -> offset 60 % 60 == 0
    assert result.entries[12].rotated.startswith("0 ")


def test_rotate_wildcard_minute_unchanged():
    result = rotate(["* * * * * /bin/true"], step=10)
    assert result.entries[0].rotated.startswith("* ")


def test_rotate_invalid_expression_is_not_valid():
    result = rotate(["not a cron"])
    assert not result.entries[0].is_valid


def test_rotate_invalid_has_error():
    result = rotate(["not a cron"])
    assert result.entries[0].error is not None


def test_rotate_invalid_rotated_equals_original():
    result = rotate(["bad"])
    assert result.entries[0].rotated == "bad"


def test_rotate_valid_count():
    result = rotate(["0 * * * * /a", "bad", "5 * * * * /b"])
    assert result.valid_count == 2


def test_rotate_invalid_count():
    result = rotate(["0 * * * * /a", "bad"])
    assert result.invalid_count == 1


def test_rotate_step_stored():
    result = rotate([], step=15)
    assert result.step == 15


def test_rotate_entry_to_dict():
    entry = RotateEntry(original="0 * * * * /a", rotated="5 * * * * /a", is_valid=True)
    d = entry.to_dict()
    assert d["original"] == "0 * * * * /a"
    assert d["rotated"] == "5 * * * * /a"
    assert d["is_valid"] is True
    assert d["error"] is None


def test_format_rotate_result_contains_header():
    result = rotate(["0 * * * * /bin/true"], step=5)
    output = format_rotate_result(result)
    assert "Rotated" in output
    assert "step=5" in output


def test_format_rotate_result_shows_arrow_for_valid():
    result = rotate(["0 * * * * /bin/true"], step=5)
    output = format_rotate_result(result)
    assert "->" in output


def test_format_rotate_result_shows_error_for_invalid():
    result = rotate(["garbage"])
    output = format_rotate_result(result)
    assert "ERROR" in output


def test_rotate_multiple_step10():
    exprs = [f"{i*10 % 60} * * * * /job{i}" for i in range(6)]
    result = rotate(exprs, step=10)
    assert result.valid_count == 6
