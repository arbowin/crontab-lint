"""Integration tests for the stacker module."""

import datetime
import pytest

from crontab_lint.stacker import stack, format_stack_result


START = datetime.datetime(2024, 1, 1, 0, 0)

STANDARD_PAIRS = [
    ("0 * * * * echo a", "30 * * * * echo b"),
    ("0 6 * * * echo morning", "0 18 * * * echo evening"),
    ("0 0 1 * * echo monthly", "0 0 15 * * echo midmonth"),
]


def test_non_overlapping_pairs_have_no_overlaps():
    for expr_a, expr_b in STANDARD_PAIRS:
        result = stack([expr_a, expr_b], start=START)
        assert not result.has_overlaps(), f"Unexpected overlap for {expr_a!r} and {expr_b!r}"


def test_identical_expressions_always_overlap():
    exprs = [
        "0 * * * * echo a",
        "0 6 * * * echo b",
        "*/5 * * * * echo c",
    ]
    for expr in exprs:
        result = stack([expr, expr], start=START)
        assert result.has_overlaps(), f"Expected overlap for {expr!r}"


def test_three_expressions_partial_overlap():
    result = stack([
        "0 * * * * echo a",
        "0 6 * * * echo b",
        "0 6 * * * echo c",
    ], start=START)
    assert result.is_valid
    assert result.has_overlaps()
    for entry in result.overlaps:
        assert len(entry.expressions) >= 2


def test_format_output_mentions_overlap_count():
    result = stack(["0 * * * * echo a", "0 * * * * echo b"], hours=1, start=START)
    text = format_stack_result(result)
    assert "60" in text or "Overlapping" in text


def test_every_minute_overlap_fills_window():
    result = stack(["* * * * * echo a", "* * * * * echo b"], hours=1, start=START)
    assert result.overlap_count() == 60


def test_overlaps_are_sorted_chronologically():
    result = stack(["0 * * * * echo a", "0 * * * * echo b"], hours=3, start=START)
    timestamps = [e.timestamp for e in result.overlaps]
    assert timestamps == sorted(timestamps)
