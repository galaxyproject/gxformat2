import pytest

from ._helpers import round_trip

NESTED_WORKFLOW_AUTO_LABELS_LEGACY_SYNTAX = """
class: GalaxyWorkflow
inputs:
  outer_input: data
outputs:
  outer_output:
    outputSource: second_cat/out_file1
steps:
  first_cat:
    tool_id: cat1
    in:
      input1: outer_input
  nested_workflow:
    run:
      class: GalaxyWorkflow
      inputs:
        - id: inner_input
      outputs:
        - outputSource: 1/out_file1
      steps:
        random:
          tool_id: random_lines1
          state:
            num_lines: 1
            input:
              $link: inner_input
            seed_source:
              seed_source_selector: set_seed
              seed: asdf
    in:
      inner_input: first_cat/out_file1
  second_cat:
    tool_id: cat1
    state:
      input1:
        $link: nested_workflow/1:out_file1
      queries:
        - input2:
            $link: nested_workflow/1:out_file1
"""

NESTED_WORKFLOW_AUTO_LABELS_NEWER_SYNTAX = """
class: GalaxyWorkflow
inputs:
  outer_input: data
outputs:
  outer_output:
    outputSource: second_cat/out_file1
steps:
  first_cat:
    tool_id: cat1
    in:
      input1: outer_input
  nested_workflow:
    run:
      class: GalaxyWorkflow
      inputs:
        - id: inner_input
      outputs:
        - outputSource: 1/out_file1
      steps:
        random:
          tool_id: random_lines1
          state:
            num_lines: 1
            input:
              $link: inner_input
            seed_source:
              seed_source_selector: set_seed
              seed: asdf
    in:
      inner_input: first_cat/out_file1
  second_cat:
    tool_id: cat1
    in:
      input1: nested_workflow/1:out_file1
      queries_0|input2: nested_workflow/1:out_file1
"""


@pytest.mark.parametrize("wf_text", [NESTED_WORKFLOW_AUTO_LABELS_LEGACY_SYNTAX, NESTED_WORKFLOW_AUTO_LABELS_NEWER_SYNTAX])
def test_round_trip_auto_labels(wf_text):
    result = round_trip(wf_text)
    inputs = result['steps']['second_cat']['in']
    assert len(inputs) == 2
    assert inputs['input1']['source'] == 'nested_workflow/1:out_file1'
    assert inputs['queries_0|input2']['source'] == 'nested_workflow/1:out_file1'
