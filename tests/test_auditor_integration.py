"""Integration tests for the auditor module."""

from crontab_lint.auditor import audit, format_audit_report


EXPRESSIONS = [
    "* * * * * /bin/check",
    "0 * * * * /bin/hourly",
    "0 0 * * * /bin/daily",
    "0 0 * * 0 /bin/weekly",
    "0 0 1 * * /bin/monthly",
]


def test_all_standard_expressions_are_valid():
    report = audit(EXPRESSIONS)
    assert report.valid_count == len(EXPRESSIONS)
    assert report.invalid_count == 0


def test_every_minute_gets_high_runs_per_day():
    report = audit(["* * * * * /bin/check"])
    assert report.entries[0].runs_per_day == 1440


def test_hourly_gets_24_runs_per_day():
    report = audit(["0 * * * * /bin/hourly"])
    assert report.entries[0].runs_per_day == 24


def test_daily_gets_1_run_per_day():
    report = audit(["0 0 * * * /bin/daily"])
    assert report.entries[0].runs_per_day == 1


def test_every_minute_tagged_correctly():
    report = audit(["* * * * * /bin/check"])
    assert "every-minute" in report.entries[0].tags


def test_hourly_tagged_correctly():
    report = audit(["0 * * * * /bin/hourly"])
    assert "hourly" in report.entries[0].tags


def test_invalid_expressions_captured():
    report = audit(["99 25 * * * /bad", "* * * *"])
    assert report.invalid_count == 2


def test_format_report_includes_all_expressions():
    report = audit(EXPRESSIONS)
    output = format_audit_report(report)
    for expr in EXPRESSIONS:
        # check the cron part (first 5 fields)
        cron_part = " ".join(expr.split()[:5])
        assert cron_part in output


def test_format_report_summary_counts_correct():
    report = audit(EXPRESSIONS)
    output = format_audit_report(report)
    assert f"{len(EXPRESSIONS)} expression(s)" in output
    assert f"{len(EXPRESSIONS)} valid" in output
