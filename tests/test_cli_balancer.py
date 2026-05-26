"""Tests for crontab_lint.cli_balancer."""
import pytest
from unittest.mock import patch, mock_open
from crontab_lint.cli_balancer import build_parser, main


def test_build_parser_returns_parser():
    import argparse
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["* * * * * echo"]) == 0


def test_invalid_expression_returns_1():
    assert main(["not a cron"]) == 1


def test_multiple_valid_expressions_returns_0():
    assert main(["0 * * * * echo", "30 * * * * echo"]) == 0


def test_mixed_valid_invalid_returns_1():
    assert main(["0 * * * * echo", "bad"]) == 1


def test_file_flag_reads_expressions(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("* * * * * echo\n# comment\n\n0 * * * * echo\n")
    assert main(["-f", str(f)]) == 0


def test_file_flag_missing_file_returns_2():
    assert main(["-f", "/nonexistent/path/crons.txt"]) == 2


def test_every_minute_output_contains_balanced(capsys):
    main(["* * * * * echo"])
    captured = capsys.readouterr()
    assert "balanced" in captured.out


def test_output_shows_peak_hour(capsys):
    main(["0 * * * * echo"])
    captured = capsys.readouterr()
    assert "Peak hour" in captured.out


def test_inline_and_file_combined(tmp_path):
    f = tmp_path / "extra.txt"
    f.write_text("0 6 * * * echo\n")
    result = main(["0 * * * * echo", "-f", str(f)])
    assert result == 0
