import json
from collections import OrderedDict

import pytest

from gxformat2.converter import (
    POST_JOB_ACTIONS,
)
from .test_basic import (
    assert_valid_native,
    from_native,
    to_native,
)


WORKFLOW_PJA_TEMPLATE_1905_FORMAT = """
class: GalaxyWorkflow
doc: |
  Workflow with post job actions.
inputs:
  the_input:
    type: File
    doc: input doc
steps:
  cat:
    tool_id: cat1
    doc: cat doc
    in:
      input1: the_input
    outputs:
      out_file1:
        {action}: {action_value}
"""


WORKFLOW_PJA_TEMPLATE_1909_FORMAT = """
class: GalaxyWorkflow
doc: |
  Workflow with post job actions.
inputs:
  the_input:
    type: File
    doc: input doc
steps:
  cat:
    tool_id: cat1
    doc: cat doc
    in:
      input1: the_input
    out:
      out_file1:
        {action}: {action_value}
"""


@pytest.mark.parametrize("wf_template", [WORKFLOW_PJA_TEMPLATE_1905_FORMAT, WORKFLOW_PJA_TEMPLATE_1909_FORMAT])
def test_post_job_action_to_native(wf_template):
    for action_key in POST_JOB_ACTIONS:
        default_value = POST_JOB_ACTIONS[action_key]['default']
        expected_value = None
        if isinstance(default_value, dict):
            action_value = 'new_value'
            if action_key == 'rename':
                expected_value = {'newname': action_value}
            elif action_key == 'change_datatype':
                expected_value = {'newtype': action_value}
        elif isinstance(default_value, list):
            action_value = '[tag]'
            expected_value = {'tags': 'tag'}
        elif isinstance(default_value, bool):
            action_value = 'true'
            expected_value = True
        workflow_yaml = wf_template.format(action=action_key, action_value=action_value)
        native = to_native(workflow_yaml)
        pja_class = POST_JOB_ACTIONS[action_key]['action_class']
        expected_pja = {pja_class + 'out_file1': OrderedDict([
                ("output_name", "out_file1"),
                ("action_type", pja_class),
                ("action_arguments", expected_value or action_value),
        ])}
        expected_pja = json.dumps(expected_pja, sort_keys=True)
        converted_pjas = json.dumps(native['steps']['1']['post_job_actions'], sort_keys=True)
        assert expected_pja == converted_pjas, f"Expected:\n{expected_pja}\nActual:\n{converted_pjas}'"
        assert_valid_native(native)
        roundtrip_workflow = from_native(native)
        out_def = roundtrip_workflow['steps']['cat']['out']['out_file1']
        assert action_key in out_def, f"{action_key} not in {out_def}"
