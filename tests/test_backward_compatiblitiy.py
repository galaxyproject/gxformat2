"""Test converting to native format and back out migrates legacy syntax elements."""

from ._helpers import round_trip

LEGACY_PJA_1 = """
class: GalaxyWorkflow
name: My Cool Workflow!
inputs:
  input1: data
outputs:
  out1:
    outputSource: second_cat/out_file1
steps:
  first_cat:
    tool_id: cat1
    in:
      input1: input1
    outputs:
       out_file1:
         hide: true
         rename: "the new value"
  second_cat:
    tool_id: cat1
    in:
      input1: first_cat/out_file1
"""


def test_workflow_name():
    """To be valid schema salad syntax, workflow name should be label."""
    updated = round_trip(LEGACY_PJA_1)
    assert "label" in updated
    assert updated["label"] == "My Cool Workflow!"
    assert "name" not in updated


def test_step_outputs():
    """To be valid a valid Process - workflow steps should have an out element, not outputs.

    This is also much more consistent with 'in' syntax.
    """
    updated = round_trip(LEGACY_PJA_1)
    assert "out" in updated["steps"]["first_cat"]
    assert "outputs" not in updated["steps"]["first_cat"]
