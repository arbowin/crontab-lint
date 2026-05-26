"""Tests for crontab_lint.cli_splitter."""

import pytest
from crontab_lint.cli_splitter import build_parser, main


def test_build_parser_returns_parser():
    import argparse
    assert isinstance(build_parser(), argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["0 * * * * echo hi"]) == 0


def test_invalid_expression_returns_1():
    assert main(["99 * * * * echo hi"]) == 1


def test_multiple_valid_expressions_returns_0():
    assert main(["0 * * * * cmd", "*/5 * * * * cmd"]) == 0


def test_mixed_expressions_returns_1():
    assert main(["0 * * * * cmd", "99 * * * * cmd"]) == 1


def test_file_flag_reads_expressions(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * * echo hi\n*/5 * * * * echo hi\n")
    assert main(["-f", str(f)]) == 0


def test_file_flag_with_comments_skipped(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# a comment\n0 * * * * echo hi\n")
    assert main(["-f", str(f)]) == 0


def test_file_flag_missing_file_returns_2():
    assert main(["-f", "/no/such/file.txt"]) == 2


def test_output_contains_total(capsys):
    main(["0 * * * * cmd"])
    captured = capsys.readouterr()
    assert "Total" in captured.out


def test_output_contains_expression(capsys):
    main(["0 0 * * * cmd"])
    captured = capsys.readouterr()
    assert "0 0 * * * cmd" in captured.out


def test_file_flag_empty_file_returns_2(tmp_path):
    """An empty crontab file should be treated as no input and return exit code 2."""
    f = tmp_path / "empty.txt"
    f.write_text("")
    assert main(["-f", str(f)]) == 2


def test_file_flag_only_comments_returns_2(tmp_path):
    """A file containing only comments (no valid entries) should return exit code 2."""
    f = tmp_path / "comments_only.txt"
    f.write_text("# comment one\n# comment two\n")
    assert main(["-f", str(f)]) == 2
