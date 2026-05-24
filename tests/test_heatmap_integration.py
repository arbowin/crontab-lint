"""Integration tests for heatmap combining parser, schedule, and formatting."""
import pytest

from crontab_lint.heatmap import build_heatmap, format_heatmap


_STANDARD_EXPRESSIONS = [
    ("* * * * *", 60),
    ("*/5 * * * *", 12),
    ("0 * * * *", 1),
    ("0 0 * * *", 1),
    ("@hourly", 1),
    ("@daily", 1),
]


@pytest.mark.parametrize("expr,expected_cell", _STANDARD_EXPRESSIONS)
def test_standard_expression_is_valid(expr, expected_cell):
    result = build_heatmap(expr)
    assert result.is_valid, f"{expr!r} should be valid"


@pytest.mark.parametrize("expr,expected_cell", _STANDARD_EXPRESSIONS)
def test_standard_expression_cell_value(expr, expected_cell):
    result = build_heatmap(expr)
    # All days, hour 0 should match expected_cell for expressions that run at hour 0
    assert result.grid[0][0] == expected_cell


def test_weekday_expression_zero_on_off_days():
    # Monday-Friday only (dow 1-5)
    result = build_heatmap("0 9 * * 1-5")
    assert result.grid[1][9] == 1   # Monday 9am
    assert result.grid[5][9] == 1   # Friday 9am
    assert result.grid[0][9] == 0   # Sunday 9am
    assert result.grid[6][9] == 0   # Saturday 9am


def test_format_output_has_24_hour_columns():
    result = build_heatmap("0 * * * *")
    output = format_heatmap(result)
    # Header line should contain hour 0 and hour 23
    assert " 0" in output
    assert "23" in output


def test_invalid_expression_grid_is_all_zeros():
    result = build_heatmap("not valid")
    for row in result.grid:
        assert all(v == 0 for v in row)


def test_list_expression_runs_on_specific_hours():
    result = build_heatmap("0 6,12,18 * * *")
    for dow in range(7):
        assert result.grid[dow][6] == 1
        assert result.grid[dow][12] == 1
        assert result.grid[dow][18] == 1
        assert result.grid[dow][0] == 0
        assert result.grid[dow][9] == 0
