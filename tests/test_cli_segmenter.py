import json
import pytest
from crontab_lint.cli_segmenter import build_parser, main


def test_build_parser_returns_parser():
    from argparse import ArgumentParser
    assert isinstance(build_parser(), ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["0 * * * * /bin/true"]) == 0


def test_invalid_expression_returns_1():
    assert main(["bad expression"]) == 1


def test_multiple_valid_returns_0():
    assert main(["0 * * * * /x", "*/5 * * * * /y"]) == 0


def test_mixed_returns_1():
    assert main(["0 * * * * /x", "bad"]) == 1


def test_json_flag_returns_0_for_valid(capsys):
    code = main(["--json", "0 * * * * /bin/true"])
    assert code == 0
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert isinstance(data, list)
    assert data[0]["is_valid"] is True


def test_json_flag_has_segments(capsys):
    main(["--json", "0 * * * * /bin/true"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert len(data[0]["segments"]) == 4


def test_json_flag_invalid_expression(capsys):
    code = main(["--json", "bad"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data[0]["is_valid"] is False
    assert data[0]["error"] is not None


def test_json_total_runs_every_minute(capsys):
    main(["--json", "* * * * * /bin/true"])
    captured = capsys.readouterr()
    data = json.loads(captured.out)
    assert data[0]["total_runs"] == 1440


def test_file_flag_reads_expressions(tmp_path, capsys):
    f = tmp_path / "crons.txt"
    f.write_text("# comment\n\n0 * * * * /bin/true\n*/10 * * * * /bin/check\n")
    code = main(["--file", str(f)])
    assert code == 0


def test_file_flag_missing_file_returns_2():
    code = main(["--file", "/nonexistent/path/file.txt"])
    assert code == 2


def test_output_contains_segment_labels(capsys):
    main(["0 * * * * /bin/true"])
    captured = capsys.readouterr()
    assert "morning" in captured.out
    assert "night" in captured.out


def test_output_contains_total(capsys):
    main(["* * * * * /bin/true"])
    captured = capsys.readouterr()
    assert "TOTAL" in captured.out
