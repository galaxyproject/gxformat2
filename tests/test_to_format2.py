import copy
import json
import os

from yaml import safe_load

from gxformat2.converter import python_to_workflow
from gxformat2.export import from_galaxy_native, main
from ._helpers import MockGalaxyInterface, TEST_PATH, to_example_path


def test_sars_covid_example():
    sars_example = os.path.join(TEST_PATH, "sars-cov-2-variant-calling.ga")
    converted_path = _run_example_path(sars_example)
    with open(converted_path) as fh:
        wf = safe_load(fh)
    assert wf["steps"][1]["run"]["inputs"]["Paired Collection (fastqsanger)"]["collection_type"] == "list:paired"


def test_multi_data_example():
    example = os.path.join(TEST_PATH, "muti_data_example.ga")
    converted_path = _run_example_path(example)
    with open(converted_path) as fh:
        wf = safe_load(fh)
    assert wf["steps"]["count_multi_file"]["in"]["input1"]["source"] == ["required", "optional"]


def test_multiple_string_example():
    example = os.path.join(TEST_PATH, "multi-string.ga")
    converted_path = _run_example_path(example)
    with open(converted_path) as fh:
        wf = safe_load(fh)
    assert wf["inputs"]["multi-text"]["type"] == ["string"]


def test_compact_workflow_example():
    sars_example = os.path.join(TEST_PATH, "sars-cov-2-variant-calling.ga")
    compact_path = _run_example_path(sars_example, compact=True)
    with open(compact_path) as fh:
        wf = safe_load(fh)
    assert "position" not in wf["steps"][0]


def test_dict_tool_state_export():
    """Test that from_galaxy_native handles dict-form tool_state (not JSON string)."""
    sars_example = os.path.join(TEST_PATH, "sars-cov-2-variant-calling.ga")
    with open(sars_example) as f:
        native_wf = json.load(f)

    # Convert all tool_state from JSON strings to dicts
    for step in native_wf["steps"].values():
        ts = step.get("tool_state")
        if ts and isinstance(ts, str):
            step["tool_state"] = json.loads(ts)

    # Should not raise — export handles both formats
    result = from_galaxy_native(native_wf)
    assert "steps" in result


def test_unlabeled_input_round_trip():
    """Test that unlabeled inputs preserve label=None through round-trip."""
    example = os.path.join(TEST_PATH, "basic_without_step_input_label.ga")
    with open(example) as f:
        native_wf = json.load(f)

    # Verify the input step has no label
    assert native_wf["steps"]["0"]["label"] is None

    # Export to format2
    format2 = from_galaxy_native(copy.deepcopy(native_wf))

    # The format2 key should use the sentinel prefix
    assert "_unlabeled_input_0" in format2["inputs"]

    # Re-import to native
    native_rt = python_to_workflow(copy.deepcopy(format2), MockGalaxyInterface(), None)

    # The round-tripped step should have label=None, not "0" or "_unlabeled_input_0"
    assert native_rt["steps"]["0"]["label"] is None


def test_unlabeled_input_connections_round_trip():
    """Test that connections to unlabeled inputs survive round-trip."""
    example = os.path.join(TEST_PATH, "basic_without_step_input_label.ga")
    with open(example) as f:
        native_wf = json.load(f)

    format2 = from_galaxy_native(copy.deepcopy(native_wf))

    # The cat step should reference the unlabeled input via sentinel
    cat_step = format2["steps"][0]
    assert "_unlabeled_input_0" in str(cat_step["in"]["input1"]["source"])

    # Re-import and verify connection still works
    native_rt = python_to_workflow(copy.deepcopy(format2), MockGalaxyInterface(), None)
    cat_step_rt = native_rt["steps"]["1"]
    input_conn = cat_step_rt["input_connections"]["input1"]
    if isinstance(input_conn, list):
        assert input_conn[0]["id"] == 0
    else:
        assert input_conn["id"] == 0


def _run_example_path(path, compact=False):
    out = _examples_path_for(path)
    argv = [path, out]
    if compact:
        argv.append("--compact")
    main(argv=argv)
    return out


def _examples_path_for(workflow_path):
    return to_example_path(workflow_path, "format2", "gxwf.yml")
