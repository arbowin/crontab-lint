"""Integration tests for the splitter module."""

from crontab_lint.splitter import split, format_split_result

STANDARD = [
    "* * * * * echo every_minute",
    "0 * * * * echo hourly",
    "0 0 * * * echo daily",
    "0 0 * * 0 echo weekly",
    "0 0 1 * * echo monthly",
    "*/5 * * * * echo every_five",
]

INVALID = [
    "99 * * * * echo bad_minute",
    "0 25 * * * echo bad_hour",
    "only_three_fields cmd",
]


def test_all_standard_expressions_are_valid():
    result = split(STANDARD)
    assert result.valid_count == len(STANDARD)
    assert result.invalid_count == 0


def test_all_invalid_expressions_are_invalid():
    result = split(INVALID)
    assert result.invalid_count == len(INVALID)
    assert result.valid_count == 0


def test_mixed_split_counts_are_correct():
    result = split(STANDARD + INVALID)
    assert result.valid_count == len(STANDARD)
    assert result.invalid_count == len(INVALID)
    assert result.total == len(STANDARD) + len(INVALID)


def test_format_output_contains_valid_section():
    result = split(STANDARD[:2])
    output = format_split_result(result)
    assert "Valid expressions" in output


def test_format_output_contains_invalid_section():
    result = split(INVALID[:1])
    output = format_split_result(result)
    assert "Invalid expressions" in output


def test_format_output_contains_all_expressions():
    exprs = ["0 * * * * cmd", "99 * * * * cmd"]
    result = split(exprs)
    output = format_split_result(result)
    for expr in exprs:
        assert expr in output
