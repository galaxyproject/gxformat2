"""Tests for gxformat2.to_format2 — model-returning native→Format2 conversion."""

from gxformat2.normalized import NormalizedFormat2
from gxformat2.options import ConversionOptions
from gxformat2.to_format2 import to_format2

MINIMAL_NATIVE = {
    "a_galaxy_workflow": "true",
    "format-version": "0.1",
    "name": "Test Workflow",
    "annotation": "A test workflow",
    "steps": {
        "0": {
            "id": 0,
            "type": "data_input",
            "label": "the_input",
            "tool_state": '{"optional": false}',
            "input_connections": {},
            "inputs": [{"name": "the_input", "description": ""}],
            "outputs": [],
            "workflow_outputs": [],
        },
        "1": {
            "id": 1,
            "type": "tool",
            "tool_id": "cat1",
            "tool_version": "1.0",
            "label": "the_cat",
            "input_connections": {"input1": {"id": 0, "output_name": "output"}},
            "workflow_outputs": [{"output_name": "out_file1", "label": "the_output"}],
        },
    },
}


class TestToFormat2Basic:

    def test_returns_normalized_format2(self):
        result = to_format2(MINIMAL_NATIVE)
        assert isinstance(result, NormalizedFormat2)

    def test_workflow_metadata(self):
        result = to_format2(MINIMAL_NATIVE)
        assert result.label == "Test Workflow"
        assert result.doc == "A test workflow"

    def test_inputs_extracted(self):
        result = to_format2(MINIMAL_NATIVE)
        assert len(result.inputs) == 1
        assert result.inputs[0].id == "the_input"

    def test_outputs_wired(self):
        result = to_format2(MINIMAL_NATIVE)
        assert len(result.outputs) == 1
        assert result.outputs[0].id == "the_output"
        assert "the_cat" in result.outputs[0].outputSource

    def test_tool_step_converted(self):
        result = to_format2(MINIMAL_NATIVE)
        assert len(result.steps) == 1
        step = result.steps[0]
        assert step.tool_id == "cat1"
        assert step.tool_version == "1.0"

    def test_step_inputs_have_source(self):
        result = to_format2(MINIMAL_NATIVE)
        step = result.steps[0]
        assert len(step.in_) == 1
        assert step.in_[0].id == "input1"
        assert step.in_[0].source == "the_input"

    def test_compact_strips_position(self):
        native = {
            **MINIMAL_NATIVE,
            "steps": {
                **MINIMAL_NATIVE["steps"],
                "1": {
                    **MINIMAL_NATIVE["steps"]["1"],
                    "position": {"left": 100, "top": 200},
                },
            },
        }
        opts = ConversionOptions(compact=True)
        result = to_format2(native, options=opts)
        assert result.steps[0].position is None


class TestToFormat2Subworkflow:

    def test_inline_subworkflow(self):
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "Outer",
            "steps": {
                "0": {
                    "id": 0,
                    "type": "data_input",
                    "label": "outer_input",
                    "tool_state": "{}",
                    "input_connections": {},
                    "inputs": [],
                    "outputs": [],
                    "workflow_outputs": [],
                },
                "1": {
                    "id": 1,
                    "type": "subworkflow",
                    "label": "nested",
                    "input_connections": {"inner_input": {"id": 0, "output_name": "output"}},
                    "subworkflow": {
                        "a_galaxy_workflow": "true",
                        "format-version": "0.1",
                        "name": "Inner",
                        "steps": {
                            "0": {
                                "id": 0,
                                "type": "data_input",
                                "label": "inner_input",
                                "tool_state": "{}",
                                "input_connections": {},
                                "inputs": [],
                                "outputs": [],
                                "workflow_outputs": [],
                            },
                        },
                    },
                },
            },
        }
        result = to_format2(native)
        nested = [s for s in result.steps if s.label == "nested"][0]
        assert nested.run is not None
        assert isinstance(nested.run, NormalizedFormat2)
        assert len(nested.run.inputs) == 1

    def test_url_subworkflow_passthrough(self):
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "Outer",
            "steps": {
                "0": {
                    "id": 0,
                    "type": "data_input",
                    "label": "outer_input",
                    "tool_state": "{}",
                    "input_connections": {},
                    "inputs": [],
                    "outputs": [],
                    "workflow_outputs": [],
                },
                "1": {
                    "id": 1,
                    "type": "subworkflow",
                    "label": "nested",
                    "content_source": "url",
                    "content_id": "https://example.com/inner.ga",
                    "input_connections": {"inner_input": {"id": 0, "output_name": "output"}},
                },
            },
        }
        result = to_format2(native)
        nested = [s for s in result.steps if s.label == "nested"][0]
        assert nested.run == "https://example.com/inner.ga"


class TestToFormat2PostJobActions:

    def test_rename_action(self):
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "PJA Test",
            "steps": {
                "0": {
                    "id": 0,
                    "type": "data_input",
                    "label": "inp",
                    "tool_state": "{}",
                    "input_connections": {},
                    "inputs": [],
                    "outputs": [],
                    "workflow_outputs": [],
                },
                "1": {
                    "id": 1,
                    "type": "tool",
                    "tool_id": "cat1",
                    "label": "cat",
                    "input_connections": {"input1": {"id": 0, "output_name": "output"}},
                    "post_job_actions": {
                        "RenameDatasetActionout_file1": {
                            "action_type": "RenameDatasetAction",
                            "output_name": "out_file1",
                            "action_arguments": {"newname": "renamed_output"},
                        }
                    },
                },
            },
        }
        result = to_format2(native)
        step = result.steps[0]
        assert len(step.out) == 1
        assert step.out[0].id == "out_file1"
        assert step.out[0].rename == "renamed_output"


class TestToFormat2UserTool:

    def test_user_defined_tool(self):
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "User Tool Test",
            "steps": {
                "0": {
                    "id": 0,
                    "type": "data_input",
                    "label": "inp",
                    "tool_state": "{}",
                    "input_connections": {},
                    "inputs": [],
                    "outputs": [],
                    "workflow_outputs": [],
                },
                "1": {
                    "id": 1,
                    "type": "tool",
                    "label": "my_tool",
                    "tool_representation": {
                        "class": "GalaxyUserTool",
                        "name": "My Tool",
                        "shell_command": "cat '$input1' > '$output1'",
                    },
                    "input_connections": {"input1": {"id": 0, "output_name": "output"}},
                },
            },
        }
        result = to_format2(native)
        step = result.steps[0]
        assert step.run is not None
        assert step.run["class"] == "GalaxyUserTool"
        assert step.tool_id is None
