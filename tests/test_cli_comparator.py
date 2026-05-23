"""Tests for crontab_lint.cli_comparator module."""

import json
import os
import tempfile
import pytest

from crontab_lint.cli_comparator import main, build_parser


def test_no_args_returns_2():
    assert main([]) == 2


def test_single_valid_expression_returns_0():
    assert main(["0 * * * * echo hi"]) == 0


def test_duplicate_expressions_returns_1():
    assert main(["0 0 * * * cmd", "0 0 * * * other"]) == 1


def test_different_expressions_returns_0():
    assert main(["0 * * * * cmd", "30 * * * * cmd"]) == 0


def test_shorthand_duplicate_returns_1():
    assert main(["@daily backup", "0 0 * * * backup"]) == 1


def test_json_output_is_valid_json(capsys):
    main(["--json", "0 * * * * cmd"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "has_duplicates" in data
    assert "groups" in data
    assert "unresolvable" in data


def test_json_output_no_duplicates(capsys):
    main(["--json", "0 * * * * cmd"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["has_duplicates"] is False


def test_json_output_with_duplicates(capsys):
    main(["--json", "0 0 * * * a", "0 0 * * * b"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data["has_duplicates"] is True
    assert len(data["groups"]) == 1
    assert len(data["groups"][0]["expressions"]) == 2


def test_file_flag_reads_expressions():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
        f.write("# comment\n")
        f.write("0 * * * * cmd\n")
        f.write("\n")
        f.write("30 * * * * cmd\n")
        fname = f.name
    try:
        result = main(["-f", fname])
        assert result == 0
    finally:
        os.unlink(fname)


def test_file_flag_missing_file_returns_2():
    result = main(["-f", "/nonexistent/path/crons.txt"])
    assert result == 2


def test_build_parser_returns_parser():
    p = build_parser()
    assert p is not None
