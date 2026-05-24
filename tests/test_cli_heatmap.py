"""Tests for crontab_lint.cli_heatmap."""
import argparse
from unittest.mock import patch, mock_open

import pytest

from crontab_lint.cli_heatmap import build_parser, main, _read_file


def test_build_parser_returns_parser():
    assert isinstance(build_parser(), argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["0 * * * *"]) == 0


def test_invalid_expression_returns_1():
    assert main(["not valid"]) == 1


def test_multiple_expressions_all_valid_returns_0():
    assert main(["0 * * * *", "*/5 * * * *"]) == 0


def test_mixed_valid_invalid_returns_1():
    assert main(["0 * * * *", "bad expr"]) == 1


def test_read_file_skips_comments(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n0 * * * *\n")
    result = _read_file(str(f))
    assert result == ["0 * * * *"]


def test_read_file_skips_blank_lines(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("\n0 * * * *\n\n")
    result = _read_file(str(f))
    assert result == ["0 * * * *"]


def test_file_flag_reads_expressions(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * *\n")
    assert main(["-f", str(f)]) == 0


def test_missing_file_returns_2():
    assert main(["-f", "/nonexistent/path/file.txt"]) == 2


def test_color_flag_accepted():
    assert main(["--color", "* * * * *"]) == 0
