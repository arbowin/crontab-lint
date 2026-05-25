"""Tests for crontab_lint.cli_digester."""

import json
import pytest
from unittest.mock import patch, mock_open
from crontab_lint.cli_digester import build_parser, main


def test_build_parser_returns_parser():
    import argparse
    assert isinstance(build_parser(), argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["0 6 * * * /bin/job"]) == 0


def test_invalid_expression_returns_1():
    assert main(["99 * * * * /bin/job"]) == 1


def test_multiple_valid_returns_0():
    assert main(["0 6 * * * /bin/a", "*/5 * * * * /bin/b"]) == 0


def test_mixed_valid_invalid_returns_1():
    assert main(["0 6 * * * /bin/a", "99 * * * * /bin/b"]) == 1


def test_json_flag_outputs_json(capsys):
    main(["--json", "0 0 * * * /bin/job"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["is_valid"] is True


def test_json_flag_contains_fingerprint(capsys):
    main(["--json", "0 0 * * * /bin/job"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "fingerprint" in data[0]
    assert len(data[0]["fingerprint"]) == 12


def test_json_invalid_returns_1():
    code = main(["--json", "99 * * * * /bin/job"])
    assert code == 1


def test_output_shows_fingerprint(capsys):
    main(["0 0 * * * /bin/job"])
    captured = capsys.readouterr()
    assert "fingerprint" in captured.out


def test_output_shows_explanation_for_valid(capsys):
    main(["0 0 * * * /bin/job"])
    captured = capsys.readouterr()
    assert "explanation" in captured.out


def test_output_shows_error_for_invalid(capsys):
    main(["99 * * * * /bin/job"])
    captured = capsys.readouterr()
    assert "error" in captured.out


def test_file_flag_reads_expressions(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n0 6 * * * /bin/job\n")
    assert main(["--file", str(f)]) == 0


def test_file_flag_missing_file_returns_2():
    assert main(["--file", "/nonexistent/path/crons.txt"]) == 2
