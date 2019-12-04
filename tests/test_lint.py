import copy
import json
import os
import tempfile

from gxformat2.lint import main
from gxformat2._yaml import ordered_dump, ordered_load
from ._helpers import assert_valid_native, to_native

_deep_copy = copy.deepcopy

TEST_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_EXAMPLES = os.path.join(TEST_PATH, "examples")

BASIC_WORKFLOW = """
class: GalaxyWorkflow
doc: |
  Simple workflow that no-op cats a file and then selects 10 random lines.
inputs:
  the_input:
    type: File
    doc: input doc
outputs:
  the_output:
    outputSource: cat/out_file1
steps:
  cat:
    tool_id: cat1
    doc: cat doc
    in:
      input1: the_input
"""

WORKFLOW_WITH_REPEAT = """
class: GalaxyWorkflow
inputs:
  input1: data
outputs:
  out1:
    outputSource: first_cat/out_file1
steps:
  first_cat:
    tool_id: cat
    in:
      input1: input1
      queries_0|input2: input1
      queries_1|input2: input1
"""


RULES_TOOL = """
class: GalaxyWorkflow
inputs:
  input_c: collection
outputs:
  out1:
    outputSource: random_lines/out_file1
steps:
  apply:
    tool_id: __APPLY_RULES__
    state:
      input:
        $link: input_c
      rules:
        rules:
          - type: add_column_metadata
            value: identifier0
          - type: add_column_metadata
            value: identifier0
        mapping:
          - type: list_identifiers
            columns: [0, 1]
  random_lines:
    tool_id: random_lines1
    state:
      num_lines: 1
      input:
        $link: apply#output
      seed_source:
        seed_source_selector: set_seed
        seed: asdf
"""


NESTED_WORKFLOW = """
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
        inner_input: data
      outputs:
        workflow_output:
          outputSource: random_lines/out_file1
      steps:
        random_lines:
          tool_id: random_lines1
          state:
            num_lines: 2
            input:
              $link: inner_input
            seed_source:
              seed_source_selector: set_seed
              seed: asdf
    in:
      inner_input: first_cat/out_file1
  split:
    tool_id: split
    in:
      input1: nested_workflow/workflow_output
  second_cat:
    tool_id: cat_list
    in:
      input1: split/output
"""


RUNTIME_INPUTS = """
class: GalaxyWorkflow
inputs:
  input1: data
outputs:
  out1:
    outputSource: random/out_file1
steps:
  the_pause:
    type: pause
    in:
      input: input1
  random:
    tool_id: random_lines1
    runtime_inputs:
      - num_lines
    state:
      input:
        $link: the_pause
      seed_source:
        seed_source_selector: set_seed
        seed: asdf
"""

PJA_1 = """
class: GalaxyWorkflow
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
    out:
       out_file1:
         hide: true
         rename: "the new value"
  second_cat:
    tool_id: cat1
    in:
      input1: first_cat/out_file1
"""


def setup_module(module):
    # Setup an examples directory with examples we want to correspond to what exit codes,
    # do this so we can run same tests in Java.
    green_format2 = ordered_load(BASIC_WORKFLOW)
    _dump_with_exit_code(green_format2, 0, "basic_format2")
    green_native = to_native(BASIC_WORKFLOW)
    assert_valid_native(green_native)
    _dump_with_exit_code(green_native, 0, "basic_native")

    invalid_format2_no_format_dict = _deep_copy(green_format2)
    del invalid_format2_no_format_dict["class"]
    _dump_with_exit_code(invalid_format2_no_format_dict, 2, "format2_no_class")

    invalid_ga_no_format_dict = _deep_copy(green_native)
    del invalid_ga_no_format_dict["a_galaxy_workflow"]
    _dump_with_exit_code(invalid_ga_no_format_dict, 2, "native_no_class")

    invalid_ga_steps_not_order_index_dict = _deep_copy(green_native)
    steps = invalid_ga_steps_not_order_index_dict["steps"]
    step_0 = steps.pop("0")
    steps["moo_0"] = step_0
    _dump_with_exit_code(invalid_ga_steps_not_order_index_dict, 2, "native_step_not_order_index")

    invalid_ga_no_steps = _deep_copy(green_native)
    invalid_ga_no_steps.pop("steps")
    _dump_with_exit_code(invalid_ga_no_steps, 2, "native_no_steps")

    invalid_format2_no_steps_dict = _deep_copy(green_format2)
    del invalid_format2_no_steps_dict["steps"]
    _dump_with_exit_code(invalid_format2_no_steps_dict, 2, "format2_no_steps")

    red_format2_step_errors = _deep_copy(green_format2)
    red_format2_step_errors["steps"]["cat"]["errors"] = "Tool is not installed."
    _dump_with_exit_code(red_format2_step_errors, 1, "format2_step_errors")

    red_native_step_errors = _deep_copy(green_native)
    red_native_step_errors["steps"]["1"]["errors"] = "Tool is not installed."
    _dump_with_exit_code(red_native_step_errors, 1, "native_step_errors")

    red_ga_no_outputs = _deep_copy(green_native)
    red_ga_no_outputs_steps = red_ga_no_outputs.get("steps")
    for step in red_ga_no_outputs_steps.values():
        step.pop("workflow_outputs", None)
    _dump_with_exit_code(red_ga_no_outputs, 1, "native_no_outputs")

    red_ga_no_output_labels = _deep_copy(green_native)
    red_ga_no_output_labels_steps = red_ga_no_output_labels.get("steps")
    for step in red_ga_no_output_labels_steps.values():
        for workflow_output in step.get("workflow_outputs", []):
            workflow_output["label"] = None
    _dump_with_exit_code(red_ga_no_output_labels, 1, "native_no_output_labels")

    # gotta call this a format error to implement Process in schema...
    red_format2_no_outputs = _deep_copy(green_format2)
    del red_format2_no_outputs["outputs"]
    _dump_with_exit_code(red_format2_no_outputs, 2, "format2_no_output")

    green_format2_rules = ordered_load(RULES_TOOL)
    _dump_with_exit_code(green_format2_rules, 0, "format2_rules")

    green_native_rules = to_native(RULES_TOOL)
    _dump_with_exit_code(green_native_rules, 0, "native_format")

    green_format2_repeat = ordered_load(WORKFLOW_WITH_REPEAT)
    _dump_with_exit_code(green_format2_repeat, 0, "format2_repeat")
    green_native_rules = to_native(WORKFLOW_WITH_REPEAT)
    _dump_with_exit_code(green_native_rules, 0, "native_repeat")

    green_format2_nested = ordered_load(NESTED_WORKFLOW)
    _dump_with_exit_code(green_format2_nested, 0, "format2_nested")
    green_native_nested = to_native(NESTED_WORKFLOW)
    _dump_with_exit_code(green_native_nested, 0, "native_nested")

    invalid_format2_nested = _deep_copy(green_format2_nested)
    del invalid_format2_nested["steps"]["nested_workflow"]["run"]["steps"]
    _dump_with_exit_code(invalid_format2_nested, 2, "format2_nested_no_steps")

    invalid_native_nested = _deep_copy(green_native_nested)
    del invalid_native_nested["steps"]['2']['subworkflow']['steps']
    _dump_with_exit_code(invalid_native_nested, 2, "native_nested_no_steps")

    green_format2_runtime_inputs = ordered_load(RUNTIME_INPUTS)
    _dump_with_exit_code(green_format2_runtime_inputs, 0, "format2_runtime_inputs")
    green_native_runtime_inputs = to_native(RUNTIME_INPUTS)
    _dump_with_exit_code(green_native_runtime_inputs, 0, "native_runtime_inputs")

    green_format2_runtime_inputs = ordered_load(RUNTIME_INPUTS)
    invalid_format2_runtime_inputs_type = _deep_copy(green_format2_runtime_inputs)
    invalid_format2_runtime_inputs_type['steps']['random']['runtime_inputs'][0] = 5
    _dump_with_exit_code(invalid_format2_runtime_inputs_type, 2, "format2_runtime_inputs_invalid_type")

    green_format2_pja = ordered_load(PJA_1)
    _dump_with_exit_code(green_format2_runtime_inputs, 0, "format2_pja1")

    invalid_format2_pja_hide_type = _deep_copy(green_format2_pja)
    invalid_format2_pja_hide_type['steps']['first_cat']['out']['out_file1']['hide'] = "moocow"
    _dump_with_exit_code(invalid_format2_pja_hide_type, 2, "format2_pja_hide_invalid_type")


def test_lint_ga_basic():
    assert main(["lint", os.path.join(TEST_PATH, "wf3-shed-tools-raw.ga")]) == 1  # no outputs


def test_lint_ga_unicycler():
    assert main(["lint", os.path.join(TEST_PATH, "unicycler.ga")]) == 0


def test_lint_ga_unicycler_missing_tools():
    # only difference is one missing tool.
    assert main(["lint", os.path.join(TEST_PATH, "unicycler-hacked-no-tool.ga")]) == 1


def test_lint_ga_unicycler():
    assert main(["lint", os.path.join(TEST_PATH, "ecoli-comparison.ga")]) == 1  # no outputs


def test_lint_examples():
    for file_name in os.listdir(TEST_EXAMPLES):
        file_path = os.path.join(TEST_EXAMPLES, file_name)
        expected_exit_code = int(file_name[0])
        actual_exit_code = main(["lint", file_path])
        if actual_exit_code != expected_exit_code:
            contents = open(file_path, "r").read()
            template = "File [%s] didn't lint properly - expected exit code [%d], got [%d]. Contents:\n%s"
            raise AssertionError(template % (file_name, expected_exit_code, actual_exit_code, contents))


def _dump_with_exit_code(as_dict, exit_code, description):
    if not os.path.exists(TEST_EXAMPLES):
        os.makedirs(TEST_EXAMPLES)
    with open(os.path.join(TEST_EXAMPLES, "%d_%s.yml" % (exit_code, description)), "w") as fd:
        ordered_dump(as_dict, fd)
        fd.flush()
