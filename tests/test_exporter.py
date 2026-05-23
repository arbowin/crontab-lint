"""Tests for crontab_lint.exporter."""

from __future__ import annotations

import csv
import io
import json

import pytest

from crontab_lint.exporter import to_csv, to_json
from crontab_lint.linter import lint


# ---------------------------------------------------------------------------
# to_json
# ---------------------------------------------------------------------------

def test_to_json_returns_string():
    results = [lint("* * * * * echo hi")]
    output = to_json(results)
    assert isinstance(output, str)


def test_to_json_valid_expression():
    results = [lint("0 * * * * echo hi")]
    data = json.loads(to_json(results))
    assert len(data) == 1
    assert data[0]["expression"] == "0 * * * * echo hi"
    assert data[0]["valid"] is True
    assert data[0]["issues"] == []


def test_to_json_invalid_expression_has_issues():
    results = [lint("99 * * * * echo hi")]
    data = json.loads(to_json(results))
    assert data[0]["valid"] is False
    assert len(data[0]["issues"]) >= 1
    assert data[0]["issues"][0]["severity"] == "error"


def test_to_json_multiple_results():
    results = [lint("* * * * * echo a"), lint("0 0 * * * echo b")]
    data = json.loads(to_json(results))
    assert len(data) == 2


def test_to_json_includes_explanation():
    results = [lint("* * * * * echo hi")]
    data = json.loads(to_json(results))
    assert data[0]["explanation"] != ""


def test_to_json_empty_list():
    output = to_json([])
    assert json.loads(output) == []


def test_to_json_issue_fields_present():
    """Each issue dict should contain 'severity', 'field', and 'message' keys."""
    results = [lint("99 * * * * echo hi")]
    data = json.loads(to_json(results))
    issue = data[0]["issues"][0]
    assert "severity" in issue
    assert "field" in issue
    assert "message" in issue


# ---------------------------------------------------------------------------
# to_csv
# ---------------------------------------------------------------------------

def test_to_csv_returns_string():
    results = [lint("* * * * * echo hi")]
    output = to_csv(results)
    assert isinstance(output, str)


def test_to_csv_has_header():
    results = [lint("* * * * * echo hi")]
    output = to_csv(results)
    reader = csv.DictReader(io.StringIO(output))
    assert "expression" in reader.fieldnames
    assert "valid" in reader.fieldnames
    assert "severity" in reader.fieldnames


def test_to_csv_valid_expression_single_row():
    results = [lint("0 0 * * * echo hi")]
    output = to_csv(results)
    rows = list(csv.DictReader(io.StringIO(output)))
    assert len(rows) == 1
    assert rows[0]["valid"] == "True"
    assert rows[0]["severity"] == ""


def test_to_csv_invalid_expression_has_issue_row():
    results = [lint("99 * * * * echo hi")]
    output = to_csv(results)
    rows = list(csv.DictReader(io.StringIO(output)))
    assert len(rows) >= 1
    assert rows[0]["severity"] == "error"
    assert rows[0]["message"] != ""


def test_to_csv_empty_list_only_header():
    output = to_csv([])
    rows = list(csv.DictReader(io.StringIO(output)))
    assert rows == []
