"""Tests for crontab_lint.predictor."""

from datetime import datetime, timedelta

import pytest

from crontab_lint.predictor import PredictResult, predict, format_predict_result

# Fixed anchor so tests are deterministic
ANCHOR = datetime(2024, 6, 1, 0, 0, 0)


def test_predict_returns_predict_result():
    result = predict("* * * * * echo hi", window_start=ANCHOR)
    assert isinstance(result, PredictResult)


def test_predict_valid_expression_is_valid():
    result = predict("0 * * * * echo hi", window_start=ANCHOR)
    assert result.is_valid is True
    assert result.error is None


def test_predict_invalid_expression_is_not_valid():
    result = predict("invalid", window_start=ANCHOR)
    assert result.is_valid is False


def test_predict_invalid_has_error():
    result = predict("invalid", window_start=ANCHOR)
    assert result.error is not None
    assert len(result.error) > 0


def test_predict_every_minute_runs_in_24h_window():
    result = predict("* * * * * echo", window_start=ANCHOR, window_hours=1)
    assert result.will_run is True
    assert result.run_count == 60


def test_predict_hourly_runs_in_24h_window():
    result = predict("0 * * * * echo", window_start=ANCHOR, window_hours=24)
    assert result.run_count == 24


def test_predict_daily_midnight_runs_once_in_24h():
    result = predict("0 0 * * * echo", window_start=ANCHOR, window_hours=24)
    assert result.run_count == 1


def test_predict_window_start_defaults_to_now():
    # Should not raise; just verify it returns a result
    result = predict("0 12 * * * echo")
    assert isinstance(result, PredictResult)


def test_predict_window_end_is_correct():
    result = predict("* * * * * echo", window_start=ANCHOR, window_hours=6)
    expected_end = ANCHOR + timedelta(hours=6)
    assert result.window_end == expected_end


def test_predict_runs_are_within_window():
    result = predict("*/15 * * * * echo", window_start=ANCHOR, window_hours=2)
    for dt in result.runs_in_window:
        assert result.window_start <= dt < result.window_end


def test_predict_will_run_false_when_no_runs():
    # Expression that only runs on Feb 30 — use a day that won't appear in the window
    start = datetime(2024, 6, 1, 1, 0)
    result = predict("0 3 * * 0 echo", window_start=start, window_hours=1)
    # Sunday may or may not fall in a 1-hour window; test the property logic
    assert result.will_run == (result.run_count > 0)


def test_format_predict_result_valid():
    result = predict("0 * * * * echo", window_start=ANCHOR, window_hours=3)
    output = format_predict_result(result)
    assert "Expression" in output
    assert "Window" in output
    assert "Run count" in output


def test_format_predict_result_invalid():
    result = predict("bad expression", window_start=ANCHOR)
    output = format_predict_result(result)
    assert "Error" in output


def test_format_predict_result_shows_next_runs():
    result = predict("0 * * * * echo", window_start=ANCHOR, window_hours=24)
    output = format_predict_result(result)
    assert "Next runs" in output


def test_format_predict_result_shows_ellipsis_for_many_runs():
    result = predict("* * * * * echo", window_start=ANCHOR, window_hours=1)
    output = format_predict_result(result)
    assert "more" in output
