"""Integration tests for grouper: realistic multi-expression scenarios."""

from crontab_lint.grouper import group, format_group_result, has_group


SAMPLE_CRONS = [
    "* * * * * /usr/bin/check",
    "0 * * * * /usr/bin/hourly_job",
    "0 0 * * * /usr/bin/daily_backup",
    "0 0 * * 0 /usr/bin/weekly_report",
    "0 0 1 * * /usr/bin/monthly_invoice",
    "0 0 1 1 * /usr/bin/yearly_audit",
]


def test_all_standard_groups_present():
    result = group(SAMPLE_CRONS, by="tag")
    for expected in ["every_minute", "hourly", "daily", "weekly", "monthly", "yearly"]:
        assert has_group(result, expected), f"Missing group: {expected}"


def test_no_ungrouped_for_valid_expressions():
    result = group(SAMPLE_CRONS, by="tag")
    assert result.ungrouped == []


def test_validity_grouping_all_valid():
    result = group(SAMPLE_CRONS, by="validity")
    assert has_group(result, "valid")
    assert len(result.members("valid")) == len(SAMPLE_CRONS)
    assert not has_group(result, "invalid")


def test_validity_grouping_mixed():
    mixed = SAMPLE_CRONS + ["bad expression", "also bad"]
    result = group(mixed, by="validity")
    assert len(result.members("valid")) == len(SAMPLE_CRONS)
    assert len(result.members("invalid")) == 2


def test_format_output_contains_all_groups():
    result = group(SAMPLE_CRONS, by="tag")
    output = format_group_result(result)
    for expr in SAMPLE_CRONS:
        assert expr in output


def test_format_shows_member_counts():
    exprs = ["* * * * * a", "* * * * * b"]
    result = group(exprs, by="tag")
    output = format_group_result(result)
    assert "2 expression" in output
