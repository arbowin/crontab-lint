import pytest
from crontab_lint.slotter import slot, format_slot_result, Slot, SlotResult


def test_slot_returns_slot_result():
    result = slot("* * * * * /cmd")
    assert isinstance(result, SlotResult)


def test_slot_valid_expression_is_valid():
    result = slot("0 * * * * /cmd")
    assert result.is_valid is True
    assert result.error == ""


def test_slot_invalid_expression_is_not_valid():
    result = slot("bad expression")
    assert result.is_valid is False


def test_slot_invalid_has_error():
    result = slot("99 * * * * /cmd")
    assert result.is_valid is False
    assert result.error != ""


def test_slot_default_four_slots():
    result = slot("0 * * * * /cmd")
    assert len(result.slots) == 4


def test_slot_custom_slot_count():
    result = slot("0 * * * * /cmd", n=6)
    assert len(result.slots) == 6


def test_slot_labels_are_strings():
    result = slot("0 * * * * /cmd")
    for s in result.slots:
        assert isinstance(s.label, str)
        assert ":" in s.label


def test_slot_every_minute_total_runs_1440():
    result = slot("* * * * * /cmd")
    assert result.total_runs == 1440


def test_slot_every_minute_even_distribution():
    result = slot("* * * * * /cmd", n=4)
    counts = [s.run_count for s in result.slots]
    assert counts[0] == counts[1] == counts[2] == counts[3]


def test_slot_hourly_total_runs_24():
    result = slot("0 * * * * /cmd")
    assert result.total_runs == 24


def test_slot_hourly_each_slot_has_six_runs():
    result = slot("0 * * * * /cmd", n=4)
    for s in result.slots:
        assert s.run_count == 6


def test_slot_midnight_only_one_run():
    result = slot("0 0 * * * /cmd")
    assert result.total_runs == 1


def test_slot_midnight_first_slot_gets_the_run():
    result = slot("0 0 * * * /cmd", n=4)
    assert result.slots[0].run_count == 1
    assert result.slots[1].run_count == 0


def test_slot_busiest_slot_is_none_for_invalid():
    result = slot("bad")
    assert result.busiest_slot is None


def test_slot_busiest_slot_returned_for_valid():
    result = slot("* * * * * /cmd", n=4)
    assert result.busiest_slot is not None
    assert isinstance(result.busiest_slot, Slot)


def test_slot_n_one_gives_single_slot():
    result = slot("0 * * * * /cmd", n=1)
    assert len(result.slots) == 1
    assert result.slots[0].run_count == 24


def test_slot_to_dict_keys():
    result = slot("0 * * * * /cmd", n=2)
    for s in result.slots:
        d = s.to_dict()
        assert "label" in d
        assert "start_hour" in d
        assert "end_hour" in d
        assert "run_count" in d


def test_format_slot_result_valid():
    result = slot("0 0 * * * /cmd")
    out = format_slot_result(result)
    assert "Expression" in out
    assert "Total runs" in out


def test_format_slot_result_invalid_shows_error():
    result = slot("bad")
    out = format_slot_result(result)
    assert "ERROR" in out


def test_format_slot_result_shows_busiest():
    result = slot("* * * * * /cmd")
    out = format_slot_result(result)
    assert "Busiest" in out
