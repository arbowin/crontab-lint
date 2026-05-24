"""Tests for crontab_lint.cli_snapshotter."""

import json
import pytest

from crontab_lint.cli_snapshotter import build_parser, main
from crontab_lint.snapshotter import take_snapshot, save_snapshot


def test_build_parser_returns_parser():
    from argparse import ArgumentParser
    assert isinstance(build_parser(), ArgumentParser)


def test_no_args_returns_2():
    assert main([]) == 2


def test_take_subcommand_no_output_returns_error():
    with pytest.raises(SystemExit):
        main(["take", "* * * * * x"])


def test_take_valid_expression_returns_0(tmp_path):
    out = str(tmp_path / "snap.json")
    result = main(["take", "* * * * * echo hi", "--output", out])
    assert result == 0


def test_take_invalid_expression_returns_1(tmp_path):
    out = str(tmp_path / "snap.json")
    result = main(["take", "99 99 99 99 99 bad", "--output", out])
    assert result == 1


def test_take_creates_json_file(tmp_path):
    out = str(tmp_path / "snap.json")
    main(["take", "0 0 * * * x", "--output", out])
    with open(out) as fh:
        data = json.load(fh)
    assert "entries" in data
    assert "timestamp" in data


def test_diff_no_changes_returns_0(tmp_path):
    snap = take_snapshot(["* * * * * x"])
    p1 = str(tmp_path / "a.json")
    p2 = str(tmp_path / "b.json")
    save_snapshot(snap, p1)
    save_snapshot(snap, p2)
    assert main(["diff", p1, p2]) == 0


def test_diff_with_changes_returns_1(tmp_path):
    old = take_snapshot(["* * * * * x"])
    new = take_snapshot(["* * * * * x", "0 0 * * * y"])
    p1 = str(tmp_path / "old.json")
    p2 = str(tmp_path / "new.json")
    save_snapshot(old, p1)
    save_snapshot(new, p2)
    assert main(["diff", p1, p2]) == 1


def test_diff_missing_old_returns_2(tmp_path):
    new = take_snapshot(["* * * * * x"])
    p2 = str(tmp_path / "new.json")
    save_snapshot(new, p2)
    result = main(["diff", str(tmp_path / "missing.json"), p2])
    assert result == 2


def test_diff_missing_new_returns_2(tmp_path):
    old = take_snapshot(["* * * * * x"])
    p1 = str(tmp_path / "old.json")
    save_snapshot(old, p1)
    result = main(["diff", p1, str(tmp_path / "missing.json")])
    assert result == 2
