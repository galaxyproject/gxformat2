from gxformat2._yaml import ordered_load
from gxformat2.normalize import inputs_normalized, outputs_normalized
from ._helpers import (
    to_native,
)
from .test_auto_label import NESTED_WORKFLOW_AUTO_LABELS_NEWER_SYNTAX


def test_optional_inputs():
    # Ensure normalized inputs can be used to check if inputs have defaults.
    for workflow_dict in _both_formats("""
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
"""):
        steps = inputs_normalized(workflow_dict=workflow_dict)
        assert steps[1]["type"] == "parameter_input"
        assert steps[1]["default"] == 3


def test_outputs_normalized():
    for workflow_dict in _both_formats(NESTED_WORKFLOW_AUTO_LABELS_NEWER_SYNTAX):
        outputs = outputs_normalized(workflow_dict=workflow_dict)
        assert len(outputs) == 1
        assert outputs[0]["id"] == "outer_output"


def _both_formats(contents):
    return [ordered_load(contents), to_native(contents)]
