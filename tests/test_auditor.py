"""Tests for crontab_lint.auditor."""

import pytest
from crontab_lint.auditor import audit, format_audit_report, AuditEntry, AuditReport


VALID_EXPR = "0 * * * * /usr/bin/backup"
INVALID_EXPR = "99 * * *"
EVERY_MINUTE = "* * * * * /bin/check"


def test_audit_returns_audit_report():
    report = audit([VALID_EXPR])
    assert isinstance(report, AuditReport)


def test_audit_empty_list():
    report = audit([])
    assert report.total == 0
    assert report.valid_count == 0
    assert report.invalid_count == 0


def test_audit_single_valid_expression():
    report = audit([VALID_EXPR])
    assert report.total == 1
    assert report.valid_count == 1
    assert report.invalid_count == 0


def test_audit_single_invalid_expression():
    report = audit([INVALID_EXPR])
    assert report.total == 1
    assert report.invalid_count == 1
    assert report.valid_count == 0


def test_audit_entry_has_expression():
    report = audit([VALID_EXPR])
    assert report.entries[0].expression == VALID_EXPR


def test_audit_entry_is_valid_for_valid_expression():
    report = audit([VALID_EXPR])
    assert report.entries[0].is_valid() is True


def test_audit_entry_is_not_valid_for_invalid_expression():
    report = audit([INVALID_EXPR])
    assert report.entries[0].is_valid() is False


def test_audit_entry_has_tags():
    report = audit([VALID_EXPR])
    assert isinstance(report.entries[0].tags, list)


def test_audit_entry_has_grade():
    report = audit([VALID_EXPR])
    assert report.entries[0].grade in ("A", "B", "C", "D", "F")


def test_audit_entry_has_frequency_label():
    report = audit([EVERY_MINUTE])
    assert isinstance(report.entries[0].frequency_label, str)
    assert len(report.entries[0].frequency_label) > 0


def test_audit_entry_has_runs_per_day():
    report = audit([EVERY_MINUTE])
    assert report.entries[0].runs_per_day == 1440


def test_audit_entry_to_dict_keys():
    report = audit([VALID_EXPR])
    d = report.entries[0].to_dict()
    for key in ("expression", "valid", "tags", "grade", "frequency_label", "runs_per_day", "issues", "explanation"):
        assert key in d


def test_audit_multiple_expressions_counts():
    report = audit([VALID_EXPR, INVALID_EXPR, EVERY_MINUTE])
    assert report.total == 3
    assert report.valid_count == 2
    assert report.invalid_count == 1


def test_format_audit_report_returns_string():
    report = audit([VALID_EXPR])
    output = format_audit_report(report)
    assert isinstance(output, str)


def test_format_audit_report_contains_expression():
    report = audit([VALID_EXPR])
    output = format_audit_report(report)
    assert "0 * * * *" in output


def test_format_audit_report_shows_invalid_status():
    report = audit([INVALID_EXPR])
    output = format_audit_report(report)
    assert "INVALID" in output


def test_format_audit_report_shows_ok_status():
    report = audit([VALID_EXPR])
    output = format_audit_report(report)
    assert "OK" in output


def test_format_audit_report_shows_summary_line():
    report = audit([VALID_EXPR, INVALID_EXPR])
    output = format_audit_report(report)
    assert "2 expression(s)" in output
