"""Tests for gxformat2.to_format2 — model-returning native→Format2 conversion."""

from gxformat2.normalized import ensure_format2, NormalizedFormat2, to_format2
from gxformat2.normalized._format2 import GalaxyUserToolStub
from gxformat2.options import ConversionOptions

from .example_wfs import BASIC_WORKFLOW

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


class TestEnsureFormat2:

    def test_accepts_format2_dict(self):
        from gxformat2.yaml import ordered_load

        fmt2 = ordered_load(BASIC_WORKFLOW)
        result = ensure_format2(fmt2)
        assert isinstance(result, NormalizedFormat2)
        assert result.label

    def test_expand_true_returns_expanded_type(self):
        from gxformat2.normalized import ExpandedFormat2

        result = ensure_format2(MINIMAL_NATIVE, expand=True)
        assert isinstance(result, ExpandedFormat2)


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
        assert isinstance(step.run, GalaxyUserToolStub)
        assert step.run.class_ == "GalaxyUserTool"
        assert step.tool_id is None
