"""Integration tests for the sampler module."""

import pytest
from crontab_lint.sampler import sample, format_sample_result
from crontab_lint.linter import lint
from crontab_lint.tagger import tag


STANDARD_TAGS = ["every-minute", "hourly", "daily"]


def test_all_sampled_expressions_pass_lint():
    result = sample(count=10, seed=0)
    for expr in result.expressions:
        lr = lint(expr)
        assert lr.is_valid, f"{expr!r} failed lint"


def test_sampled_count_matches_requested():
    for n in [1, 3, 5]:
        result = sample(count=n, seed=n)
        assert len(result.expressions) == n


def test_tag_filter_every_minute():
    result = sample(count=2, tag_filter="every-minute", seed=10)
    for expr in result.expressions:
        assert "every-minute" in tag(expr).tags


def test_tag_filter_daily():
    result = sample(count=2, tag_filter="daily", seed=20)
    for expr in result.expressions:
        assert "daily" in tag(expr).tags


def test_format_includes_all_expressions():
    result = sample(count=4, seed=42)
    text = format_sample_result(result)
    for expr in result.expressions:
        assert expr in text


def test_format_empty_result_graceful():
    result = sample(count=3, tag_filter="__no_such_tag__", seed=0)
    text = format_sample_result(result)
    assert isinstance(text, str)
    assert len(text) > 0
