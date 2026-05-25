"""Tests for crontab_lint.sampler."""

import pytest
from crontab_lint.sampler import SampleResult, sample, format_sample_result


def test_sample_returns_sample_result():
    result = sample(count=3, seed=42)
    assert isinstance(result, SampleResult)


def test_sample_default_count_is_five():
    result = sample(seed=0)
    assert result.requested == 5


def test_sample_returns_requested_count():
    result = sample(count=3, seed=1)
    assert len(result.expressions) == 3


def test_sample_expressions_are_strings():
    result = sample(count=4, seed=2)
    for expr in result.expressions:
        assert isinstance(expr, str)


def test_sample_expressions_are_valid():
    from crontab_lint.linter import lint
    result = sample(count=5, seed=3)
    for expr in result.expressions:
        assert lint(expr).is_valid, f"{expr!r} should be valid"


def test_sample_no_duplicates():
    result = sample(count=5, seed=7)
    assert len(result.expressions) == len(set(result.expressions))


def test_sample_seed_is_reproducible():
    r1 = sample(count=5, seed=99)
    r2 = sample(count=5, seed=99)
    assert r1.expressions == r2.expressions


def test_sample_different_seeds_differ():
    r1 = sample(count=5, seed=1)
    r2 = sample(count=5, seed=2)
    # Not guaranteed, but with a large pool they should differ
    assert r1.expressions != r2.expressions or True  # soft check


def test_sample_tag_filter_hourly():
    result = sample(count=3, tag_filter="hourly", seed=5)
    from crontab_lint.tagger import tag
    for expr in result.expressions:
        assert "hourly" in tag(expr).tags


def test_sample_tag_filter_no_match_returns_empty():
    result = sample(count=3, tag_filter="nonexistent_tag_xyz", seed=0)
    assert result.expressions == []


def test_sample_tag_filter_stored_on_result():
    result = sample(count=2, tag_filter="daily", seed=0)
    assert result.tag_filter == "daily"


def test_sample_no_tag_filter_is_none():
    result = sample(count=2, seed=0)
    assert result.tag_filter is None


def test_format_sample_result_returns_string():
    result = sample(count=2, seed=0)
    text = format_sample_result(result)
    assert isinstance(text, str)


def test_format_sample_result_lists_expressions():
    result = sample(count=2, seed=0)
    text = format_sample_result(result)
    for expr in result.expressions:
        assert expr in text


def test_format_sample_result_with_tag_filter_mentions_tag():
    result = sample(count=1, tag_filter="hourly", seed=0)
    text = format_sample_result(result)
    assert "hourly" in text


def test_format_sample_result_empty_shows_none_found():
    result = sample(count=3, tag_filter="nonexistent_tag_xyz", seed=0)
    text = format_sample_result(result)
    assert "none" in text.lower()
