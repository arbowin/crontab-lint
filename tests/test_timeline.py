"""Tests for crontab_lint.timeline."""

from datetime import datetime

import pytest

from crontab_lint.timeline import (
    TimelineEntry,
    TimelineResult,
    build_timeline,
    format_timeline,
)

START = datetime(2024, 1, 1, 0, 0, 0)


def test_build_timeline_returns_timeline_result():
    result = build_timeline(["* * * * * echo hi"], start=START, count=3)
    assert isinstance(result, TimelineResult)


def test_build_timeline_valid_expression_has_entries():
    result = build_timeline(["* * * * * echo hi"], start=START, count=3)
    assert len(result.entries) == 3


def test_build_timeline_entries_are_sorted():
    result = build_timeline(
        ["0 * * * * cmd", "30 * * * * cmd"],
        start=START,
        count=2,
    )
    times = [e.fires_at for e in result.entries]
    assert times == sorted(times)


def test_build_timeline_invalid_expression_recorded():
    result = build_timeline(["not_a_cron"], start=START, count=3)
    assert "not_a_cron" in result.invalid_expressions


def test_build_timeline_invalid_has_no_entries():
    result = build_timeline(["not_a_cron"], start=START, count=3)
    assert result.entries == []


def test_build_timeline_has_invalid_flag():
    result = build_timeline(["bad"], start=START, count=1)
    assert result.has_invalid is True


def test_build_timeline_no_invalid_flag_for_valid():
    result = build_timeline(["* * * * * cmd"], start=START, count=1)
    assert result.has_invalid is False


def test_build_timeline_empty_list():
    result = build_timeline([], start=START, count=5)
    assert result.entries == []
    assert result.invalid_expressions == []


def test_timeline_entry_to_dict():
    dt = datetime(2024, 6, 15, 12, 30)
    entry = TimelineEntry(expression="0 12 * * * cmd", fires_at=dt, is_valid=True)
    d = entry.to_dict()
    assert d["expression"] == "0 12 * * * cmd"
    assert d["fires_at"] == "2024-06-15T12:30:00"
    assert d["is_valid"] is True


def test_format_timeline_contains_expression():
    result = build_timeline(["0 9 * * * cmd"], start=START, count=1)
    output = format_timeline(result)
    assert "0 9 * * * cmd" in output


def test_format_timeline_empty_entries():
    result = TimelineResult(entries=[], invalid_expressions=[])
    output = format_timeline(result)
    assert "No scheduled runs found" in output


def test_format_timeline_shows_invalid():
    result = build_timeline(["garbage"], start=START, count=1)
    output = format_timeline(result)
    assert "invalid" in output
    assert "garbage" in output


def test_build_timeline_mixed_valid_and_invalid():
    result = build_timeline(
        ["* * * * * cmd", "bad_expr"],
        start=START,
        count=2,
    )
    assert len(result.entries) == 2
    assert len(result.invalid_expressions) == 1
