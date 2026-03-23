"""Tests for gxformat2.native.load_native()."""

import pytest
from pydantic import ValidationError

from gxformat2.native import load_native

MINIMAL_WORKFLOW = {
    "a_galaxy_workflow": "true",
    "format-version": "0.1",
    "name": "Test",
    "steps": {},
}


class TestLoadNativeStrict:
    """Strict mode rejects Galaxy serialization quirks."""

    def test_tags_empty_string_rejected(self):
        wf = {**MINIMAL_WORKFLOW, "tags": ""}
        with pytest.raises(ValidationError):
            load_native(wf, strict=True)

    def test_tags_comma_string_rejected(self):
        wf = {**MINIMAL_WORKFLOW, "tags": "a,b"}
        with pytest.raises(ValidationError):
            load_native(wf, strict=True)

    def test_valid_tags_accepted(self):
        wf = {**MINIMAL_WORKFLOW, "tags": ["a", "b"]}
        result = load_native(wf, strict=True)
        assert result.tags == ["a", "b"]


class TestLoadNativeLax:
    """Lax mode normalizes known quirks."""

    def test_tags_empty_string_normalized(self):
        wf = {**MINIMAL_WORKFLOW, "tags": ""}
        result = load_native(wf, strict=False)
        assert result.tags == []

    def test_tags_comma_separated_normalized(self):
        wf = {**MINIMAL_WORKFLOW, "tags": "a,b"}
        result = load_native(wf, strict=False)
        assert result.tags == ["a", "b"]

    def test_tags_comma_separated_whitespace(self):
        wf = {**MINIMAL_WORKFLOW, "tags": " a , b , "}
        result = load_native(wf, strict=False)
        assert result.tags == ["a", "b"]

    def test_tags_single_value(self):
        wf = {**MINIMAL_WORKFLOW, "tags": "mytag"}
        result = load_native(wf, strict=False)
        assert result.tags == ["mytag"]

    def test_valid_tags_unchanged(self):
        wf = {**MINIMAL_WORKFLOW, "tags": ["a", "b"]}
        result = load_native(wf, strict=False)
        assert result.tags == ["a", "b"]

    def test_tags_none_unchanged(self):
        wf = {**MINIMAL_WORKFLOW, "tags": None}
        result = load_native(wf, strict=False)
        assert result.tags is None

    def test_no_tags_key(self):
        result = load_native(MINIMAL_WORKFLOW, strict=False)
        assert result.tags is None

    def test_subworkflow_tags_normalized(self):
        wf = {
            **MINIMAL_WORKFLOW,
            "steps": {
                "0": {
                    "id": 0,
                    "type": "subworkflow",
                    "subworkflow": {**MINIMAL_WORKFLOW, "tags": "sub_a,sub_b"},
                }
            },
        }
        result = load_native(wf, strict=False)
        assert result.steps["0"].subworkflow.tags == ["sub_a", "sub_b"]

    def test_action_arguments_string_normalized(self):
        wf = {
            **MINIMAL_WORKFLOW,
            "steps": {
                "0": {
                    "id": 0,
                    "type": "tool",
                    "tool_id": "cat1",
                    "post_job_actions": {
                        "RenameOut": {
                            "action_type": "RenameDatasetAction",
                            "output_name": "out",
                            "action_arguments": "bad_scalar_value",
                        }
                    },
                }
            },
        }
        result = load_native(wf, strict=False)
        pja = result.steps["0"].post_job_actions["RenameOut"]
        assert pja.action_arguments is None

    def test_action_arguments_dict_unchanged(self):
        wf = {
            **MINIMAL_WORKFLOW,
            "steps": {
                "0": {
                    "id": 0,
                    "type": "tool",
                    "tool_id": "cat1",
                    "post_job_actions": {
                        "RenameOut": {
                            "action_type": "RenameDatasetAction",
                            "output_name": "out",
                            "action_arguments": {"newname": "renamed"},
                        }
                    },
                }
            },
        }
        result = load_native(wf, strict=False)
        pja = result.steps["0"].post_job_actions["RenameOut"]
        assert pja.action_arguments == {"newname": "renamed"}

    def test_does_not_mutate_input(self):
        wf = {**MINIMAL_WORKFLOW, "tags": "a,b"}
        original_tags = wf["tags"]
        load_native(wf, strict=False)
        assert wf["tags"] == original_tags
