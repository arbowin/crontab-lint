"""Tests for crontab_lint.ranker."""

import pytest
from crontab_lint.ranker import (
    RankedEntry,
    RankResult,
    rank,
    format_rank_result,
)


def test_rank_returns_rank_result():
    result = rank(["* * * * * echo hi"])
    assert isinstance(result, RankResult)


def test_rank_empty_list():
    result = rank([])
    assert result.entries == []


def test_rank_single_expression_gets_rank_one():
    result = rank(["0 * * * * echo hi"])
    assert len(result.entries) == 1
    assert result.entries[0].rank == 1


def test_rank_frequency_most_frequent_is_first():
    result = rank(
        ["0 0 * * * echo daily", "* * * * * echo every_minute"],
        key="frequency",
    )
    ranked = result.by_rank()
    assert ranked[0].expression == "* * * * * echo every_minute"


def test_rank_frequency_assigns_sequential_ranks():
    result = rank(
        ["0 0 * * * echo a", "0 * * * * echo b", "* * * * * echo c"],
        key="frequency",
    )
    ranks = [e.rank for e in result.by_rank()]
    assert ranks == [1, 2, 3]


def test_rank_complexity_simpler_first():
    result = rank(
        ["0 0 1 1 * echo yearly", "* * * * * echo every_minute"],
        key="complexity",
    )
    ranked = result.by_rank()
    assert ranked[0].expression == "* * * * * echo every_minute"


def test_rank_invalid_key_raises():
    with pytest.raises(ValueError, match="Unknown ranking key"):
        rank(["* * * * * echo hi"], key="bogus")


def test_rank_invalid_expression_is_marked_invalid():
    result = rank(["not a cron"])
    assert result.entries[0].is_valid is False


def test_rank_valid_expression_is_marked_valid():
    result = rank(["0 0 * * * echo hi"])
    assert result.entries[0].is_valid is True


def test_rank_entry_has_runs_per_day():
    result = rank(["* * * * * echo hi"])
    entry = result.entries[0]
    assert isinstance(entry.runs_per_day, float)
    assert entry.runs_per_day > 0


def test_rank_entry_to_dict_keys():
    result = rank(["0 * * * * echo hi"])
    d = result.entries[0].to_dict()
    assert set(d.keys()) == {"rank", "expression", "runs_per_day", "score", "is_valid"}


def test_format_rank_result_empty():
    result = RankResult(entries=[])
    output = format_rank_result(result)
    assert "No expressions" in output


def test_format_rank_result_contains_expression():
    result = rank(["0 0 * * * echo daily"])
    output = format_rank_result(result)
    assert "0 0 * * * echo daily" in output


def test_format_rank_result_contains_header():
    result = rank(["0 0 * * * echo daily"])
    output = format_rank_result(result)
    assert "Rank" in output
    assert "Runs/Day" in output
