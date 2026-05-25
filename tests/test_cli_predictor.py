"""Tests for crontab_lint.cli_predictor."""

import argparse
from unittest.mock import patch, mock_open

import pytest

from crontab_lint.cli_predictor import build_parser, main


def test_build_parser_returns_parser():
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    code = main(["0 * * * * echo hi"])
    assert code == 0


def test_invalid_expression_returns_1():
    code = main(["not_valid"])
    assert code == 1


def test_multiple_valid_expressions_returns_0():
    code = main(["0 * * * * echo", "*/5 * * * * echo"])
    assert code == 0


def test_mixed_valid_invalid_returns_1():
    code = main(["0 * * * * echo", "bad expression"])
    assert code == 1


def test_custom_window_accepted():
    code = main(["--window", "6", "0 * * * * echo"])
    assert code == 0


def test_start_flag_accepted():
    code = main(["--start", "2024-01-01T00:00", "0 * * * * echo"])
    assert code == 0


def test_invalid_start_returns_2():
    code = main(["--start", "not-a-date", "0 * * * * echo"])
    assert code == 2


def test_file_flag_reads_expressions(tmp_path):
    cron_file = tmp_path / "crons.txt"
    cron_file.write_text("# comment\n\n0 * * * * echo\n")
    code = main(["-f", str(cron_file)])
    assert code == 0


def test_file_flag_missing_file_returns_2():
    code = main(["-f", "/nonexistent/path/file.txt"])
    assert code == 2


def test_output_contains_expression(capsys):
    main(["0 12 * * * echo"])
    captured = capsys.readouterr()
    assert "0 12 * * * echo" in captured.out


def test_output_contains_window_info(capsys):
    main(["--start", "2024-06-01T00:00", "0 * * * * echo"])
    captured = capsys.readouterr()
    assert "Window" in captured.out
