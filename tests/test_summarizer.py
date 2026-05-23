"""Tests for crontab_lint.summarizer."""

import pytest
from crontab_lint.summarizer import summarize, format_summary, SummaryReport


VALID_EXPR = "0 * * * * /bin/task"
WARN_EXPR = "0 * 5 * 1 /bin/task"   # both DOM and DOW set -> warning
ERROR_EXPR = "99 * * * * /bin/bad"   # minute out of range


def test_summarize_empty_list():
    report = summarize([])
    assert report.total == 0
    assert report.valid == 0
    assert report.warnings == 0
    assert report.errors == 0


def test_summarize_all_valid():
    report = summarize([VALID_EXPR, "*/5 * * * * /bin/x"])
    assert report.total == 2
    assert report.valid == 2
    assert report.warnings == 0
    assert report.errors == 0


def test_summarize_counts_errors():
    report = summarize([ERROR_EXPR])
    assert report.errors == 1
    assert report.valid == 0
    assert ERROR_EXPR in report.by_severity["error"]


def test_summarize_counts_warnings():
    report = summarize([WARN_EXPR])
    assert report.warnings == 1
    assert report.valid == 0
    assert WARN_EXPR in report.by_severity["warning"]


def test_summarize_mixed():
    report = summarize([VALID_EXPR, WARN_EXPR, ERROR_EXPR])
    assert report.total == 3
    assert report.valid == 1
    assert report.warnings == 1
    assert report.errors == 1


def test_format_summary_contains_totals():
    report = summarize([VALID_EXPR, ERROR_EXPR])
    text = format_summary(report)
    assert "Total expressions" in text
    assert "2" in text


def test_format_summary_lists_error_expressions():
    report = summarize([ERROR_EXPR])
    text = format_summary(report)
    assert "Expressions with errors" in text
    assert ERROR_EXPR in text


def test_format_summary_lists_warning_expressions():
    report = summarize([WARN_EXPR])
    text = format_summary(report)
    assert "Expressions with warnings" in text
    assert WARN_EXPR in text


def test_format_summary_no_error_section_when_none():
    report = summarize([VALID_EXPR])
    text = format_summary(report)
    assert "Expressions with errors" not in text


def test_format_summary_header_present():
    report = SummaryReport()
    text = format_summary(report)
    assert "Crontab Lint Summary" in text
