"""Tests for crontab_lint.cli_deduplicator."""
import pytest
from unittest.mock import patch, mock_open
from crontab_lint.cli_deduplicator import build_parser, main


def test_build_parser_returns_parser():
    import argparse
    assert isinstance(build_parser(), argparse.ArgumentParser)


def test_no_args_returns_2():
    with patch("sys.argv", ["crontab-dedup"]):
        result = main([])
    assert result == 2


def test_unique_expressions_returns_0():
    result = main(["0 * * * * echo", "5 * * * * echo"])
    assert result == 0


def test_duplicate_expressions_returns_1():
    result = main(["0 * * * * echo", "0 * * * * echo"])
    assert result == 1


def test_single_expression_returns_0():
    result = main(["* * * * * echo"])
    assert result == 0


def test_unique_only_flag_prints_expressions(capsys):
    main(["--unique-only", "0 * * * * echo", "5 * * * * echo"])
    out = capsys.readouterr().out
    assert "0 * * * * echo" in out
    assert "5 * * * * echo" in out


def test_unique_only_omits_duplicates(capsys):
    main(["--unique-only", "0 * * * * echo", "0 * * * * echo"])
    out = capsys.readouterr().out
    lines = [l for l in out.strip().splitlines() if l]
    assert len(lines) == 1


def test_format_output_contains_totals(capsys):
    main(["0 * * * * echo", "0 * * * * echo"])
    out = capsys.readouterr().out
    assert "Total" in out


def test_file_flag_reads_expressions(tmp_path, capsys):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * * echo\n5 * * * * echo\n")
    result = main(["-f", str(f)])
    assert result == 0


def test_file_flag_detects_duplicates(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * * echo\n0 * * * * echo\n")
    result = main(["-f", str(f)])
    assert result == 1


def test_file_flag_skips_comments(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n0 * * * * echo\n")
    result = main(["-f", str(f)])
    assert result == 0


def test_missing_file_returns_2(tmp_path):
    result = main(["-f", str(tmp_path / "missing.txt")])
    assert result == 2


def test_shorthand_duplicate_detected():
    result = main(["@hourly echo", "0 * * * * echo"])
    assert result == 1
