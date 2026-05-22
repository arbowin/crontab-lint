"""Tests for the CLI entry point."""

import textwrap
from unittest.mock import patch

import pytest

from crontab_lint.cli import main, read_expressions_from_file


# ---------------------------------------------------------------------------
# read_expressions_from_file
# ---------------------------------------------------------------------------

def test_read_expressions_skips_comments(tmp_path):
    crontab = tmp_path / "crontab"
    crontab.write_text(
        textwrap.dedent("""\
            # this is a comment
            */5 * * * * /usr/bin/task
            0 12 * * * /usr/bin/other
        """)
    )
    lines = read_expressions_from_file(str(crontab))
    assert lines == ["*/5 * * * * /usr/bin/task", "0 12 * * * /usr/bin/other"]


def test_read_expressions_skips_blank_lines(tmp_path):
    crontab = tmp_path / "crontab"
    crontab.write_text("*/5 * * * * /cmd\n\n0 0 * * * /other\n")
    lines = read_expressions_from_file(str(crontab))
    assert len(lines) == 2


# ---------------------------------------------------------------------------
# main() exit codes
# ---------------------------------------------------------------------------

def test_main_no_args_returns_2():
    assert main([]) == 2


def test_main_valid_expression_returns_0():
    assert main(["*/5 * * * * /usr/bin/task"]) == 0


def test_main_invalid_expression_returns_1():
    assert main(["99 * * * * /bad"]) == 1


def test_main_multiple_all_valid_returns_0():
    assert main(["0 * * * * /a", "*/10 * * * * /b"]) == 0


def test_main_multiple_one_invalid_returns_1():
    assert main(["0 * * * * /a", "99 * * * * /bad"]) == 1


def test_main_file_valid(tmp_path):
    crontab = tmp_path / "crontab"
    crontab.write_text("0 12 * * * /usr/bin/backup\n")
    assert main(["-f", str(crontab)]) == 0


def test_main_file_not_found_returns_2():
    assert main(["-f", "/nonexistent/path/crontab.txt"]) == 2


def test_main_verbose_flag_accepted():
    assert main(["--verbose", "0 0 * * * /cmd"]) == 0


def test_main_output_contains_expression(capsys):
    main(["0 12 * * * /usr/bin/backup"])
    captured = capsys.readouterr()
    assert "0 12 * * * /usr/bin/backup" in captured.out


def test_main_invalid_output_contains_error(capsys):
    main(["99 * * * * /bad"])
    captured = capsys.readouterr()
    assert "error" in captured.out.lower() or "ERROR" in captured.out
