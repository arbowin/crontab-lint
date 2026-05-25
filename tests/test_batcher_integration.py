"""Integration tests for crontab_lint.batcher."""
from crontab_lint.batcher import batch, format_batch_result

STANDARD_EXPRESSIONS = [
    "* * * * * echo every-minute",
    "0 * * * * echo hourly",
    "0 0 * * * echo daily",
    "0 0 * * 0 echo weekly",
    "0 0 1 * * echo monthly",
    "30 6 * * 1-5 echo weekdays",
]


def test_all_standard_expressions_are_valid():
    result = batch(STANDARD_EXPRESSIONS)
    assert result.valid_count == len(STANDARD_EXPRESSIONS)


def test_invalid_does_not_affect_valid_count():
    exprs = STANDARD_EXPRESSIONS + ["not a cron"]
    result = batch(exprs)
    assert result.valid_count == len(STANDARD_EXPRESSIONS)
    assert result.invalid_count == 1


def test_stop_on_error_stops_early():
    exprs = ["bad"] + STANDARD_EXPRESSIONS
    result = batch(exprs, stop_on_error=True)
    assert result.total == 1


def test_format_output_contains_all_expressions():
    result = batch(STANDARD_EXPRESSIONS)
    output = format_batch_result(result)
    for expr in STANDARD_EXPRESSIONS:
        assert expr in output


def test_entry_to_dict_valid_expression():
    result = batch(["0 0 * * * echo daily"])
    d = result.entries[0].to_dict()
    assert d["valid"] is True
    assert d["error_count"] == 0


def test_entry_to_dict_invalid_expression():
    result = batch(["bad"])
    d = result.entries[0].to_dict()
    assert d["valid"] is False
    assert d["error_count"] >= 1
