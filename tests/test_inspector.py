import pytest
from crontab_lint.inspector import inspect, InspectResult, FieldInspection


def test_inspect_returns_inspect_result():
    result = inspect("* * * * * /bin/true")
    assert isinstance(result, InspectResult)


def test_inspect_valid_expression_is_valid():
    result = inspect("0 9 * * 1 /bin/true")
    assert result.is_valid is True
    assert result.error is None


def test_inspect_invalid_expression_is_not_valid():
    result = inspect("not a cron")
    assert result.is_valid is False
    assert result.error is not None


def test_inspect_out_of_range_is_not_valid():
    result = inspect("99 * * * * /bin/true")
    assert result.is_valid is False


def test_inspect_valid_expression_has_five_fields():
    result = inspect("* * * * * /bin/true")
    assert len(result.fields) == 5


def test_inspect_field_names_are_correct():
    result = inspect("* * * * * /bin/true")
    names = [f.name for f in result.fields]
    assert names == ["minute", "hour", "day_of_month", "month", "day_of_week"]


def test_inspect_wildcard_kind():
    result = inspect("* * * * * /bin/true")
    for f in result.fields:
        assert f.kind == "wildcard"


def test_inspect_value_kind():
    result = inspect("0 9 * * * /bin/true")
    minute_field = result.fields[0]
    assert minute_field.kind == "value"
    assert minute_field.values == [0]


def test_inspect_range_kind():
    result = inspect("0 9-17 * * * /bin/true")
    hour_field = result.fields[1]
    assert hour_field.kind == "range"
    assert hour_field.values == list(range(9, 18))


def test_inspect_step_kind():
    result = inspect("*/15 * * * * /bin/true")
    minute_field = result.fields[0]
    assert minute_field.kind == "step"
    assert minute_field.values == [0, 15, 30, 45]


def test_inspect_list_kind():
    result = inspect("0 6,12,18 * * * /bin/true")
    hour_field = result.fields[1]
    assert hour_field.kind == "list"
    assert hour_field.values == [6, 12, 18]


def test_inspect_wildcard_values_are_empty():
    result = inspect("* * * * * /bin/true")
    for f in result.fields:
        assert f.values == []


def test_inspect_field_has_note():
    result = inspect("0 9 * * * /bin/true")
    for f in result.fields:
        assert isinstance(f.note, str)
        assert len(f.note) > 0


def test_inspect_to_dict_keys():
    result = inspect("* * * * * /bin/true")
    d = result.to_dict()
    assert "expression" in d
    assert "is_valid" in d
    assert "error" in d
    assert "fields" in d


def test_inspect_field_to_dict_keys():
    result = inspect("0 9 * * * /bin/true")
    fd = result.fields[0].to_dict()
    assert set(fd.keys()) == {"name", "raw", "kind", "values", "note"}


def test_inspect_invalid_has_empty_fields():
    result = inspect("bad expression here")
    assert result.fields == []
