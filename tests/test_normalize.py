from gxformat2.export import from_galaxy_native
from gxformat2.normalize import Inputs, inputs_normalized, NormalizedWorkflow, outputs_normalized
from gxformat2.yaml import ordered_load
from ._helpers import (
    to_native,
)
from .example_wfs import INT_INPUT, INTEGER_INPUT
from .test_auto_label import NESTED_WORKFLOW_AUTO_LABELS_NEWER_SYNTAX

RANDOM_LINES_EXAMPLE = """
class: GalaxyWorkflow
inputs:
  data_input: data
  int_input:
    type: integer
    default: 3
steps:
  random:
    tool_id: random_lines1
    in:
      input: data_input
      num_lines: int_input
    state:
      seed_source:
        seed_source_selector: set_seed
        seed: asdf
"""


def test_inputs():
    for workflow_dict in _both_formats(RANDOM_LINES_EXAMPLE):
        inputs = Inputs(workflow_dict=workflow_dict)
        assert inputs.is_an_input(0)
        assert inputs.is_an_input("int_input")
        assert not inputs.is_an_input(2)
        assert not inputs.is_an_input("random")
        assert inputs.count == 2


def test_optional_inputs():
    # Ensure normalized inputs can be used to check if inputs have defaults.
    for workflow_dict in _both_formats(RANDOM_LINES_EXAMPLE):
        steps = inputs_normalized(workflow_dict=workflow_dict)
        assert steps[1]["type"] == "int"
        assert steps[1]["default"] == 3


def test_outputs_normalized():
    for workflow_dict in _both_formats(NESTED_WORKFLOW_AUTO_LABELS_NEWER_SYNTAX):
        outputs = outputs_normalized(workflow_dict=workflow_dict)
        assert len(outputs) == 1
        assert outputs[0]["id"] == "outer_output"


def test_normalized_workflow():
    # same workflow with slightly different input definitions, make sure normalize
    # unifies these
    for wf in [INTEGER_INPUT, INT_INPUT]:
        int_input_normalized = NormalizedWorkflow(ordered_load(wf)).normalized_workflow_dict
        inputs = int_input_normalized["inputs"]
        assert isinstance(inputs, list)
        assert isinstance(inputs[0], dict)  # str converted to dictionary
        assert inputs[0]["id"] == "input_d"
        assert inputs[0]["type"] == "data"  # converted from File to data
        assert isinstance(inputs[1], dict)
        assert inputs[1]["type"] == "int"


def test_unlabeled_subworkflow_step_anonymous_output():
    """NormalizedWorkflow resolves anonymous output refs when inner subworkflow steps are unlabeled."""
    native_workflow = {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "Subworkflow Anon Output Test",
        "steps": {
            "0": {
                "id": 0,
                "type": "data_input",
                "label": "input_data",
                "tool_state": '{"name": "input_data"}',
                "input_connections": {},
                "workflow_outputs": [],
            },
            "1": {
                "id": 1,
                "type": "subworkflow",
                "label": "nested",
                "tool_state": "{}",
                "input_connections": {
                    "inner_input": [{"id": 0, "output_name": "output"}],
                },
                "workflow_outputs": [
                    {"output_name": "0:out_file1", "label": "subwf_output"},
                ],
                "subworkflow": {
                    "a_galaxy_workflow": "true",
                    "format-version": "0.1",
                    "name": "Inner",
                    "steps": {
                        "0": {
                            "id": 0,
                            "type": "tool",
                            "label": None,
                            "tool_id": "cat1",
                            "tool_version": "1.0",
                            "tool_state": "{}",
                            "input_connections": {},
                            "workflow_outputs": [
                                {"output_name": "out_file1", "label": None},
                            ],
                        },
                    },
                },
            },
        },
    }
    as_format2 = from_galaxy_native(native_workflow, tool_interface=None, json_wrapper=False)
    # The outputSource should contain the anonymous subworkflow ref pattern
    output_sources = [v["outputSource"] for v in as_format2["outputs"].values()]
    # Should have a source referencing the subworkflow step
    assert any("nested" in s for s in output_sources)

    # NormalizedWorkflow should resolve without error
    normalized = NormalizedWorkflow(as_format2)
    norm_outputs = normalized.normalized_workflow_dict.get("outputs", {})
    # The anonymous "0:out_file1" reference should be resolved to a proper output name
    for output_def in norm_outputs.values():
        source = output_def.get("outputSource", "")
        assert ":" not in source, f"Unresolved anonymous subworkflow ref: {source}"


def _both_formats(contents):
    return [ordered_load(contents), to_native(contents)]
