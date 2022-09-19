import json
import os

from gxformat2._scripts import ensure_format2_from_path
from gxformat2.converter import main
from gxformat2.lint import lint_ga_path
from gxformat2.linting import LintContext
from gxformat2.yaml import ordered_dump
from ._helpers import TEST_PATH, to_example_path
from .example_wfs import (
    BASIC_WORKFLOW,
    INT_INPUT,
    MULTI_DATA_INPUT_WORKFLOW,
)

EXAMPLES_DIR_NAME = "native"


def test_basic_workflow():
    format2_path = to_example_path("basic", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(BASIC_WORKFLOW)
    out = _run_example_path(format2_path)
    with open(out) as f:
        as_native = json.load(f)
    assert as_native["name"] == "Simple workflow"
    assert as_native["annotation"] == "Simple workflow that no-op cats a file and then selects 10 random lines.\n"
    assert as_native.get("label") is None


def test_double_convert_sars_wf():
    sars_example = os.path.join(TEST_PATH, "sars-cov-2-variant-calling.ga")
    workflow_dict = ensure_format2_from_path(sars_example)
    format2_path = to_example_path(sars_example, EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        ordered_dump(workflow_dict, f)

    out = _run_example_path(format2_path)
    lint_context = LintContext()
    lint_ga_path(lint_context, out)


def test_int_input():
    format2_path = to_example_path("int_example", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(INT_INPUT)
    out = _run_example_path(format2_path)
    with open(out) as f:
        as_native = json.load(f)

    int_step = as_native["steps"]["1"]
    assert int_step["type"] == "parameter_input"
    assert json.loads(int_step["tool_state"])["parameter_type"] == "integer"


def test_multi_data_input():
    format2_path = to_example_path("muti_data_example", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(MULTI_DATA_INPUT_WORKFLOW)
    out = _run_example_path(format2_path)
    with open(out) as f:
        as_native = json.load(f)
    multi_data_step = as_native["steps"]["2"]
    assert len(multi_data_step["input_connections"]["input1"]) == 2


def _run_example_path(path):
    out = _examples_path_for(path)
    main(argv=[path, out])
    return out


def _examples_path_for(workflow_path):
    return to_example_path(workflow_path, EXAMPLES_DIR_NAME, "ga")
