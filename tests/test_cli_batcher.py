"""Tests for crontab_lint.cli_batcher."""
import pytest

from crontab_lint.cli_batcher import build_parser, main


def test_build_parser_returns_parser():
    from argparse import ArgumentParser
    assert isinstance(build_parser(), ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_single_valid_expression_returns_0():
    assert main(["* * * * * echo hi"]) == 0


def test_single_invalid_expression_returns_1():
    assert main(["bad expression"]) == 1


def test_multiple_valid_expressions_returns_0():
    assert main(["* * * * * echo", "0 12 * * * echo noon"]) == 0


def test_mixed_returns_1():
    assert main(["* * * * * echo", "bad"]) == 1


def test_stop_on_error_flag_accepted():
    assert main(["* * * * * echo", "--stop-on-error"]) == 0


def test_summary_flag_accepted(capsys):
    ret = main(["* * * * * echo", "--summary"])
    out = capsys.readouterr().out
    assert ret == 0
    assert "Total:" in out


def test_file_missing_returns_2(tmp_path):
    missing = str(tmp_path / "nope.txt")
    assert main(["-f", missing]) == 2


def test_file_with_valid_expressions_returns_0(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("* * * * * echo\n0 12 * * * echo noon\n")
    assert main(["-f", str(f)]) == 0


def test_file_with_invalid_expression_returns_1(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("bad expression\n")
    assert main(["-f", str(f)]) == 1


def test_file_skips_comments(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n* * * * * echo\n")
    result = main(["-f", str(f)])
    assert result == 0


def test_file_skips_blank_lines(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("\n* * * * * echo\n\n")
    result = main(["-f", str(f)])
    assert result == 0
