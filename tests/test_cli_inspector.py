import json
from unittest.mock import patch, mock_open
import pytest
from crontab_lint.cli_inspector import build_parser, main


def test_build_parser_returns_parser():
    from argparse import ArgumentParser
    assert isinstance(build_parser(), ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["* * * * * /bin/true"]) == 0


def test_invalid_expression_returns_1():
    assert main(["not valid"]) == 1


def test_multiple_valid_expressions_returns_0():
    assert main(["0 9 * * * /bin/cmd", "*/15 * * * * /bin/other"]) == 0


def test_mixed_returns_1():
    assert main(["* * * * * /bin/true", "bad expr"]) == 1


def test_json_output_is_valid_json(capsys):
    main(["--json", "* * * * * /bin/true"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert len(data) == 1


def test_json_output_contains_fields(capsys):
    main(["--json", "0 9 * * * /bin/true"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert "fields" in data[0]
    assert len(data[0]["fields"]) == 5


def test_json_invalid_expression(capsys):
    main(["--json", "bad expr"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data[0]["is_valid"] is False
    assert data[0]["error"] is not None


def test_file_flag_reads_expressions(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n\n* * * * * /bin/true\n0 9 * * * /bin/cmd\n")
    assert main(["-f", str(f)]) == 0


def test_file_flag_missing_file_returns_2():
    assert main(["-f", "/nonexistent/path/file.txt"]) == 2


def test_text_output_shows_expression(capsys):
    main(["*/5 * * * * /bin/true"])
    captured = capsys.readouterr()
    assert "*/5 * * * * /bin/true" in captured.out


def test_text_output_shows_field_names(capsys):
    main(["0 9 * * * /bin/true"])
    captured = capsys.readouterr()
    assert "minute" in captured.out
    assert "hour" in captured.out
