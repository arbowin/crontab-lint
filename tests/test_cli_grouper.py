"""Tests for crontab_lint.cli_grouper."""

import textwrap
from pathlib import Path
from unittest.mock import patch

import pytest

from crontab_lint.cli_grouper import build_parser, main


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["0 * * * * cmd"]) == 0


def test_every_minute_groups_correctly(capsys):
    main(["* * * * * cmd"])
    out = capsys.readouterr().out
    assert "every_minute" in out


def test_by_validity_valid(capsys):
    main(["--by", "validity", "0 * * * * cmd"])
    out = capsys.readouterr().out
    assert "valid" in out


def test_by_validity_invalid(capsys):
    main(["--by", "validity", "not a cron"])
    out = capsys.readouterr().out
    assert "invalid" in out


def test_multiple_expressions_grouped(capsys):
    main(["* * * * * a", "0 * * * * b"])
    out = capsys.readouterr().out
    assert "every_minute" in out
    assert "hourly" in out


def test_read_from_file_returns_0(tmp_path: Path, capsys):
    f = tmp_path / "crons.txt"
    f.write_text("0 0 * * * /backup\n# comment\n\n0 * * * * /check\n")
    result = main(["--file", str(f)])
    assert result == 0
    out = capsys.readouterr().out
    assert "daily" in out or "hourly" in out


def test_missing_file_returns_2(tmp_path: Path):
    result = main(["--file", str(tmp_path / "nonexistent.txt")])
    assert result == 2


def test_file_and_inline_combined(tmp_path: Path, capsys):
    f = tmp_path / "crons.txt"
    f.write_text("0 0 * * * /backup\n")
    main(["--file", str(f), "* * * * * cmd"])
    out = capsys.readouterr().out
    assert "every_minute" in out
