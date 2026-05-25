"""Tests for crontab_lint.cli_chunker."""

import pytest
from unittest.mock import patch, mock_open
from crontab_lint.cli_chunker import build_parser, main


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["* * * * * echo hi"]) == 0


def test_invalid_expression_returns_0():
    # Invalid expressions are allowed; exit code is still 0 (chunker never returns 1)
    assert main(["not_a_cron"]) == 0


def test_size_flag_accepted():
    assert main(["--size", "5", "* * * * * echo hi"]) == 0


def test_size_zero_returns_2():
    assert main(["--size", "0", "* * * * * echo hi"]) == 2


def test_multiple_expressions_returns_0():
    exprs = ["* * * * * echo hi", "0 * * * * echo hi", "0 0 * * * echo hi"]
    assert main(exprs) == 0


def test_file_flag_reads_expressions(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("* * * * * echo hi\n0 * * * * echo hi\n")
    assert main(["--file", str(f)]) == 0


def test_file_flag_skips_comments(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n* * * * * echo hi\n")
    assert main(["--file", str(f)]) == 0


def test_file_not_found_returns_2():
    assert main(["--file", "/nonexistent/path/crons.txt"]) == 2


def test_output_contains_chunk_label(capsys):
    main(["* * * * * echo hi"])
    captured = capsys.readouterr()
    assert "chunk_1" in captured.out


def test_output_contains_total(capsys):
    main(["* * * * * echo hi", "0 * * * * echo hi"])
    captured = capsys.readouterr()
    assert "Total expressions: 2" in captured.out
