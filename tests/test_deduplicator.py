"""Tests for crontab_lint.deduplicator."""
import pytest
from crontab_lint.deduplicator import (
    DeduplicateEntry,
    DeduplicateResult,
    deduplicate,
    format_deduplicate_result,
)


def test_deduplicate_returns_deduplicate_result():
    result = deduplicate(["* * * * * echo hi"])
    assert isinstance(result, DeduplicateResult)


def test_deduplicate_empty_list():
    result = deduplicate([])
    assert result.total == 0
    assert result.duplicate_count == 0
    assert result.unique_expressions == []


def test_deduplicate_single_expression_is_unique():
    result = deduplicate(["0 * * * * echo hi"])
    assert result.total == 1
    assert result.duplicate_count == 0
    assert not result.entries[0].is_duplicate


def test_deduplicate_identical_expressions_second_is_duplicate():
    result = deduplicate(["0 * * * * echo hi", "0 * * * * echo hi"])
    assert result.total == 2
    assert result.duplicate_count == 1
    assert not result.entries[0].is_duplicate
    assert result.entries[1].is_duplicate


def test_deduplicate_first_seen_index_points_to_canonical():
    result = deduplicate(["0 * * * * echo hi", "0 * * * * echo hi"])
    assert result.entries[1].first_seen_index == 0


def test_deduplicate_canonical_has_no_first_seen_index():
    result = deduplicate(["0 * * * * echo hi"])
    assert result.entries[0].first_seen_index is None


def test_deduplicate_unique_expressions_only_returns_non_duplicates():
    exprs = ["0 * * * * a", "0 * * * * a", "5 * * * * b"]
    result = deduplicate(exprs)
    assert len(result.unique_expressions) == 2


def test_deduplicate_shorthand_and_explicit_are_equivalent():
    # @hourly == 0 * * * *
    result = deduplicate(["@hourly echo hi", "0 * * * * echo hi"])
    assert result.duplicate_count == 1


def test_deduplicate_three_identical_one_unique():
    exprs = ["* * * * * a", "* * * * * a", "* * * * * a", "0 0 * * * b"]
    result = deduplicate(exprs)
    assert result.duplicate_count == 2
    assert len(result.unique_expressions) == 2


def test_deduplicate_preserves_order():
    exprs = ["0 1 * * * a", "0 2 * * * b", "0 3 * * * c"]
    result = deduplicate(exprs)
    assert [e.expression for e in result.entries] == exprs


def test_deduplicate_entry_has_normalized_field():
    result = deduplicate(["0 * * * * echo"])
    assert result.entries[0].normalized != ""


def test_deduplicate_entry_to_dict():
    result = deduplicate(["* * * * * echo"])
    d = result.entries[0].to_dict()
    assert "expression" in d
    assert "is_duplicate" in d
    assert "first_seen_index" in d
    assert "normalized" in d


def test_format_deduplicate_result_contains_unique_label():
    result = deduplicate(["0 * * * * echo"])
    output = format_deduplicate_result(result)
    assert "UNIQUE" in output


def test_format_deduplicate_result_contains_duplicate_label():
    result = deduplicate(["0 * * * * echo", "0 * * * * echo"])
    output = format_deduplicate_result(result)
    assert "DUPLICATE" in output


def test_format_deduplicate_result_contains_totals():
    result = deduplicate(["0 * * * * echo", "0 * * * * echo"])
    output = format_deduplicate_result(result)
    assert "Total" in output
    assert "Duplicates" in output
