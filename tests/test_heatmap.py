"""Tests for crontab_lint.heatmap."""
import pytest

from crontab_lint.heatmap import (
    HeatmapResult,
    build_heatmap,
    format_heatmap,
    DAYS,
)


def test_build_heatmap_returns_heatmap_result():
    result = build_heatmap("0 * * * *")
    assert isinstance(result, HeatmapResult)


def test_build_heatmap_valid_expression_is_valid():
    result = build_heatmap("0 * * * *")
    assert result.is_valid is True


def test_build_heatmap_invalid_expression_is_not_valid():
    result = build_heatmap("not a cron")
    assert result.is_valid is False


def test_build_heatmap_invalid_has_error():
    result = build_heatmap("not a cron")
    assert result.error != ""


def test_build_heatmap_grid_shape():
    result = build_heatmap("0 * * * *")
    assert len(result.grid) == 7
    assert all(len(row) == 24 for row in result.grid)


def test_every_minute_all_cells_nonzero():
    result = build_heatmap("* * * * *")
    for row in result.grid:
        assert all(v > 0 for v in row)


def test_hourly_each_hour_has_one_run():
    result = build_heatmap("0 * * * *")
    for row in result.grid:
        assert all(v == 1 for v in row)


def test_midnight_only_hour_zero():
    result = build_heatmap("0 0 * * *")
    for row in result.grid:
        assert row[0] == 1
        assert all(row[h] == 0 for h in range(1, 24))


def test_weekday_only_runs_on_correct_days():
    # Monday only (dow=1)
    result = build_heatmap("0 0 * * 1")
    assert result.grid[1][0] == 1  # Monday midnight
    assert result.grid[0][0] == 0  # Sunday midnight
    assert result.grid[2][0] == 0  # Tuesday midnight


def test_format_heatmap_contains_expression():
    result = build_heatmap("0 * * * *")
    output = format_heatmap(result)
    assert "0 * * * *" in output


def test_format_heatmap_contains_day_names():
    result = build_heatmap("0 * * * *")
    output = format_heatmap(result)
    for day in DAYS:
        assert day in output


def test_format_heatmap_invalid_shows_error():
    result = build_heatmap("bad")
    output = format_heatmap(result)
    assert "Invalid" in output


def test_format_heatmap_color_flag_accepted():
    result = build_heatmap("* * * * *")
    output = format_heatmap(result, use_color=True)
    # ANSI escape codes should be present for non-zero cells
    assert "\033[" in output


def test_every_minute_runs_per_hour_cell_is_60():
    result = build_heatmap("* * * * *")
    assert result.grid[0][0] == 60


def test_every_five_minutes_cell_is_12():
    result = build_heatmap("*/5 * * * *")
    assert result.grid[0][0] == 12
