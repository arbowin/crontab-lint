"""Tests for crontab_lint.cli_resolver."""

from unittest.mock import mock_open, patch

import pytest

from crontab_lint.cli_resolver import build_parser, main


def test_build_parser_returns_parser():
    import argparse
    assert isinstance(build_parser(), argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    code = main(["0 * * * * echo hi"])
    assert code == 0


def test_invalid_expression_returns_1():
    code = main(["99 * * * * echo hi"])
    assert code == 1


def test_multiple_valid_expressions_returns_0():
    code = main(["0 * * * * echo hi", "30 6 * * 1-5 echo hi"])
    assert code == 0


def test_mixed_valid_invalid_returns_1():
    code = main(["0 * * * * echo hi", "bad expr"])
    assert code == 1


def test_count_flag_respected(capsys):
    main(["-n", "2", "* * * * * echo hi"])
    captured = capsys.readouterr()
    # Expect exactly 2 numbered runs
    assert "  1." in captured.out
    assert "  2." in captured.out
    assert "  3." not in captured.out


def test_shorthand_expression_returns_0():
    assert main(["@daily echo hi"]) == 0


def test_file_flag_valid(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * * echo hi\n# comment\n\n30 6 * * 1 echo hi\n")
    assert main(["-f", str(f)]) == 0


def test_file_flag_missing_file_returns_2():
    assert main(["-f", "/nonexistent/path/crons.txt"]) == 2


def test_format_flag_changes_output(capsys):
    main(["--format", "%d/%m/%Y", "-n", "1", "0 0 * * * echo hi"])
    captured = capsys.readouterr()
    assert "/" in captured.out
