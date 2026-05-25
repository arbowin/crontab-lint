"""Tests for crontab_lint.chunker."""

import pytest
from crontab_lint.chunker import Chunk, ChunkResult, chunk, format_chunk_result


def test_chunk_returns_chunk_result():
    result = chunk(["* * * * * echo hi"])
    assert isinstance(result, ChunkResult)


def test_chunk_empty_list_returns_one_empty_chunk():
    result = chunk([])
    assert result.total_expressions == 0
    assert result.has_error is False


def test_chunk_single_valid_expression():
    result = chunk(["* * * * * echo hi"], chunk_size=5)
    assert len(result.chunks) == 1
    assert result.chunks[0].valid_count == 1
    assert result.chunks[0].invalid_count == 0


def test_chunk_single_invalid_expression():
    result = chunk(["not_a_cron"], chunk_size=5)
    assert result.chunks[0].invalid_count == 1
    assert result.chunks[0].valid_count == 0


def test_chunk_splits_into_correct_number_of_chunks():
    exprs = ["* * * * * echo hi"] * 25
    result = chunk(exprs, chunk_size=10)
    assert len(result.chunks) == 3


def test_chunk_last_chunk_may_be_smaller():
    exprs = ["* * * * * echo hi"] * 12
    result = chunk(exprs, chunk_size=10)
    assert len(result.chunks[1].expressions) == 2


def test_chunk_size_zero_returns_error():
    result = chunk(["* * * * * echo hi"], chunk_size=0)
    assert result.has_error is True
    assert "chunk_size" in result.error


def test_chunk_size_negative_returns_error():
    result = chunk(["* * * * * echo hi"], chunk_size=-3)
    assert result.has_error is True


def test_chunk_total_expressions_matches_input():
    exprs = ["* * * * * echo hi"] * 7
    result = chunk(exprs, chunk_size=3)
    assert result.total_expressions == 7


def test_chunk_label_format():
    exprs = ["* * * * * echo hi"] * 3
    result = chunk(exprs, chunk_size=3)
    assert result.chunks[0].label.startswith("chunk_1")


def test_chunk_to_dict_contains_keys():
    result = chunk(["* * * * * echo hi"])
    d = result.to_dict()
    assert "chunks" in d
    assert "total_expressions" in d
    assert "chunk_size" in d


def test_chunk_entry_to_dict():
    result = chunk(["* * * * * echo hi"])
    d = result.chunks[0].to_dict()
    assert "label" in d
    assert "expressions" in d
    assert "valid_count" in d
    assert "invalid_count" in d
    assert "total" in d


def test_format_chunk_result_valid():
    result = chunk(["* * * * * echo hi", "0 * * * * echo hi"])
    text = format_chunk_result(result)
    assert "chunk_1" in text
    assert "2 expressions" in text


def test_format_chunk_result_error():
    result = chunk(["* * * * * echo hi"], chunk_size=0)
    text = format_chunk_result(result)
    assert "Error" in text


def test_chunk_mixed_expressions():
    exprs = ["* * * * * echo hi", "bad", "0 0 * * * echo hi"]
    result = chunk(exprs, chunk_size=10)
    assert result.chunks[0].valid_count == 2
    assert result.chunks[0].invalid_count == 1
