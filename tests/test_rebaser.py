"""Tests for crontab_lint.rebaser."""

import pytest
from crontab_lint.rebaser import rebase, format_rebase_result, RebaseResult


def test_rebase_returns_rebase_result():
    result = rebase("0 0 * * * echo hi")
    assert isinstance(result, RebaseResult)


def test_rebase_valid_expression_is_valid():
    result = rebase("0 0 * * * echo hi")
    assert result.is_valid is True
    assert result.error is None


def test_rebase_invalid_expression_is_not_valid():
    result = rebase("not a cron")
    assert result.is_valid is False
    assert result.rebased is None


def test_rebase_invalid_has_error():
    result = rebase("not a cron")
    assert result.error is not None and len(result.error) > 0


def test_rebase_no_offset_returns_same_fields():
    result = rebase("30 6 * * * /bin/job")
    assert result.rebased.startswith("30 6")


def test_rebase_minute_offset_wraps():
    result = rebase("50 0 * * * /bin/job", minute_offset=15)
    # 50 + 15 = 65 -> 65 % 60 = 5
    assert result.rebased.startswith("5 ")


def test_rebase_hour_offset_wraps():
    result = rebase("0 22 * * * /bin/job", hour_offset=3)
    # 22 + 3 = 25 -> 25 % 24 = 1
    assert result.rebased.startswith("0 1 ")


def test_rebase_minute_and_hour_offset():
    result = rebase("0 12 * * * /bin/job", minute_offset=30, hour_offset=2)
    assert result.rebased.startswith("30 14 ")


def test_rebase_wildcard_minute_unchanged():
    result = rebase("* 6 * * * /bin/job", minute_offset=10)
    assert result.rebased.startswith("* ")


def test_rebase_wildcard_hour_unchanged():
    result = rebase("0 * * * * /bin/job", hour_offset=5)
    parts = result.rebased.split()
    assert parts[1] == "*"


def test_rebase_list_minute():
    result = rebase("0,30 6 * * * /bin/job", minute_offset=5)
    parts = result.rebased.split()
    assert parts[0] == "5,35"


def test_rebase_list_minute_wraps():
    result = rebase("55,58 6 * * * /bin/job", minute_offset=5)
    parts = result.rebased.split()
    assert parts[0] == "0,3"


def test_rebase_preserves_dom_dow_and_command():
    result = rebase("0 9 1 6 * /bin/backup", hour_offset=1)
    parts = result.rebased.split()
    assert parts[2] == "1"
    assert parts[3] == "6"
    assert parts[4] == "*"
    assert parts[5] == "/bin/backup"


def test_rebase_stores_offsets():
    result = rebase("0 0 * * * echo", minute_offset=7, hour_offset=3)
    assert result.minute_offset == 7
    assert result.hour_offset == 3


def test_format_rebase_result_valid():
    result = rebase("0 6 * * * /bin/job", minute_offset=5)
    text = format_rebase_result(result)
    assert "Expression" in text
    assert "Rebased" in text
    assert "Offsets" in text


def test_format_rebase_result_invalid():
    result = rebase("bad expression")
    text = format_rebase_result(result)
    assert "Error" in text
    assert "Rebased" not in text
