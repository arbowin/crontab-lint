"""Integration tests for the digester module."""

import pytest
from crontab_lint.digester import digest

STANDARD_EXPRESSIONS = [
    "* * * * * /bin/true",
    "0 * * * * /bin/hourly",
    "0 0 * * * /bin/daily",
    "0 0 * * 0 /bin/weekly",
    "0 0 1 * * /bin/monthly",
    "*/5 * * * * /bin/every5",
    "0 9-17 * * 1-5 /bin/workday",
]


def test_all_standard_expressions_valid():
    for expr in STANDARD_EXPRESSIONS:
        r = digest(expr)
        assert r.is_valid, f"{expr!r} should be valid"


def test_all_standard_expressions_have_fingerprint():
    for expr in STANDARD_EXPRESSIONS:
        r = digest(expr)
        assert len(r.fingerprint) == 12


def test_all_fingerprints_are_unique():
    fingerprints = [digest(e).fingerprint for e in STANDARD_EXPRESSIONS]
    assert len(fingerprints) == len(set(fingerprints))


def test_every_minute_runs_per_day_is_1440():
    r = digest("* * * * * /bin/true")
    assert r.runs_per_day == 1440


def test_hourly_runs_per_day_is_24():
    r = digest("0 * * * * /bin/hourly")
    assert r.runs_per_day == 24


def test_daily_runs_per_day_is_1():
    r = digest("0 0 * * * /bin/daily")
    assert r.runs_per_day == 1


def test_fields_captured_correctly():
    r = digest("30 6 1 3 5 /bin/job")
    assert r.fields["minute"] == "30"
    assert r.fields["hour"] == "6"
    assert r.fields["day_of_month"] == "1"
    assert r.fields["month"] == "3"
    assert r.fields["day_of_week"] == "5"


def test_to_dict_roundtrip_preserves_expression():
    expr = "0 12 * * 1-5 /bin/job"
    r = digest(expr)
    d = r.to_dict()
    assert d["expression"] == expr
