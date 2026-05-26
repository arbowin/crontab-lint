"""Tests for crontab_lint.cli_estimator."""

import pytest
from crontab_lint.cli_estimator import build_parser, main


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["* * * * * /bin/true"]) == 0


def test_invalid_expression_returns_1():
    assert main(["bad expression"]) == 1


def test_multiple_valid_expressions_returns_0():
    assert main(["* * * * * /bin/true", "0 * * * * /bin/hourly"]) == 0


def test_mixed_valid_invalid_returns_1():
    assert main(["* * * * * /bin/true", "bad"]) == 1


def test_valid_expression_prints_interval(capsys):
    main(["* * * * * /bin/true"])
    captured = capsys.readouterr()
    assert "Interval" in captured.out


def test_valid_expression_prints_runs_per_day(capsys):
    main(["* * * * * /bin/true"])
    captured = capsys.readouterr()
    assert "Runs/day" in captured.out


def test_invalid_expression_prints_error(capsys):
    main(["bad"])
    captured = capsys.readouterr()
    assert "Error" in captured.out


def test_file_flag_reads_expressions(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n\n* * * * * /bin/true\n0 * * * * /bin/hourly\n")
    assert main(["-f", str(f)]) == 0


def test_file_flag_missing_file_returns_2():
    assert main(["-f", "/nonexistent/path/crons.txt"]) == 2


def test_hourly_output_contains_hour(capsys):
    main(["0 * * * * /bin/hourly"])
    captured = capsys.readouterr()
    assert "hour" in captured.out
