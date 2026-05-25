"""Tests for crontab_lint.digester."""

import pytest
from crontab_lint.digester import digest, DigestResult


def test_digest_returns_digest_result():
    result = digest("* * * * * /bin/true")
    assert isinstance(result, DigestResult)


def test_digest_valid_expression_is_valid():
    result = digest("0 9 * * 1 /bin/job")
    assert result.is_valid is True


def test_digest_invalid_expression_is_not_valid():
    result = digest("99 * * * * /bin/job")
    assert result.is_valid is False


def test_digest_invalid_has_error():
    result = digest("99 * * * * /bin/job")
    assert result.error is not None
    assert len(result.error) > 0


def test_digest_valid_has_no_error():
    result = digest("0 0 * * * /bin/job")
    assert result.error is None


def test_digest_fingerprint_is_string():
    result = digest("* * * * * /bin/true")
    assert isinstance(result.fingerprint, str)
    assert len(result.fingerprint) == 12


def test_digest_fingerprint_is_stable():
    r1 = digest("0 6 * * * /bin/job")
    r2 = digest("0 6 * * * /bin/job")
    assert r1.fingerprint == r2.fingerprint


def test_digest_fingerprint_differs_for_different_expressions():
    r1 = digest("0 6 * * * /bin/job")
    r2 = digest("0 7 * * * /bin/job")
    assert r1.fingerprint != r2.fingerprint


def test_digest_explanation_non_empty_for_valid():
    result = digest("0 0 * * * /bin/job")
    assert len(result.explanation) > 0


def test_digest_explanation_empty_for_invalid():
    result = digest("invalid")
    assert result.explanation == ""


def test_digest_tags_is_list():
    result = digest("* * * * * /bin/true")
    assert isinstance(result.tags, list)


def test_digest_every_minute_has_every_minute_tag():
    result = digest("* * * * * /bin/true")
    assert "every-minute" in result.tags


def test_digest_runs_per_day_none_for_invalid():
    result = digest("bad expression")
    assert result.runs_per_day is None


def test_digest_runs_per_day_positive_for_valid():
    result = digest("* * * * * /bin/true")
    assert result.runs_per_day is not None
    assert result.runs_per_day > 0


def test_digest_fields_dict_has_five_keys():
    result = digest("0 6 * * 1 /bin/job")
    assert len(result.fields) == 5


def test_digest_fields_minute_correct():
    result = digest("30 * * * * /bin/job")
    assert result.fields["minute"] == "30"


def test_digest_to_dict_returns_dict():
    result = digest("0 0 * * * /bin/job")
    d = result.to_dict()
    assert isinstance(d, dict)


def test_digest_to_dict_contains_expected_keys():
    result = digest("0 0 * * * /bin/job")
    d = result.to_dict()
    for key in ("expression", "is_valid", "fingerprint", "explanation",
                "tags", "runs_per_day", "error", "fields"):
        assert key in d
