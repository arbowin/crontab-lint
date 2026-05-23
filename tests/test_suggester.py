"""Tests for crontab_lint.suggester."""

import pytest
from crontab_lint.suggester import suggest, SuggestionResult, Suggestion


def test_suggest_returns_suggestion_result():
    result = suggest("* * * * * echo hi")
    assert isinstance(result, SuggestionResult)


def test_suggest_valid_no_shorthand_has_no_suggestions():
    result = suggest("5 4 * * 1 echo hi")
    assert not result.has_suggestions()


def test_suggest_daily_shorthand():
    result = suggest("0 0 * * * echo hi")
    assert result.has_suggestions()
    assert any("@daily" in s.message for s in result.suggestions)


def test_suggest_hourly_shorthand():
    result = suggest("0 * * * * echo hi")
    assert result.has_suggestions()
    assert any("@hourly" in s.message for s in result.suggestions)


def test_suggest_yearly_shorthand():
    result = suggest("0 0 1 1 * echo hi")
    assert result.has_suggestions()
    assert any("@yearly" in s.message for s in result.suggestions)


def test_suggest_shorthand_includes_suggested_expression():
    result = suggest("0 0 * * * echo hi")
    shorthand_suggestions = [
        s for s in result.suggestions if s.suggested_expression is not None
    ]
    assert len(shorthand_suggestions) == 1
    assert shorthand_suggestions[0].suggested_expression == "@daily"


def test_suggest_parse_error_returns_suggestion():
    result = suggest("not_a_cron")
    assert result.has_suggestions()
    assert any("parse error" in s.message.lower() for s in result.suggestions)


def test_suggest_minute_out_of_range():
    result = suggest("99 * * * * echo hi")
    assert result.has_suggestions()
    assert any("minute" in s.message.lower() or "range" in s.message.lower() for s in result.suggestions)


def test_suggest_hour_out_of_range():
    result = suggest("0 25 * * * echo hi")
    assert result.has_suggestions()
    assert any("hour" in s.message.lower() or "range" in s.message.lower() for s in result.suggestions)


def test_suggest_both_dom_and_dow_warning():
    result = suggest("0 0 1 * 1 echo hi")
    assert result.has_suggestions()
    assert any(
        "day-of-month" in s.message.lower() or "day-of-week" in s.message.lower()
        for s in result.suggestions
    )


def test_suggestion_has_no_suggestions_for_clean_expression():
    result = suggest("30 9 * * 1-5 echo hi")
    assert not result.has_suggestions()


def test_suggest_original_preserved():
    expr = "0 0 * * * echo hi"
    result = suggest(expr)
    assert result.original == expr
