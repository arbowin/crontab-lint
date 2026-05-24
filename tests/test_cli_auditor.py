"""Tests for crontab_lint.cli_auditor."""

import json
import pytest
from unittest.mock import patch, mock_open
from crontab_lint.cli_auditor import build_parser, main


VALID_EXPR = "0 6 * * * /usr/bin/job"
INVALID_EXPR = "99 * * *"


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main([VALID_EXPR]) == 0


def test_invalid_expression_returns_1():
    assert main([INVALID_EXPR]) == 1


def test_mixed_returns_1():
    assert main([VALID_EXPR, INVALID_EXPR]) == 1


def test_json_flag_outputs_json(capsys):
    main(["--json", VALID_EXPR])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "entries" in data
    assert data["total"] == 1


def test_json_output_has_valid_count(capsys):
    main(["--json", VALID_EXPR])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["valid"] == 1
    assert data["invalid"] == 0


def test_json_entry_has_expected_keys(capsys):
    main(["--json", VALID_EXPR])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    entry = data["entries"][0]
    for key in ("expression", "valid", "tags", "grade", "frequency_label", "runs_per_day"):
        assert key in entry


def test_text_output_contains_expression(capsys):
    main([VALID_EXPR])
    captured = capsys.readouterr()
    assert "0 6 * * *" in captured.out


def test_text_output_shows_ok(capsys):
    main([VALID_EXPR])
    captured = capsys.readouterr()
    assert "OK" in captured.out


def test_file_flag_reads_expressions():
    file_content = "# comment\n\n0 6 * * * /job\n"
    with patch("builtins.open", mock_open(read_data=file_content)):
        result = main(["-f", "fake.txt"])
    assert result == 0


def test_file_not_found_returns_2(capsys):
    result = main(["-f", "/nonexistent/path/file.txt"])
    assert result == 2
