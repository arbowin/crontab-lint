"""Tests for crontab_lint.resolver."""

from datetime import datetime

import pytest

from crontab_lint.resolver import ResolveResult, format_resolve_result, resolve

FIXED = datetime(2024, 1, 15, 12, 0, 0)  # Monday noon


def test_resolve_returns_resolve_result():
    result = resolve("* * * * * echo hi", after=FIXED)
    assert isinstance(result, ResolveResult)


def test_resolve_valid_expression_is_valid():
    result = resolve("0 * * * * echo hi", after=FIXED)
    assert result.is_valid is True
    assert result.error is None


def test_resolve_invalid_expression_is_not_valid():
    result = resolve("bad expression here", after=FIXED)
    assert result.is_valid is False
    assert result.error is not None


def test_resolve_default_count_is_five():
    result = resolve("* * * * * echo hi", after=FIXED)
    assert len(result.runs) == 5


def test_resolve_custom_count():
    result = resolve("* * * * * echo hi", count=3, after=FIXED)
    assert len(result.runs) == 3


def test_resolve_count_capped_at_fifty():
    result = resolve("* * * * * echo hi", count=200, after=FIXED)
    assert len(result.runs) == 50


def test_resolve_count_minimum_is_one():
    result = resolve("* * * * * echo hi", count=0, after=FIXED)
    assert len(result.runs) == 1


def test_resolve_runs_are_strings():
    result = resolve("0 9 * * 1 echo hi", after=FIXED)
    for run in result.runs:
        assert isinstance(run, str)


def test_resolve_custom_format():
    result = resolve("0 0 * * * echo hi", count=1, after=FIXED, fmt="%d/%m/%Y")
    assert len(result.runs) == 1
    assert "/" in result.runs[0]


def test_resolve_invalid_has_no_runs():
    result = resolve("99 * * * * echo hi", after=FIXED)
    assert result.has_runs() is False


def test_resolve_shorthand_daily():
    result = resolve("@daily echo hi", count=2, after=FIXED)
    assert result.is_valid is True
    assert len(result.runs) == 2


def test_format_resolve_result_valid():
    result = resolve("0 12 * * * echo hi", count=2, after=FIXED)
    output = format_resolve_result(result)
    assert "Expression" in output
    assert "Next runs" in output
    assert "1." in output


def test_format_resolve_result_invalid():
    result = resolve("not valid", after=FIXED)
    output = format_resolve_result(result)
    assert "Error" in output
    assert "Next runs" not in output


def test_resolve_expression_preserved():
    expr = "30 6 * * 1-5 echo hi"
    result = resolve(expr, after=FIXED)
    assert result.expression == expr
