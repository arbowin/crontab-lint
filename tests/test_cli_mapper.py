"""Tests for crontab_lint.cli_mapper."""
import json
from unittest.mock import patch

import pytest

from crontab_lint.cli_mapper import build_parser, main


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0(capsys):
    assert main(["0 * * * * /bin/true"]) == 0


def test_invalid_expression_returns_1(capsys):
    assert main(["not a cron"]) == 1


def test_multiple_valid_expressions_returns_0(capsys):
    assert main(["0 * * * * /bin/true", "0 0 * * * /bin/true"]) == 0


def test_mixed_valid_invalid_returns_1(capsys):
    assert main(["0 * * * * /bin/true", "bad"]) == 1


def test_output_contains_expression(capsys):
    main(["0 0 * * * /bin/true"])
    captured = capsys.readouterr()
    assert "0 0 * * *" in captured.out


def test_json_flag_returns_json(capsys):
    main(["--json", "0 0 * * * /bin/true"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["is_valid"] is True


def test_json_flag_invalid_expression(capsys):
    main(["--json", "bad cron"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data[0]["is_valid"] is False


def test_file_flag_reads_expressions(tmp_path, capsys):
    f = tmp_path / "crons.txt"
    f.write_text("0 * * * * /bin/true\n0 0 * * * /bin/true\n")
    code = main(["-f", str(f)])
    assert code == 0


def test_file_flag_skips_comments(tmp_path, capsys):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n0 0 * * * /bin/true\n")
    main(["-f", str(f)])
    captured = capsys.readouterr()
    assert "comment" not in captured.out


def test_file_not_found_returns_2(capsys):
    code = main(["-f", "/nonexistent/path.txt"])
    assert code == 2
