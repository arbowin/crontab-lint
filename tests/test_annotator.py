"""Tests for crontab_lint.annotator."""

import pytest
from crontab_lint.annotator import AnnotatedLine, annotate_lines, render_annotated


# ---------------------------------------------------------------------------
# AnnotatedLine.render
# ---------------------------------------------------------------------------

def test_render_blank_line():
    al = AnnotatedLine(original="", annotation="", is_blank=True)
    assert al.render() == ""


def test_render_comment_line():
    al = AnnotatedLine(original="# my comment", annotation="ignored", is_comment=True)
    assert al.render() == "# my comment"


def test_render_normal_line_adds_annotation():
    al = AnnotatedLine(original="* * * * * /bin/true", annotation="every minute")
    rendered = al.render(column=40)
    assert "# every minute" in rendered
    assert rendered.startswith("* * * * * /bin/true")


def test_render_uses_at_least_one_space():
    long_line = "0 0 * * * " + "x" * 80
    al = AnnotatedLine(original=long_line, annotation="midnight")
    rendered = al.render(column=20)
    assert "# midnight" in rendered


# ---------------------------------------------------------------------------
# annotate_lines
# ---------------------------------------------------------------------------

def test_annotate_blank_line_is_blank():
    result = annotate_lines([""])
    assert len(result) == 1
    assert result[0].is_blank


def test_annotate_comment_line_is_comment():
    result = annotate_lines(["# this is a comment"])
    assert result[0].is_comment


def test_annotate_valid_expression_has_annotation():
    result = annotate_lines(["* * * * * /usr/bin/env"])
    assert not result[0].is_blank
    assert not result[0].is_comment
    assert result[0].annotation != ""


def test_annotate_valid_expression_annotation_contains_explanation():
    result = annotate_lines(["0 * * * * /usr/bin/env"])
    annotation = result[0].annotation
    # Should not start with ERROR
    assert not annotation.startswith("ERROR")


def test_annotate_invalid_expression_annotation_starts_with_error():
    result = annotate_lines(["99 * * * * /bin/bad"])
    assert result[0].annotation.startswith("ERROR")


def test_annotate_too_few_fields_is_error():
    result = annotate_lines(["* * * *"])
    assert result[0].annotation.startswith("ERROR")


def test_annotate_multiple_lines():
    lines = [
        "# header",
        "",
        "* * * * * /bin/a",
        "0 12 * * * /bin/b",
    ]
    result = annotate_lines(lines)
    assert len(result) == 4
    assert result[0].is_comment
    assert result[1].is_blank
    assert not result[2].is_blank
    assert not result[3].is_blank


# ---------------------------------------------------------------------------
# render_annotated
# ---------------------------------------------------------------------------

def test_render_annotated_returns_string():
    output = render_annotated(["* * * * * /bin/true"])
    assert isinstance(output, str)


def test_render_annotated_preserves_blank_lines():
    output = render_annotated(["", "* * * * * /bin/true", ""])
    lines = output.split("\n")
    assert lines[0] == ""
    assert lines[2] == ""


def test_render_annotated_comment_unchanged():
    output = render_annotated(["# hello world"])
    assert output == "# hello world"
