"""Tests for crontab_lint.cli_pauser."""

import pytest
from crontab_lint.cli_pauser import build_parser, main


def test_build_parser_returns_parser():
    import argparse
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["0 9 * * *"]) == 0


def test_invalid_expression_returns_1():
    assert main(["not a cron"]) == 1


def test_multiple_valid_expressions_returns_0():
    assert main(["0 9 * * *", "*/5 * * * *"]) == 0


def test_mixed_returns_1():
    assert main(["0 9 * * *", "bad"]) == 1


def test_min_pause_filters_output(capsys):
    main(["* * * * *", "--min-pause", "1"])
    captured = capsys.readouterr()
    # every-minute has no pause, so it should still appear but say "none"
    assert "* * * * *" in captured.out


def test_file_missing_returns_2(tmp_path):
    missing = str(tmp_path / "missing.txt")
    assert main(["-f", missing]) == 2


def test_file_with_valid_expressions_returns_0(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("0 9 * * *\n0 12 * * *\n")
    assert main(["-f", str(f)]) == 0


def test_file_skips_comments(tmp_path):
    f = tmp_path / "crons.txt"
    f.write_text("# a comment\n0 9 * * *\n")
    assert main(["-f", str(f)]) == 0


def test_output_contains_expression(capsys):
    main(["0 0 * * *"])
    out = capsys.readouterr().out
    assert "0 0 * * *" in out


def test_output_contains_longest_pause(capsys):
    main(["0 0 * * *"])
    out = capsys.readouterr().out
    assert "Longest pause" in out
