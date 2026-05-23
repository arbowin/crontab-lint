"""Integration tests for comparator using real normalizer output."""

import pytest
from crontab_lint.comparator import compare, format_comparison


def test_hourly_variants_are_equivalent():
    exprs = ["@hourly run", "0 * * * * run"]
    result = compare(exprs)
    assert result.has_duplicates()
    assert len(result.duplicate_groups()) == 1


def test_yearly_variants_are_equivalent():
    exprs = ["@yearly task", "@annually task", "0 0 1 1 * task"]
    result = compare(exprs)
    assert result.has_duplicates()
    assert result.duplicate_groups()[0].size() == 3


def test_three_unique_expressions():
    exprs = ["0 1 * * * a", "0 2 * * * b", "0 3 * * * c"]
    result = compare(exprs)
    assert len(result.groups) == 3
    assert not result.has_duplicates()
    assert result.total_expressions() == 3


def test_mixed_valid_invalid_and_duplicate():
    exprs = ["@daily a", "0 0 * * * b", "not-valid", "5 5 * * * c"]
    result = compare(exprs)
    assert result.has_duplicates()
    assert len(result.unresolvable) == 1
    assert result.total_expressions() == 4


def test_format_shows_all_members_of_duplicate_group():
    exprs = ["@daily task_a", "0 0 * * * task_b"]
    result = compare(exprs)
    output = format_comparison(result)
    assert "task_a" in output
    assert "task_b" in output


def test_format_lists_unresolvable_items():
    exprs = ["bad1", "bad2"]
    result = compare(exprs)
    output = format_comparison(result)
    assert "bad1" in output
    assert "bad2" in output
    assert "Could not normalize" in output
