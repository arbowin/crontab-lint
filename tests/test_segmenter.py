import pytest
from crontab_lint.segmenter import segment, format_segment_result, Segment, SegmentResult


def test_segment_returns_segment_result():
    result = segment("* * * * * /bin/true")
    assert isinstance(result, SegmentResult)


def test_segment_valid_expression_is_valid():
    result = segment("0 * * * * /bin/true")
    assert result.is_valid is True
    assert result.error is None


def test_segment_invalid_expression_is_not_valid():
    result = segment("bad expression")
    assert result.is_valid is False
    assert result.error is not None


def test_segment_invalid_has_no_segments():
    result = segment("99 99 99 99 99 /x")
    assert result.is_valid is False
    assert result.segments == []


def test_segment_always_returns_four_segments():
    result = segment("0 * * * * /bin/true")
    assert len(result.segments) == 4


def test_segment_labels_are_correct():
    result = segment("0 * * * * /bin/true")
    labels = [s.label for s in result.segments]
    assert labels == ["night", "morning", "afternoon", "evening"]


def test_segment_hour_ranges_are_correct():
    result = segment("0 * * * * /bin/true")
    assert result.segments[0].hour_start == 0
    assert result.segments[0].hour_end == 6
    assert result.segments[3].hour_start == 18
    assert result.segments[3].hour_end == 24


def test_segment_every_minute_total_is_1440():
    result = segment("* * * * * /bin/true")
    assert result.total_runs() == 1440


def test_segment_every_minute_each_band_proportional():
    result = segment("* * * * * /bin/true")
    # Each 6-hour band has 6*60=360 runs
    for seg in result.segments:
        assert seg.run_count == 360


def test_segment_hourly_total_is_24():
    result = segment("0 * * * * /bin/true")
    assert result.total_runs() == 24


def test_segment_daily_midnight_total_is_1():
    result = segment("0 0 * * * /bin/true")
    assert result.total_runs() == 1


def test_segment_daily_midnight_in_night_band():
    result = segment("0 0 * * * /bin/true")
    night = next(s for s in result.segments if s.label == "night")
    assert night.run_count == 1


def test_segment_business_hours_only_in_morning_afternoon():
    # 9-17 falls in morning (6-12) and afternoon (12-18)
    result = segment("0 9-17 * * * /bin/true")
    night = next(s for s in result.segments if s.label == "night")
    evening = next(s for s in result.segments if s.label == "evening")
    assert night.run_count == 0
    assert evening.run_count == 0


def test_segment_busiest_returns_segment():
    result = segment("* * * * * /bin/true")
    busiest = result.busiest_segment()
    assert isinstance(busiest, Segment)


def test_segment_busiest_is_none_for_invalid():
    result = segment("bad")
    assert result.busiest_segment() is None


def test_segment_to_dict_has_keys():
    result = segment("0 * * * * /bin/true")
    d = result.segments[0].to_dict()
    assert "label" in d
    assert "hour_start" in d
    assert "hour_end" in d
    assert "run_count" in d


def test_format_segment_result_valid_contains_labels():
    result = segment("0 * * * * /bin/true")
    text = format_segment_result(result)
    assert "morning" in text
    assert "night" in text


def test_format_segment_result_invalid_shows_error():
    result = segment("bad")
    text = format_segment_result(result)
    assert "Error" in text


def test_format_segment_result_shows_total():
    result = segment("* * * * * /bin/true")
    text = format_segment_result(result)
    assert "TOTAL" in text
    assert "1440" in text
