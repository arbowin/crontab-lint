"""Tests for crontab_lint.formatter."""

import pytest
from crontab_lint.formatter import format_result, format_many
from crontab_lint.linter import lint, lint_many


def test_format_result_valid_expression():
    result = lint("0 * * * * /usr/bin/backup")
    output = format_result(result)
    assert "0 * * * * /usr/bin/backup" in output
    assert "OK" in output


def test_format_result_includes_explanation():
    result = lint("0 * * * * /bin/run")
    output = format_result(result)
    assert "Meaning:" in output


def test_format_result_invalid_shows_error():
    result = lint("99 * * * * /bin/run")
    output = format_result(result)
    assert "ERROR" in output
    assert "INVALID" in output


def test_format_result_warning_shown():
    result = lint("0 * 5 * 1 /bin/run")
    output = format_result(result)
    assert "WARNING" in output


def test_format_result_verbose_no_issues():
    result = lint("0 * * * * /bin/run")
    output = format_result(result, verbose=True)
    assert "No issues found" in output


def test_format_result_not_verbose_hides_no_issues_message():
    result = lint("0 * * * * /bin/run")
    output = format_result(result, verbose=False)
    assert "No issues found" not in output


def test_format_many_empty_list():
    output = format_many([])
    assert "No expressions" in output


def test_format_many_summary_line():
    results = lint_many(["0 * * * * /bin/a", "99 * * * * /bin/b"])
    output = format_many(results)
    assert "Summary:" in output
    assert "2 expression(s)" in output


def test_format_many_counts_errors():
    results = lint_many(["0 * * * * /bin/a", "99 * * * * /bin/b"])
    output = format_many(results)
    assert "1 error(s)" in output


def test_format_many_counts_ok():
    results = lint_many(["0 * * * * /bin/a", "30 6 * * * /bin/b"])
    output = format_many(results)
    assert "2 OK" in output


def test_format_many_includes_index():
    results = lint_many(["0 * * * * /bin/a", "0 6 * * * /bin/b"])
    output = format_many(results)
    assert "[1/2]" in output
    assert "[2/2]" in output
