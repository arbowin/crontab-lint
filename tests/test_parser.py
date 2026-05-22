"""Tests for the crontab_lint.parser module."""

import pytest
from crontab_lint.parser import (
    parse,
    ParseError,
    ParsedCron,
    CronField,
    CRONTAB_FIELDS,
)


class TestParseBasicStructure:
    def test_five_field_expression(self):
        result = parse("* * * * *")
        assert isinstance(result, ParsedCron)
        assert len(result.fields) == 5
        assert result.command is None

    def test_field_names_are_correct(self):
        result = parse("* * * * *")
        names = [f.name for f in result.fields]
        assert names == CRONTAB_FIELDS

    def test_command_is_captured(self):
        result = parse("0 5 * * * /usr/bin/backup.sh --quiet")
        assert result.command == "/usr/bin/backup.sh --quiet"

    def test_raw_expression_preserved(self):
        expr = "30 6 * * 1"
        result = parse(expr)
        assert result.raw == expr

    def test_leading_trailing_whitespace_stripped(self):
        result = parse("  * * * * *  ")
        assert len(result.fields) == 5


class TestParseErrors:
    def test_empty_string_raises(self):
        with pytest.raises(ParseError, match="must not be empty"):
            parse("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ParseError, match="must not be empty"):
            parse("   ")

    def test_too_few_fields_raises(self):
        with pytest.raises(ParseError, match="Expected at least 5 fields"):
            parse("* * * *")

    def test_single_field_raises(self):
        with pytest.raises(ParseError):
            parse("*")


class TestAliasNormalization:
    def test_month_name_lowercased(self):
        result = parse("0 0 1 Jan *")
        month_field = next(f for f in result.fields if f.name == "month")
        assert month_field.raw == "1"

    def test_weekday_alias(self):
        result = parse("0 0 * * Mon")
        dow_field = next(f for f in result.fields if f.name == "day_of_week")
        assert dow_field.raw == "1"

    def test_month_dec_alias(self):
        result = parse("0 0 25 Dec *")
        month_field = next(f for f in result.fields if f.name == "month")
        assert month_field.raw == "12"

    def test_weekday_sun_maps_to_zero(self):
        result = parse("0 0 * * Sun")
        dow_field = next(f for f in result.fields if f.name == "day_of_week")
        assert dow_field.raw == "0"


class TestFieldRanges:
    def test_minute_range(self):
        result = parse("* * * * *")
        minute = result.fields[0]
        assert minute.min_val == 0
        assert minute.max_val == 59

    def test_hour_range(self):
        result = parse("* * * * *")
        hour = result.fields[1]
        assert hour.min_val == 0
        assert hour.max_val == 23

    def test_day_of_month_range(self):
        result = parse("* * * * *")
        dom = result.fields[2]
        assert dom.min_val == 1
        assert dom.max_val == 31
