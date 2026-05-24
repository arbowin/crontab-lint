"""Tests for crontab_lint.scorer."""

import pytest
from crontab_lint.scorer import score, format_score_result, ScoreResult


def test_score_returns_score_result():
    result = score("* * * * * /bin/true")
    assert isinstance(result, ScoreResult)


def test_score_valid_expression_is_valid():
    result = score("0 9 * * 1 /bin/backup")
    assert result.is_valid is True


def test_score_invalid_expression_is_not_valid():
    result = score("not a cron")
    assert result.is_valid is False
    assert result.score == 0
    assert result.grade == "F"


def test_score_out_of_range_is_not_valid():
    result = score("99 * * * * /bin/true")
    assert result.is_valid is False
    assert result.score == 0


def test_score_clean_expression_is_high():
    result = score("0 0 * * * /bin/backup")
    assert result.score >= 90
    assert result.grade == "A"


def test_score_both_dom_and_dow_lowers_score():
    result = score("0 0 1 * 1 /bin/backup")
    # Validator should produce a warning for this case
    assert result.score < 100


def test_score_many_list_items_penalised():
    result = score("1,2,3,4,5,6,7 * * * * /bin/task")
    assert result.score < 100
    assert any("list items" in p for p in result.penalties)


def test_score_standard_step_no_penalty():
    result = score("*/15 * * * * /bin/task")
    # */N is clean — no step penalty
    assert not any("non-standard step" in p for p in result.penalties)


def test_score_non_standard_step_penalised():
    result = score("1-59/2 * * * * /bin/task")
    assert any("non-standard step" in p for p in result.penalties)


def test_grade_a_for_perfect():
    result = score("0 6 * * * /bin/report")
    assert result.grade == "A"
    assert result.score >= 90


def test_format_score_result_contains_expression():
    result = score("*/5 * * * * /bin/poll")
    text = format_score_result(result)
    assert "*/5 * * * * /bin/poll" in text


def test_format_score_result_contains_grade():
    result = score("0 0 * * * /bin/daily")
    text = format_score_result(result)
    assert "Grade" in text
    assert result.grade in text


def test_format_score_result_no_penalties_line():
    result = score("0 0 * * * /bin/daily")
    text = format_score_result(result)
    assert "none" in text


def test_format_score_result_shows_penalties():
    result = score("1,2,3,4,5,6,7 * * * * /bin/task")
    text = format_score_result(result)
    assert "Penalties" in text
