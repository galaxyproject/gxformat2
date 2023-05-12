"""Test exporting Galaxy workflow to abstract CWL syntax."""
import os

from cwltool.context import (
    getdefault,
    LoadingContext,
)
from cwltool.main import (
    default_loader,
    fetch_document,
    resolve_and_validate_document,
    tool_resolver,
)

from gxformat2.abstract import CWL_VERSION, from_dict
from gxformat2.yaml import ordered_dump, ordered_load
from ._helpers import TEST_PATH, to_example_path
from .example_wfs import (
    BASIC_WORKFLOW,
    FLOAT_INPUT_DEFAULT,
    INT_INPUT,
    NESTED_WORKFLOW,
    OPTIONAL_INPUT,
    PJA_1,
    RULES_TOOL,
    RUNTIME_INPUTS,
    STRING_INPUT,
    WORKFLOW_WITH_REPEAT,
)
from .test_normalize import _both_formats

# double converting nested workflow doesn't work right, bug in gxformat2
# unrelated to abstract I think.
EXAMPLES = {
    "BASIC_WORKFLOW": BASIC_WORKFLOW,
    "FLOAT_INPUT_DEFAULT": FLOAT_INPUT_DEFAULT,
    "INT_INPUT": INT_INPUT,
    # "NESTED_WORKFLOW": NESTED_WORKFLOW,
    "OPTIONAL_INPUT": OPTIONAL_INPUT,
    "PJA_1": PJA_1,
    "RULES_TOOL": RULES_TOOL,
    "RUNTIME_INPUTS": RUNTIME_INPUTS,
    "STRING_INPUT": STRING_INPUT,
    "WORKFLOW_WITH_REPEAT": WORKFLOW_WITH_REPEAT,
}

# TODO:
# - Ensure when reading native format - output information is included,
#   not needed for concise format2 but would make the CWL more authentic
# - Fix bug in converted nested workflow that results in the following tests
#   breaking.
# - Write test around RUNTIME_INPUTs - translate it to string input.
# - Write test and handle $links embedded in Format2 workflows


def test_abstract_export():
    for name, example in EXAMPLES.items():
        format2, native = _both_formats(example)
        _run_example(format2, _examples_path_for(f"{name}_from_format2.cwl"))
        _run_example(native, _examples_path_for(f"{name}_from_native.cwl"))


def test_basic_workflow():
    for as_dict in _both_formats(BASIC_WORKFLOW):
        abstract_as_dict = from_dict(as_dict)
        assert abstract_as_dict["label"] == "Simple workflow"
        assert abstract_as_dict["doc"] == "Simple workflow that no-op cats a file and then selects 10 random lines.\n"
        assert abstract_as_dict["steps"]["cat"]["doc"] == "cat doc"


def test_to_cwl_optional():
    for as_dict in _both_formats(OPTIONAL_INPUT):
        abstract_as_dict = from_dict(as_dict)
        assert abstract_as_dict["inputs"]["the_input"]["type"] == "File?"


def test_to_cwl_array():
    for as_dict in _both_formats(RULES_TOOL):
        abstract_as_dict = from_dict(as_dict)
        assert abstract_as_dict["inputs"]["input_c"]["type"] == "File[]"


def test_nested_workflow():
    path = _examples_path_for("nested_format2.cwl")
    _run_example(ordered_load(NESTED_WORKFLOW), out=path)


def test_sars_covid_example():
    sars_example = os.path.join(TEST_PATH, "sars-cov-2-variant-calling.ga")
    _run_example_path(sars_example)


def test_no_input_label_example():
    no_input_label = os.path.join(TEST_PATH, "basic_without_step_input_label.ga")
    _run_example_path(no_input_label)


def test_int_inputs():
    for as_dict in _both_formats(INT_INPUT):
        abstract_as_dict = from_dict(as_dict)
        assert abstract_as_dict["inputs"]["num_lines"]["type"] == "int"


def test_float_inputs():
    for as_dict in _both_formats(FLOAT_INPUT_DEFAULT):
        abstract_as_dict = from_dict(as_dict)
        assert abstract_as_dict["inputs"]["num_lines"]["type"] == "float"
        assert abstract_as_dict["inputs"]["num_lines"]["default"] == 6.0


def test_string_inputs():
    for as_dict in _both_formats(STRING_INPUT):
        abstract_as_dict = from_dict(as_dict)
        assert abstract_as_dict["inputs"]["seed"]["type"] == "string"
        assert abstract_as_dict["inputs"]["seed"]["default"] == "mycooldefault"


def _run_example_path(path):
    out = _examples_path_for(path)
    with open(path) as f:
        return _run_example(ordered_load(f), out)


def _run_example(as_dict, out=None):
    if not out:
        out = _examples_path_for("test.cwl")
    abstract_as_dict = from_dict(as_dict)
    with open(out, "w") as f:
        ordered_dump(abstract_as_dict, f)

    check_abstract_def(abstract_as_dict)

    # validate format2 workflows
    enable_dev = "dev" in CWL_VERSION
    loadingContext = LoadingContext()
    loadingContext.enable_dev = enable_dev
    loadingContext.loader = default_loader(
        loadingContext.fetcher_constructor,
        enable_dev=enable_dev,
    )
    loadingContext.resolver = getdefault(loadingContext.resolver, tool_resolver)
    loadingContext, workflowobj, uri = fetch_document(out, loadingContext)
    loadingContext, uri = resolve_and_validate_document(
        loadingContext,
        workflowobj,
        uri,
    )
    return abstract_as_dict


def check_abstract_def(abstract_as_dict):
    assert abstract_as_dict["class"] == "Workflow"
    assert abstract_as_dict["cwlVersion"] == CWL_VERSION
    steps = abstract_as_dict["steps"]
    if isinstance(steps, dict):
        steps = steps.values()
    for step_def in steps:
        assert "run" in step_def
        run = step_def["run"]
        assert "in" in step_def
        assert isinstance(step_def["in"], (dict, list))
        assert run["class"] in ["Operation", "Workflow"]
        assert "out" in step_def
        assert isinstance(step_def["out"], list)


def _examples_path_for(workflow_path):
    return to_example_path(workflow_path, "abstractcwl", "cwl")
