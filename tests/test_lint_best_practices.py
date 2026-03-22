"""Tests for best-practice linting checks."""

from gxformat2.lint import (
    lint_best_practices_format2,
    lint_best_practices_ga,
)
from gxformat2.linting import LintContext


def _lint_ctx():
    return LintContext()


# --- Shared checks (annotation, creator, license) ---


class TestAnnotation:
    def test_native_no_annotation(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(ctx, {"steps": {}})
        assert any("not annotated" in m for m in ctx.warn_messages)

    def test_native_with_annotation(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(ctx, {"annotation": "A workflow", "steps": {}})
        assert not any("not annotated" in m for m in ctx.warn_messages)

    def test_format2_no_doc(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(ctx, {"steps": {}})
        assert any("not annotated" in m for m in ctx.warn_messages)

    def test_format2_empty_doc(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(ctx, {"doc": "", "steps": {}})
        assert any("not annotated" in m for m in ctx.warn_messages)

    def test_format2_empty_doc_list(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(ctx, {"doc": ["", ""], "steps": {}})
        assert any("not annotated" in m for m in ctx.warn_messages)

    def test_format2_with_doc(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(ctx, {"doc": "A workflow", "steps": {}})
        assert not any("not annotated" in m for m in ctx.warn_messages)


class TestCreator:
    def test_no_creator(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(ctx, {"steps": {}})
        assert any("creator" in m for m in ctx.warn_messages)

    def test_with_creator(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "creator": [{"class": "Person", "name": "Alice"}],
                "steps": {},
            },
        )
        assert not any("does not specify a creator" in m for m in ctx.warn_messages)

    def test_creator_identifier_no_scheme(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "creator": [{"class": "Person", "identifier": "0000-0002-1825-0097"}],
                "steps": {},
            },
        )
        assert any("fully qualified URI" in m for m in ctx.warn_messages)

    def test_creator_identifier_with_scheme(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "creator": [{"class": "Person", "identifier": "https://orcid.org/0000-0002-1825-0097"}],
                "steps": {},
            },
        )
        assert not any("fully qualified URI" in m for m in ctx.warn_messages)

    def test_creator_single_dict_not_list(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "creator": {"class": "Person", "name": "Alice"},
                "steps": {},
            },
        )
        assert not any("does not specify a creator" in m for m in ctx.warn_messages)

    def test_creator_organization_no_identifier_check(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "creator": [{"class": "Organization", "name": "Acme", "identifier": "no-scheme"}],
                "steps": {},
            },
        )
        # Organization class != "person" so identifier URI check shouldn't fire
        assert not any("fully qualified URI" in m for m in ctx.warn_messages)


class TestLicense:
    def test_no_license(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(ctx, {"steps": {}})
        assert any("license" in m for m in ctx.warn_messages)

    def test_with_license(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(ctx, {"license": "MIT", "steps": {}})
        assert not any("license" in m for m in ctx.warn_messages)


# --- Native step checks ---


class TestNativeStepMetadata:
    def test_no_annotation(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {"0": {"id": 0, "type": "tool"}},
            },
        )
        assert any("has no annotation" in m for m in ctx.warn_messages)

    def test_no_label(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {"0": {"id": 0, "type": "tool"}},
            },
        )
        assert any("has no label" in m for m in ctx.warn_messages)

    def test_with_metadata(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {"0": {"id": 0, "type": "tool", "annotation": "step ann", "label": "step lbl"}},
            },
        )
        assert not any("has no annotation" in m for m in ctx.warn_messages)
        assert not any("has no label" in m for m in ctx.warn_messages)


class TestNativeDisconnectedInputs:
    def test_disconnected(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {
                    "0": {
                        "id": 0,
                        "type": "tool",
                        "inputs": [{"name": "input1"}],
                        "input_connections": {},
                    }
                },
            },
        )
        assert any("input1" in m and "disconnected" in m for m in ctx.warn_messages)

    def test_connected(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {
                    "0": {
                        "id": 0,
                        "type": "tool",
                        "inputs": [{"name": "input1"}],
                        "input_connections": {"input1": {"id": 1, "output_name": "out"}},
                    }
                },
            },
        )
        assert not any("disconnected" in m for m in ctx.warn_messages)

    def test_null_input_connections(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {
                    "0": {
                        "id": 0,
                        "type": "tool",
                        "inputs": [{"name": "input1"}],
                        "input_connections": None,
                    }
                },
            },
        )
        assert any("disconnected" in m for m in ctx.warn_messages)

    def test_skip_input_types(self):
        for step_type in ["data_input", "data_collection_input", "parameter_input", "pause"]:
            ctx = _lint_ctx()
            lint_best_practices_ga(
                ctx,
                {
                    "steps": {
                        "0": {
                            "id": 0,
                            "type": step_type,
                            "inputs": [{"name": "input1"}],
                            "input_connections": {},
                        }
                    },
                },
            )
            assert not any("disconnected" in m for m in ctx.warn_messages), f"should skip {step_type}"


class TestNativeUntypedParams:
    def test_untyped_in_tool_state(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {
                    "0": {
                        "id": 0,
                        "type": "tool",
                        "tool_state": '{"param": "${value}"}',
                    }
                },
            },
        )
        assert any("untyped parameter as an input" in m for m in ctx.warn_messages)

    def test_untyped_in_pja(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {
                    "0": {
                        "id": 0,
                        "type": "tool",
                        "post_job_actions": {"RenameDatasetActionout": {"action_arguments": {"newname": "${renamed}"}}},
                    }
                },
            },
        )
        assert any("untyped parameter in the post-job actions" in m for m in ctx.warn_messages)

    def test_no_untyped(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {
                    "0": {
                        "id": 0,
                        "type": "tool",
                        "tool_state": '{"param": "value"}',
                        "post_job_actions": {},
                    }
                },
            },
        )
        assert not any("untyped" in m for m in ctx.warn_messages)

    def test_malformed_json_tool_state(self):
        ctx = _lint_ctx()
        lint_best_practices_ga(
            ctx,
            {
                "steps": {
                    "0": {
                        "id": 0,
                        "type": "tool",
                        "tool_state": "not valid json {{{",
                    }
                },
            },
        )
        # Should not crash, should not report untyped params
        assert not any("untyped" in m for m in ctx.warn_messages)


# --- Format2 step checks ---


class TestFormat2StepMetadata:
    def test_no_doc(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {"cat": {"tool_id": "cat1"}},
            },
        )
        assert any("has no annotation" in m for m in ctx.warn_messages)

    def test_no_label_dict_steps(self):
        """Dict steps get label from key, so they always have a label."""
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {"cat": {"tool_id": "cat1"}},
            },
        )
        # "cat" is the label from dict key
        assert not any("has no label" in m for m in ctx.warn_messages)

    def test_no_label_list_steps(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": [{"id": "cat", "tool_id": "cat1"}],
            },
        )
        assert any("has no label" in m for m in ctx.warn_messages)

    def test_with_metadata(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {"cat": {"tool_id": "cat1", "doc": "does cat stuff", "label": "cat"}},
            },
        )
        assert not any("has no annotation" in m for m in ctx.warn_messages)


class TestFormat2DisconnectedInputs:
    def test_disconnected_dict_input(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {
                    "cat": {
                        "tool_id": "cat1",
                        "label": "cat",
                        "in": {"input1": {}},
                    }
                },
            },
        )
        assert any("input1" in m and "disconnected" in m for m in ctx.warn_messages)

    def test_connected_string_shorthand(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {
                    "cat": {
                        "tool_id": "cat1",
                        "in": {"input1": "the_input"},
                    }
                },
            },
        )
        assert not any("disconnected" in m for m in ctx.warn_messages)

    def test_connected_source(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {
                    "cat": {
                        "tool_id": "cat1",
                        "in": {"input1": {"source": "the_input"}},
                    }
                },
            },
        )
        assert not any("disconnected" in m for m in ctx.warn_messages)

    def test_has_default(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {
                    "cat": {
                        "tool_id": "cat1",
                        "in": {"input1": {"default": 42}},
                    }
                },
            },
        )
        assert not any("disconnected" in m for m in ctx.warn_messages)

    def test_disconnected_list_form_input(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {
                    "cat": {
                        "tool_id": "cat1",
                        "in": [{"id": "input1"}],
                    }
                },
            },
        )
        assert any("input1" in m and "disconnected" in m for m in ctx.warn_messages)

    def test_connected_list_form_input(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {
                    "cat": {
                        "tool_id": "cat1",
                        "in": [{"id": "input1", "source": "the_input"}],
                    }
                },
            },
        )
        assert not any("disconnected" in m for m in ctx.warn_messages)


class TestFormat2UntypedParams:
    def test_untyped_in_tool_state(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {
                    "cat": {
                        "tool_id": "cat1",
                        "tool_state": {"param": "${value}"},
                    }
                },
            },
        )
        assert any("untyped parameter as an input" in m for m in ctx.warn_messages)

    def test_untyped_in_out(self):
        ctx = _lint_ctx()
        lint_best_practices_format2(
            ctx,
            {
                "steps": {
                    "cat": {
                        "tool_id": "cat1",
                        "out": {"out_file1": {"rename": "${renamed}"}},
                    }
                },
            },
        )
        assert any("untyped parameter in the post-job actions" in m for m in ctx.warn_messages)
