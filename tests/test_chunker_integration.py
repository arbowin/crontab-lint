"""Integration tests for the chunker module."""

import pytest
from crontab_lint.chunker import chunk, format_chunk_result

STANDARD_EXPRESSIONS = [
    "* * * * * echo every_minute",
    "0 * * * * echo hourly",
    "0 0 * * * echo daily",
    "0 0 * * 0 echo weekly",
    "0 0 1 * * echo monthly",
    "0 0 1 1 * echo yearly",
    "*/5 * * * * echo every_five",
    "0 9-17 * * 1-5 echo business_hours",
]


def test_all_standard_expressions_chunked_as_valid():
    result = chunk(STANDARD_EXPRESSIONS, chunk_size=4)
    for c in result.chunks:
        assert c.invalid_count == 0


def test_chunk_count_correct_for_standard():
    result = chunk(STANDARD_EXPRESSIONS, chunk_size=4)
    assert len(result.chunks) == 2


def test_each_chunk_has_four_expressions():
    result = chunk(STANDARD_EXPRESSIONS, chunk_size=4)
    for c in result.chunks:
        assert len(c.expressions) == 4


def test_format_output_has_all_chunk_labels():
    result = chunk(STANDARD_EXPRESSIONS, chunk_size=4)
    text = format_chunk_result(result)
    assert "chunk_1" in text
    assert "chunk_2" in text


def test_invalid_expressions_counted_correctly():
    exprs = STANDARD_EXPRESSIONS + ["bad_expr", "also_bad"]
    result = chunk(exprs, chunk_size=5)
    total_invalid = sum(c.invalid_count for c in result.chunks)
    assert total_invalid == 2


def test_total_expressions_matches():
    result = chunk(STANDARD_EXPRESSIONS, chunk_size=3)
    assert result.total_expressions == len(STANDARD_EXPRESSIONS)
