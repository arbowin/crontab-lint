"""Tests for crontab_lint.cli_stacker."""

import pytest

from crontab_lint.cli_stacker import build_parser, main


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_no_args_returns_2():
    assert main([]) == 2


def test_single_valid_expression_returns_0():
    assert main(["0 * * * * echo hello"]) == 0


def test_two_non_overlapping_returns_0():
    assert main(["0 * * * * echo a", "30 * * * * echo b"]) == 0


def test_two_overlapping_returns_1():
    assert main(["0 * * * * echo a", "0 * * * * echo b"]) == 1


def test_invalid_expression_returns_1():
    assert main(["not a cron"]) == 1


def test_hours_flag_accepted(capsys):
    code = main(["--hours", "1", "0 * * * * echo a", "30 * * * * echo b"])
    assert code == 0


def test_file_flag_missing_file_returns_2(tmp_path):
    missing = str(tmp_path / "missing.txt")
    assert main(["-f", missing]) == 2


def test_file_flag_reads_expressions(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * * echo a\n30 * * * * echo b\n")
    assert main(["-f", str(f)]) == 0


def test_file_with_overlapping_expressions_returns_1(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * * echo a\n0 * * * * echo b\n")
    assert main(["-f", str(f)]) == 1


def test_file_skips_comments(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# this is a comment\n0 * * * * echo a\n")
    assert main(["-f", str(f)]) == 0


def test_output_contains_expression_count(capsys):
    main(["0 * * * * echo a", "30 * * * * echo b"])
    out = capsys.readouterr().out
    assert "2" in out
