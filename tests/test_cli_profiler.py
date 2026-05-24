"""Tests for crontab_lint.cli_profiler."""

import pytest
from crontab_lint.cli_profiler import build_parser, main


def test_build_parser_returns_parser():
    import argparse
    assert isinstance(build_parser(), argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["0 6 * * * /backup"]) == 0


def test_invalid_expression_returns_1():
    assert main(["not_valid"]) == 1


def test_every_minute_prints_frequency(capsys):
    main(["* * * * * /cmd"])
    captured = capsys.readouterr()
    assert "every-minute" in captured.out


def test_daily_prints_runs_per_day(capsys):
    main(["0 6 * * * /cmd"])
    captured = capsys.readouterr()
    assert "Runs/day" in captured.out


def test_invalid_shows_invalid_status(capsys):
    main(["bad expr here"])
    captured = capsys.readouterr()
    assert "INVALID" in captured.out


def test_warn_only_suppresses_clean_output(capsys):
    main(["--warn-only", "0 6 * * * /cmd"])
    captured = capsys.readouterr()
    assert captured.out == ""


def test_warn_only_shows_high_frequency(capsys):
    main(["--warn-only", "* * * * * /cmd"])
    captured = capsys.readouterr()
    assert "WARNING" in captured.out


def test_multiple_expressions_all_shown(capsys):
    main(["0 6 * * * /a", "0 12 * * * /b"])
    captured = capsys.readouterr()
    assert "/a" in captured.out
    assert "/b" in captured.out


def test_file_flag_reads_expressions(tmp_path, capsys):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n0 6 * * * /backup\n\n* * * * * /frequent\n")
    result = main(["-f", str(f)])
    captured = capsys.readouterr()
    assert "/backup" in captured.out
    assert "/frequent" in captured.out


def test_file_flag_missing_file_returns_2(tmp_path):
    result = main(["-f", str(tmp_path / "nonexistent.txt")])
    assert result == 2
