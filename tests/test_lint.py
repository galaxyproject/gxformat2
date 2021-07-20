import copy
import os

from gxformat2.lint import main
from gxformat2.yaml import ordered_dump, ordered_load
from ._helpers import (
    assert_valid_native,
    copy_without_workflow_output_labels,
    round_trip,
    TEST_INTEROP_EXAMPLES,
    TEST_PATH,
    to_native,
)
from .example_wfs import (
    BASIC_WORKFLOW,
    INT_INPUT,
    NESTED_WORKFLOW,
    PJA_1,
    RULES_TOOL,
    RUNTIME_INPUTS,
    STRING_INPUT,
    WORKFLOW_WITH_REPEAT,
)

_deep_copy = copy.deepcopy

TEST_LINT_EXAMPLES = os.path.join(TEST_INTEROP_EXAMPLES, "lint")

WITH_REPORT = """
class: GalaxyWorkflow
label: My Cool Workflow
inputs:
  input_1: data
  image_input: data
  input_list: collection
outputs:
  output_1:
    outputSource: first_cat/out_file1
  output_image:
    outputSource: image_cat/out_file1
steps:
  first_cat:
    tool_id: cat
    in:
      input1: input_1
  image_cat:
    tool_id: cat
    in:
      input1: image_input
  qc_step:
    tool_id: qc_stdout
    state:
      quality: 9
    in:
      input: input_1
report:
  markdown: |
    ## About This Report
    This report is generated from markdown content in the workflow YAML/JSON.
"""

WORKFLOW_VOCAB_KEYS = """
class: GalaxyWorkflow
doc: |
  Test state with keys that appear elsewhere in the salad vocab.
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
    state:
      type: 8
      name: 9
      class: NotGalaxyWorkflow
    in:
      input1: the_input
"""


def setup_module(module):
    # Setup an examples directory with examples we want to correspond to what exit codes,
    # do this so we can run same tests in Java.
    green_format2 = ordered_load(BASIC_WORKFLOW)
    _dump_with_exit_code(green_format2, 0, "basic_format2")
    green_native = to_native(BASIC_WORKFLOW)
    assert_valid_native(green_native)
    _dump_with_exit_code(green_native, 0, "basic_native")

    green_explicit_errors_null = _deep_copy(green_native)
    for step_def in green_explicit_errors_null["steps"].values():
        step_def["errors"] = None
    _dump_with_exit_code(green_explicit_errors_null, 0, "basic_native_explicit_no_errors")

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

    red_ga_no_output_labels = copy_without_workflow_output_labels(green_native)
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

    green_format2_report = ordered_load(WITH_REPORT)
    _dump_with_exit_code(green_format2_report, 0, "format2_report")
    green_native_report = to_native(WITH_REPORT)
    _dump_with_exit_code(green_native_report, 0, "native_report")

    invalid_format2_report_type = _deep_copy(green_format2_report)
    invalid_format2_report_type["report"]["markdown"] = 5
    _dump_with_exit_code(invalid_format2_report_type, 2, "format2_report_invalid_type")

    invalid_native_report_type = _deep_copy(green_native_report)
    invalid_native_report_type["report"]["markdown"] = 5
    _dump_with_exit_code(invalid_native_report_type, 2, "native_report_invalid_type")

    invalid_format2_report_markdown = _deep_copy(green_format2_report)
    invalid_format2_report_markdown["report"]["markdown"] += "\n```galaxy\ncow()\n```\n"
    _dump_with_exit_code(invalid_format2_report_markdown, 2, "format2_report_invalid_markdown")

    invalid_native_report_markdown = _deep_copy(green_native_report)
    invalid_native_report_markdown["report"]["markdown"] += "\n```galaxy\ncow()\n```\n"
    _dump_with_exit_code(invalid_native_report_markdown, 2, "native_report_invalid_markdown")

    invalid_format2_report_missing_markdown = _deep_copy(green_format2_report)
    del invalid_format2_report_missing_markdown["report"]["markdown"]
    _dump_with_exit_code(invalid_format2_report_missing_markdown, 2, "format2_report_missing_markdown")

    invalid_native_report_missing_markdown = _deep_copy(green_native_report)
    del invalid_native_report_missing_markdown["report"]["markdown"]
    _dump_with_exit_code(invalid_native_report_missing_markdown, 2, "native_report_missing_markdown")

    green_format2_vocab_keys = ordered_load(WORKFLOW_VOCAB_KEYS)
    _dump_with_exit_code(green_format2_vocab_keys, 0, "format2_vocab_keys")

    green_format2_int_input = ordered_load(INT_INPUT)
    _dump_with_exit_code(green_format2_int_input, 0, "format2_int_input")

    valid_int_default_type = _deep_copy(green_format2_int_input)
    valid_int_default_type["inputs"]["num_lines"]["default"] = 5
    _dump_with_exit_code(valid_int_default_type, 0, "format2_int_input_valid_default")

    valid_float_default_type = _deep_copy(green_format2_int_input)
    valid_float_default_type["inputs"]["num_lines"]["type"] = "float"
    valid_float_default_type["inputs"]["num_lines"]["default"] = 5.0
    _dump_with_exit_code(valid_float_default_type, 0, "format2_int_input_valid_default")

    invalid_int_default_type = _deep_copy(green_format2_int_input)
    invalid_int_default_type["inputs"]["num_lines"]["default"] = "bad_default"
    _dump_with_exit_code(invalid_int_default_type, 2, "format2_int_input_bad_default")

    invalid_float_default_type = _deep_copy(green_format2_int_input)
    invalid_float_default_type["inputs"]["num_lines"]["type"] = "float"
    invalid_float_default_type["inputs"]["num_lines"]["default"] = "bad_default"
    _dump_with_exit_code(invalid_float_default_type, 2, "format2_float_input_bad_default")

    green_format2_text_input = ordered_load(STRING_INPUT)
    _dump_with_exit_code(green_format2_text_input, 0, "format2_string_input")

    invalid_string_default_type = _deep_copy(green_format2_text_input)
    invalid_string_default_type["inputs"]["seed"]["default"] = 6
    _dump_with_exit_code(invalid_string_default_type, 2, "format2_string_input_bad_default")

    # ensure that round tripping all green format2 workflows still lint green.
    for file_name in os.listdir(TEST_LINT_EXAMPLES):
        if file_name.startswith("0_format2") and "roundtrip" not in file_name:
            roundtrip_contents = round_trip(open(os.path.join(TEST_LINT_EXAMPLES, file_name)).read())
            base = os.path.splitext(file_name)[0][len("0_"):]
            _dump_with_exit_code(roundtrip_contents, 0, base + "_roundtrip")


def test_lint_ga_basic():
    assert main(["lint", os.path.join(TEST_PATH, "wf3-shed-tools-raw.ga")]) == 1  # no outputs


def test_lint_ga_unicycler():
    assert main(["lint", os.path.join(TEST_PATH, "unicycler.ga")]) == 0


def test_lint_ga_unicycler_training():
    # no tags, fails linting
    assert main(["lint", "--training-topic", "assembly", os.path.join(TEST_PATH, "unicycler.ga")]) == 1
    # correct tag passes linting
    assert main(["lint", "--training-topic", "assembly", os.path.join(TEST_PATH, "unicycler-hacked-tags.ga")]) == 0
    # incorrect tag, fails linting
    assert main(["lint", "--training-topic", "mapping", os.path.join(TEST_PATH, "unicycler-hacked-tags.ga")]) == 1


def test_lint_ga_unicycler_missing_tools():
    # only difference is one missing tool.
    assert main(["lint", os.path.join(TEST_PATH, "unicycler-hacked-no-tool.ga")]) == 1


def test_lint_ga_unicycler_ts_tools():
    # only difference is testoolshed tool.
    assert main(["lint", os.path.join(TEST_PATH, "unicycler-hacked-testtoolshed.ga")]) == 1


def test_lint_ecoli_comparison():
    assert main(["lint", os.path.join(TEST_PATH, "ecoli-comparison.ga")]) == 1  # no outputs


def test_lint_examples():
    for file_name in os.listdir(TEST_LINT_EXAMPLES):
        file_path = os.path.join(TEST_LINT_EXAMPLES, file_name)
        expected_exit_code = int(file_name[0])
        actual_exit_code = main(["lint", file_path])
        if actual_exit_code != expected_exit_code:
            contents = open(file_path).read()
            template = "File [%s] didn't lint properly - expected exit code [%d], got [%d]. Contents:\n%s"
            raise AssertionError(template % (file_name, expected_exit_code, actual_exit_code, contents))


def _dump_with_exit_code(as_dict, exit_code, description):
    if not os.path.exists(TEST_LINT_EXAMPLES):
        os.makedirs(TEST_LINT_EXAMPLES)
    with open(os.path.join(TEST_LINT_EXAMPLES, "%d_%s.yml" % (exit_code, description)), "w") as fd:
        ordered_dump(as_dict, fd)
        fd.flush()
