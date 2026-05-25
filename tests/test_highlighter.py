"""Tests for crontab_lint.highlighter."""
import pytest
from crontab_lint.highlighter import (
    highlight,
    format_highlight_result,
    has_errors,
    HighlightResult,
    FIELD_LABELS,
)


def test_highlight_returns_highlight_result():
    result = highlight("* * * * * /bin/true")
    assert isinstance(result, HighlightResult)


def test_highlight_valid_expression_is_valid():
    result = highlight("0 6 * * 1 /bin/backup")
    assert result.is_valid is True


def test_highlight_invalid_expression_is_not_valid():
    result = highlight("not a cron")
    assert result.is_valid is False


def test_highlight_expression_preserved():
    expr = "*/5 * * * * /usr/bin/check"
    result = highlight(expr)
    assert result.expression == expr


def test_highlighted_contains_ansi_codes():
    result = highlight("* * * * * /bin/true")
    assert "\033[" in result.highlighted


def test_highlight_invalid_highlighted_contains_red():
    result = highlight("bad expression here")
    assert "\033[31m" in result.highlighted


def test_highlight_legend_has_five_entries():
    result = highlight("0 0 * * * /bin/run")
    assert len(result.legend) == 5


def test_highlight_invalid_legend_is_empty():
    result = highlight("only three fields")
    assert result.legend == []


def test_highlight_legend_contains_field_names():
    result = highlight("0 12 * * 5 /bin/report")
    combined = " ".join(result.legend)
    for label in FIELD_LABELS:
        assert label in combined


def test_has_errors_valid_returns_false():
    result = highlight("30 4 * * * /bin/task")
    assert has_errors(result) is False


def test_has_errors_invalid_returns_true():
    result = highlight("99 99 99 99 99 /bin/task")
    assert has_errors(result) is True


def test_format_highlight_result_returns_string():
    result = highlight("* * * * * /bin/true")
    output = format_highlight_result(result)
    assert isinstance(output, str)


def test_format_highlight_result_includes_legend():
    result = highlight("0 0 * * * /bin/run")
    output = format_highlight_result(result)
    assert "Legend" in output


def test_format_highlight_result_invalid_shows_error_note():
    result = highlight("not valid")
    output = format_highlight_result(result)
    assert "errors" in output


def test_highlight_out_of_range_is_not_valid():
    result = highlight("99 * * * * /bin/task")
    assert result.is_valid is False


def test_highlight_five_field_no_command():
    result = highlight("0 0 1 1 0")
    assert result.is_valid is True
    assert len(result.legend) == 5
