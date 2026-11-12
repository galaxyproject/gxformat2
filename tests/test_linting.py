"""Unit tests for gxformat2.linting primitives."""

import pytest

from gxformat2.linting import (
    LintContext,
    Linter,
    LintLevel,
    LintMessage,
)


class _FakeRule(Linter):
    severity = "warning"
    applies_to = ("native",)
    profile = "structural"


def test_lint_message_is_str():
    msg = LintMessage("hello", level=LintLevel.ERROR, linter="R", json_pointer="/x")
    assert isinstance(msg, str)
    assert msg == "hello"
    assert "ell" in msg
    assert msg.level == LintLevel.ERROR
    assert msg.linter == "R"
    assert msg.json_pointer == "/x"


def test_context_records_metadata():
    ctx = LintContext()
    ctx.error("bad {value}", value="x", linter=_FakeRule, json_pointer="/steps/0")
    assert len(ctx.error_messages) == 1
    msg = ctx.error_messages[0]
    assert msg == "bad x"
    assert msg.linter == "_FakeRule"
    assert msg.json_pointer == "/steps/0"
    assert msg.level == LintLevel.ERROR


def test_child_composes_pointer():
    ctx = LintContext()
    child = ctx.child("steps").child(0)
    child.warn("disconnected")
    assert ctx.warn_messages[0].json_pointer == "/steps/0"
    assert ctx.warn_messages[0].level == LintLevel.WARN


def test_child_escapes_pointer_segment():
    ctx = LintContext()
    ctx.child("a/b~c").warn("x")
    assert ctx.warn_messages[0].json_pointer == "/a~1b~0c"


def test_explicit_pointer_overrides_context_pointer():
    ctx = LintContext().child("steps")
    ctx.error("oops", json_pointer="/elsewhere")
    assert ctx.error_messages[0].json_pointer == "/elsewhere"


def test_linter_accepts_string_name():
    ctx = LintContext()
    ctx.warn("hi", linter="DirectName")
    assert ctx.warn_messages[0].linter == "DirectName"


def test_unannotated_emission_has_empty_pointer_and_no_linter():
    ctx = LintContext()
    ctx.warn("generic")
    msg = ctx.warn_messages[0]
    assert msg.linter is None
    assert msg.json_pointer == ""


def test_percent_style_positional_substitution():
    """Positional args use %-style formatting to match galaxy.tool_util.lint."""
    ctx = LintContext()
    ctx.warn("found %d issues in %s", 3, "step")
    assert ctx.warn_messages[0] == "found 3 issues in step"


def test_format_style_keyword_substitution_still_works():
    ctx = LintContext()
    ctx.warn("bad {value}", value="x")
    assert ctx.warn_messages[0] == "bad x"


def test_positional_without_percent_placeholders_falls_back_to_format():
    """Message with no %-placeholders should not raise; falls back to .format()."""
    ctx = LintContext()
    ctx.warn("plain {0}", "x")
    assert ctx.warn_messages[0] == "plain x"


def test_info_records_level_and_shares_list_with_children():
    ctx = LintContext()
    ctx.child("creator").child(0).info("consider adding an ORCID iD", linter="R")
    msg = ctx.info_messages[0]
    assert msg == "consider adding an ORCID iD"
    assert msg.level == LintLevel.INFO
    assert msg.json_pointer == "/creator/0"


@pytest.mark.parametrize(
    "level, expected",
    [
        ("error", LintLevel.ERROR),
        ("warn", LintLevel.WARN),
        ("INFO", LintLevel.INFO),
        ("all", LintLevel.ALL),
        (LintLevel.INFO, LintLevel.INFO),
    ],
)
def test_context_level_accepts_names_and_members(level, expected):
    ctx = LintContext(level=level)
    assert ctx.level is expected
    assert ctx.child("steps").level is expected


def test_default_context_level_is_warn():
    assert LintContext().level is LintLevel.WARN


@pytest.mark.parametrize(
    "level, printed",
    [
        (LintLevel.ERROR, {"ERROR"}),
        (LintLevel.WARN, {"ERROR", "WARNING"}),
        (LintLevel.INFO, {"ERROR", "WARNING", "INFO"}),
        (LintLevel.ALL, {"ERROR", "WARNING", "INFO"}),
    ],
)
def test_print_messages_reports_messages_at_or_above_level(capsys, level, printed):
    ctx = LintContext(level=level)
    ctx.error("an error")
    ctx.warn("a warning")
    ctx.info("a suggestion")
    ctx.print_messages()
    out = capsys.readouterr().out
    assert {label for label in ("ERROR", "WARNING", "INFO") if f".. {label}: " in out} == printed
    assert ctx.found_errors
    assert ctx.found_warns is (level <= LintLevel.WARN)
