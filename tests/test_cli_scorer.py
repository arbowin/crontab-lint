"""Tests for crontab_lint.cli_scorer."""

import pytest
from unittest.mock import patch, mock_open
from crontab_lint.cli_scorer import build_parser, main


def test_build_parser_returns_parser():
    import argparse
    parser = build_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_valid_expression_returns_0():
    assert main(["0 0 * * * /bin/backup"]) == 0


def test_invalid_expression_returns_1():
    assert main(["not a cron"]) == 1


def test_out_of_range_returns_1():
    assert main(["99 * * * * /bin/task"]) == 1


def test_min_score_pass():
    # A clean expression should score >= 90, so --min-score 50 should pass
    assert main(["--min-score", "50", "0 6 * * * /bin/report"]) == 0


def test_min_score_fail():
    # Force failure by requiring a perfect score on a penalised expression
    result = main(["--min-score", "100", "1,2,3,4,5,6,7 * * * * /bin/task"])
    assert result == 1


def test_file_option_reads_expressions(tmp_path):
    cron_file = tmp_path / "crons.txt"
    cron_file.write_text("# comment\n\n0 0 * * * /bin/daily\n")
    assert main(["-f", str(cron_file)]) == 0


def test_file_not_found_returns_2():
    assert main(["-f", "/no/such/file.txt"]) == 2


def test_multiple_expressions_all_valid():
    assert main(["0 0 * * * /bin/a", "*/5 * * * * /bin/b"]) == 0


def test_multiple_expressions_one_invalid_returns_1():
    assert main(["0 0 * * * /bin/a", "bad expr"]) == 1
