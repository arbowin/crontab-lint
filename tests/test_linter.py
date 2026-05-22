import pytest
from crontab_lint.linter import lint, lint_many, LintResult


def test_lint_returns_lint_result():
    result = lint('*/5 * * * * /bin/task')
    assert isinstance(result, LintResult)


def test_lint_valid_expression():
    result = lint('0 9 * * 1 /usr/bin/report')
    assert result.valid is True
    assert result.command == '/usr/bin/report'
    assert result.explanation is not None


def test_lint_invalid_expression_too_few_fields():
    result = lint('* * * *')
    assert result.valid is False
    assert result.explanation is None


def test_lint_out_of_range_minute():
    result = lint('99 * * * * /bin/task')
    assert result.valid is False
    assert result.validation.has_errors()


def test_lint_warning_both_dom_and_dow():
    result = lint('0 0 1 * 1 /bin/task')
    assert result.valid is True
    assert result.validation.has_warnings()


def test_summary_contains_valid_marker():
    result = lint('*/10 * * * * /bin/task')
    summary = result.summary()
    assert '✓ valid' in summary


def test_summary_contains_invalid_marker():
    result = lint('60 * * * * /bin/task')
    summary = result.summary()
    assert '✗ invalid' in summary


def test_summary_contains_schedule():
    result = lint('0 * * * * /bin/task')
    summary = result.summary()
    assert 'Schedule:' in summary


def test_summary_contains_command():
    result = lint('0 0 * * * /bin/backup')
    summary = result.summary()
    assert '/bin/backup' in summary


def test_summary_contains_issue_details():
    result = lint('99 * * * * /bin/task')
    summary = result.summary()
    assert 'Issues:' in summary
    assert 'minute' in summary


def test_lint_many_returns_list():
    exprs = ['*/5 * * * * /bin/a', '0 0 * * * /bin/b']
    results = lint_many(exprs)
    assert len(results) == 2
    assert all(isinstance(r, LintResult) for r in results)


def test_lint_many_mixed_validity():
    exprs = ['*/5 * * * * /bin/a', '99 * * * * /bin/b']
    results = lint_many(exprs)
    assert results[0].valid is True
    assert results[1].valid is False
