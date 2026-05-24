"""Tests for crontab_lint.cli_merger."""

import pytest
from unittest.mock import patch, mock_open
from crontab_lint.cli_merger import build_parser, main


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_no_args_returns_2():
    assert main([]) == 2


def test_inline_valid_expression_returns_0():
    assert main(["-e", "0 * * * * echo"]) == 0


def test_inline_invalid_expression_returns_1():
    assert main(["-e", "not a cron"]) == 1


def test_inline_duplicate_expressions_returns_0():
    # duplicates alone don't cause errors
    assert main(["-e", "0 * * * * echo", "-e", "0 * * * * echo"]) == 0


def test_inline_mixed_valid_invalid_returns_1():
    assert main(["-e", "0 * * * * echo", "-e", "bad"]) == 1


def test_file_not_found_returns_2(tmp_path):
    missing = str(tmp_path / "missing.txt")
    assert main([missing]) == 2


def test_file_with_valid_expressions_returns_0(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * * echo\n30 6 * * * backup\n")
    assert main([str(f)]) == 0


def test_file_with_comments_and_blanks_ignored(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n\n0 * * * * echo\n")
    assert main([str(f)]) == 0


def test_output_file_written(tmp_path):
    out = tmp_path / "out.txt"
    rc = main(["-e", "0 * * * * echo", "--output", str(out)])
    assert rc == 0
    assert out.exists()
    content = out.read_text()
    assert "0 * * * * echo" in content


def test_verbose_flag_accepted():
    rc = main(["-v", "-e", "0 * * * * echo"])
    assert rc == 0


def test_shorthand_and_explicit_deduplicated(tmp_path, capsys):
    rc = main(["-e", "@hourly echo", "-e", "0 * * * * echo"])
    captured = capsys.readouterr()
    assert "DUPLICATE" in captured.out
