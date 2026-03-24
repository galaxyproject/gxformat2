"""Tests for best-practice linting and pydantic schema validation checks."""

import pytest

from gxformat2.examples import load
from gxformat2.lint import (
    lint_best_practices_format2,
    lint_best_practices_ga,
    lint_pydantic_validation,
)
from gxformat2.linting import LintContext


NATIVE_BASE = {"a_galaxy_workflow": "true", "format-version": "0.1"}
FORMAT2_BASE = {"class": "GalaxyWorkflow", "inputs": {}, "outputs": {}}


def lint_native(wf_dict):
    ctx = LintContext()
    lint_best_practices_ga(ctx, {**NATIVE_BASE, **wf_dict})
    return ctx


def lint_format2(wf_dict):
    ctx = LintContext()
    lint_best_practices_format2(ctx, {**FORMAT2_BASE, **wf_dict})
    return ctx


def lint_pydantic(wf_dict, format2):
    ctx = LintContext()
    lint_pydantic_validation(ctx, wf_dict, format2=format2)
    return ctx


def native_step(step_overrides=None):
    step = {"id": 0, "type": "tool"}
    if step_overrides:
        step.update(step_overrides)
    return {"steps": {"0": step}}


def format2_step(step_overrides=None, use_list=False):
    step = {"tool_id": "cat1"}
    if step_overrides:
        step.update(step_overrides)
    if use_list:
        step.setdefault("id", "cat")
        return {"steps": [step]}
    return {"steps": {"cat": step}}


def has_warning(ctx, substring):
    return any(substring in m for m in ctx.warn_messages)


def has_error(ctx, substring):
    return any(substring in m for m in ctx.error_messages)


# --- Shared checks (annotation, creator, license) ---


class TestAnnotation:
    def test_native_no_annotation(self):
        assert has_warning(lint_native({"steps": {}}), "not annotated")

    def test_native_with_annotation(self):
        assert not has_warning(lint_native({"annotation": "A workflow", "steps": {}}), "not annotated")

    def test_format2_no_doc(self):
        assert has_warning(lint_format2({"steps": {}}), "not annotated")

    @pytest.mark.parametrize("doc", ["", ["", ""]])
    def test_format2_empty_doc(self, doc):
        assert has_warning(lint_format2({"doc": doc, "steps": {}}), "not annotated")

    def test_format2_with_doc(self):
        assert not has_warning(lint_format2({"doc": "A workflow", "steps": {}}), "not annotated")


class TestCreator:
    def test_no_creator(self):
        assert has_warning(lint_native({"steps": {}}), "creator")

    def test_with_creator(self):
        ctx = lint_native({"creator": [{"class": "Person", "name": "Alice"}], "steps": {}})
        assert not has_warning(ctx, "does not specify a creator")

    def test_identifier_no_scheme(self):
        ctx = lint_native({"creator": [{"class": "Person", "identifier": "0000-0002-1825-0097"}], "steps": {}})
        assert has_warning(ctx, "fully qualified URI")

    def test_identifier_with_scheme(self):
        ctx = lint_native(
            {"creator": [{"class": "Person", "identifier": "https://orcid.org/0000-0002-1825-0097"}], "steps": {}}
        )
        assert not has_warning(ctx, "fully qualified URI")

    def test_single_creator_in_list(self):
        ctx = lint_native({"creator": [{"class": "Person", "name": "Alice"}], "steps": {}})
        assert not has_warning(ctx, "does not specify a creator")

    def test_organization_skips_identifier_check(self):
        ctx = lint_native(
            {"creator": [{"class": "Organization", "name": "Acme", "identifier": "no-scheme"}], "steps": {}}
        )
        assert not has_warning(ctx, "fully qualified URI")


class TestLicense:
    def test_no_license(self):
        assert has_warning(lint_native({"steps": {}}), "license")

    def test_with_license(self):
        assert not has_warning(lint_native({"license": "MIT", "steps": {}}), "license")


# --- Native step checks ---


class TestNativeStepMetadata:
    def test_no_annotation(self):
        assert has_warning(lint_native(native_step()), "has no annotation")

    def test_no_label(self):
        assert has_warning(lint_native(native_step()), "has no label")

    def test_with_metadata(self):
        ctx = lint_native(native_step({"annotation": "ann", "label": "lbl"}))
        assert not has_warning(ctx, "has no annotation")
        assert not has_warning(ctx, "has no label")


class TestNativeDisconnectedInputs:
    def test_disconnected(self):
        ctx = lint_native(native_step({"inputs": [{"name": "input1"}], "input_connections": {}}))
        assert has_warning(ctx, "disconnected")

    def test_connected(self):
        ctx = lint_native(native_step({"inputs": [{"name": "input1"}], "input_connections": {"input1": {"id": 1, "output_name": "output"}}}))
        assert not has_warning(ctx, "disconnected")

    def test_null_input_connections(self):
        ctx = lint_native(native_step({"inputs": [{"name": "input1"}], "input_connections": None}))
        assert has_warning(ctx, "disconnected")

    @pytest.mark.parametrize("step_type", ["data_input", "data_collection_input", "parameter_input", "pause"])
    def test_skip_input_types(self, step_type):
        ctx = lint_native(native_step({"type": step_type, "inputs": [{"name": "input1"}], "input_connections": {}}))
        assert not has_warning(ctx, "disconnected")


class TestNativeUntypedParams:
    def test_untyped_in_tool_state(self):
        assert has_warning(lint_native(native_step({"tool_state": '{"p": "${v}"}'})), "untyped parameter as an input")

    def test_untyped_in_pja(self):
        pja = {"RenameDatasetActionoutput": {"action_type": "RenameDatasetAction", "output_name": "output", "action_arguments": {"newname": "${renamed}"}}}
        assert has_warning(lint_native(native_step({"post_job_actions": pja})), "untyped parameter in the post-job")

    def test_no_untyped(self):
        ctx = lint_native(native_step({"tool_state": '{"p": "v"}', "post_job_actions": {}}))
        assert not has_warning(ctx, "untyped")

    def test_clean_tool_state(self):
        assert not has_warning(lint_native(native_step({"tool_state": '{"p": "clean"}'})), "untyped")


# --- Format2 step checks ---


class TestFormat2StepMetadata:
    def test_no_doc(self):
        assert has_warning(lint_format2(format2_step()), "has no annotation")

    def test_dict_key_is_label(self):
        assert not has_warning(lint_format2(format2_step()), "has no label")

    def test_no_label_list_steps(self):
        assert has_warning(lint_format2(format2_step(use_list=True)), "has no label")

    def test_with_metadata(self):
        assert not has_warning(lint_format2(format2_step({"doc": "stuff", "label": "cat"})), "has no annotation")


class TestFormat2DisconnectedInputs:
    def test_disconnected_dict(self):
        assert has_warning(lint_format2(format2_step({"label": "cat", "in": {"input1": {}}})), "disconnected")

    def test_connected_string(self):
        assert not has_warning(lint_format2(format2_step({"in": {"input1": "the_input"}})), "disconnected")

    def test_connected_source(self):
        assert not has_warning(lint_format2(format2_step({"in": {"input1": {"source": "the_input"}}})), "disconnected")

    def test_has_default(self):
        assert not has_warning(lint_format2(format2_step({"in": {"input1": {"default": 42}}})), "disconnected")

    def test_disconnected_list_form(self):
        assert has_warning(lint_format2(format2_step({"in": [{"id": "input1"}]})), "disconnected")

    def test_connected_list_form(self):
        assert not has_warning(lint_format2(format2_step({"in": [{"id": "input1", "source": "x"}]})), "disconnected")


class TestFormat2UntypedParams:
    def test_untyped_in_tool_state(self):
        assert has_warning(lint_format2(format2_step({"tool_state": {"p": "${v}"}})), "untyped parameter as an input")

    def test_untyped_in_out(self):
        assert has_warning(
            lint_format2(format2_step({"out": {"o": {"rename": "${r}"}}})), "untyped parameter in the post-job"
        )


# --- Pydantic schema validation ---

VALID_NATIVE = {"a_galaxy_workflow": "true", "format-version": "0.1", "steps": {}}
VALID_FORMAT2 = {"class": "GalaxyWorkflow", "inputs": {}, "outputs": {}, "steps": {}}


class TestPydanticValidationNative:
    def test_valid(self):
        ctx = lint_pydantic(VALID_NATIVE, format2=False)
        assert not ctx.error_messages and not ctx.warn_messages

    def test_missing_required(self):
        assert has_error(lint_pydantic({"steps": {}}, format2=False), "Schema validation:")

    def test_extra_field_strict_only(self):
        wf = {**VALID_NATIVE, "steps": {"0": {"id": 0, "type": "tool", "unknown": "x"}}}
        ctx = lint_pydantic(wf, format2=False)
        assert not ctx.error_messages
        assert has_warning(ctx, "strict")

    def test_wrong_type(self):
        assert has_error(lint_pydantic({**VALID_NATIVE, "steps": "bad"}, format2=False), "Schema validation:")


class TestPydanticValidationFormat2:
    def test_valid(self):
        ctx = lint_pydantic(VALID_FORMAT2, format2=True)
        assert not ctx.error_messages and not ctx.warn_messages

    def test_missing_steps(self):
        wf = {"class": "GalaxyWorkflow", "inputs": {}, "outputs": {}}
        assert has_error(lint_pydantic(wf, format2=True), "Schema validation:")

    def test_extra_field_strict_only(self):
        ctx = lint_pydantic({**VALID_FORMAT2, "unknown": "x"}, format2=True)
        assert not ctx.error_messages
        assert has_warning(ctx, "strict")


# --- Integration tests using example workflow files ---

EXPECTED_NATIVE_UNLINTED = [
    "not annotated",
    "does not specify a creator",
    "does not specify a license",
    "disconnected",
    "has no annotation",
    "has no label",
    "untyped parameter as an input",
    "untyped parameter in the post-job",
]


class TestUnlintedNative:
    def test_all_best_practice_warnings(self):
        ctx = lint_native(load("synthetic-unlinted-best-practices.ga"))
        for expected in EXPECTED_NATIVE_UNLINTED:
            assert has_warning(ctx, expected), f"missing warning: {expected}"

    def test_dict_tool_state_variant(self):
        ctx = lint_native(load("synthetic-unlinted-best-practices-dict-tool-state.ga"))
        for expected in EXPECTED_NATIVE_UNLINTED:
            assert has_warning(ctx, expected), f"missing warning: {expected}"

    def test_bad_identifier(self):
        ctx = lint_native(load("synthetic-unlinted-best-practices-bad-identifier.ga"))
        assert has_warning(ctx, "fully qualified URI")
        # Should still have a creator (just a bad identifier)
        assert not has_warning(ctx, "does not specify a creator")


class TestUnlintedFormat2:
    def test_null_input_key_rejected(self):
        """Fixture has a null YAML key for an input — a legacy Galaxy export
        artifact that should be rejected at the schema level."""
        ctx = lint_format2(load("synthetic-unlinted-best-practices.gxwf.yml"))
        assert has_error(ctx, "Schema validation")
