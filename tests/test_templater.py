"""Tests for crontab_lint.templater."""

import pytest
from crontab_lint.templater import (
    list_templates,
    get_template,
    search_templates,
    format_template,
    TemplateResult,
)


def test_list_templates_returns_list():
    names = list_templates()
    assert isinstance(names, list)
    assert len(names) > 0


def test_list_templates_includes_known_names():
    names = list_templates()
    assert "every_minute" in names
    assert "every_day" in names
    assert "every_month" in names


def test_get_template_returns_template_result():
    result = get_template("every_minute")
    assert isinstance(result, TemplateResult)


def test_get_template_unknown_returns_none():
    result = get_template("does_not_exist")
    assert result is None


def test_get_template_expression_is_correct():
    result = get_template("every_minute")
    assert result.expression == "* * * * *"


def test_get_template_description_is_set():
    result = get_template("every_hour")
    assert len(result.description) > 0


def test_get_template_lint_result_is_valid():
    result = get_template("every_day")
    assert result.lint_result.valid is True


def test_get_template_name_matches():
    result = get_template("nightly_backup")
    assert result.name == "nightly_backup"


def test_search_templates_by_keyword():
    results = search_templates("hour")
    assert len(results) > 0
    names = [r.name for r in results]
    assert "every_hour" in names


def test_search_templates_no_match_returns_empty():
    results = search_templates("zzznomatch")
    assert results == []


def test_search_templates_case_insensitive():
    results_lower = search_templates("minute")
    results_upper = search_templates("MINUTE")
    assert len(results_lower) == len(results_upper)


def test_search_templates_returns_template_results():
    results = search_templates("week")
    for r in results:
        assert isinstance(r, TemplateResult)


def test_format_template_contains_name():
    tmpl = get_template("every_week")
    output = format_template(tmpl)
    assert "every_week" in output


def test_format_template_contains_expression():
    tmpl = get_template("every_week")
    output = format_template(tmpl)
    assert tmpl.expression in output


def test_format_template_contains_description():
    tmpl = get_template("every_week")
    output = format_template(tmpl)
    assert tmpl.description in output


def test_format_template_contains_explanation():
    tmpl = get_template("every_week")
    output = format_template(tmpl)
    assert "Explanation" in output
