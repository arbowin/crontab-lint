"""Tests for crontab_lint.cli_sampler."""

import pytest
from crontab_lint.cli_sampler import build_parser, main


def test_build_parser_returns_parser():
    parser = build_parser()
    assert parser is not None


def test_no_args_uses_defaults():
    parser = build_parser()
    args = parser.parse_args([])
    assert args.count == 5
    assert args.tag is None
    assert args.seed is None
    assert args.plain is False


def test_count_flag():
    parser = build_parser()
    args = parser.parse_args(["-n", "3"])
    assert args.count == 3


def test_tag_flag():
    parser = build_parser()
    args = parser.parse_args(["-t", "hourly"])
    assert args.tag == "hourly"


def test_seed_flag():
    parser = build_parser()
    args = parser.parse_args(["--seed", "42"])
    assert args.seed == 42


def test_plain_flag():
    parser = build_parser()
    args = parser.parse_args(["--plain"])
    assert args.plain is True


def test_main_default_returns_0():
    code = main(["--seed", "1"])
    assert code == 0


def test_main_count_three_returns_0():
    code = main(["-n", "3", "--seed", "2"])
    assert code == 0


def test_main_invalid_count_returns_2():
    code = main(["-n", "0"])
    assert code == 2


def test_main_plain_output(capsys):
    code = main(["-n", "3", "--seed", "7", "--plain"])
    captured = capsys.readouterr()
    lines = [l for l in captured.out.strip().splitlines() if l]
    assert len(lines) == 3
    assert code == 0


def test_main_no_match_tag_returns_1():
    code = main(["-t", "nonexistent_tag_xyz", "--seed", "0"])
    assert code == 1


def test_main_reproducible_with_seed(capsys):
    main(["--seed", "99", "--plain"])
    out1 = capsys.readouterr().out
    main(["--seed", "99", "--plain"])
    out2 = capsys.readouterr().out
    assert out1 == out2


def test_main_formatted_output_contains_header(capsys):
    main(["--seed", "5"])
    out = capsys.readouterr().out
    assert "Sampled" in out
