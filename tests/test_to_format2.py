import copy
import json

from yaml import safe_load

from gxformat2.converter import python_to_workflow
from gxformat2.export import from_galaxy_native, main
from gxformat2.yaml import ordered_load
from ._helpers import example_path, to_example_path


def test_sars_covid_example():
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
    converted_path = _run_example_path(sars_example)
    with open(converted_path) as fh:
        wf = safe_load(fh)
    assert wf["steps"][1]["run"]["inputs"]["Paired Collection (fastqsanger)"]["collection_type"] == "list:paired"


def test_multi_data_example():
    example = example_path("real-multi-data-input.ga")
    converted_path = _run_example_path(example)
    with open(converted_path) as fh:
        wf = safe_load(fh)
    assert wf["steps"]["count_multi_file"]["in"]["input1"]["source"] == ["required", "optional"]


def test_multiple_string_example():
    example = example_path("real-multi-string-input.ga")
    converted_path = _run_example_path(example)
    with open(converted_path) as fh:
        wf = safe_load(fh)
    assert wf["inputs"]["multi-text"]["type"] == ["string"]


def test_compact_workflow_example():
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
    compact_path = _run_example_path(sars_example, compact=True)
    with open(compact_path) as fh:
        wf = safe_load(fh)
    assert "position" not in wf["steps"][0]


def test_dict_tool_state_export():
    """Test that from_galaxy_native handles dict-form tool_state (not JSON string)."""
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
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
    example = example_path("real-basic-without-step-input-label.ga")
    with open(example) as f:
        native_wf = json.load(f)

    # Verify the input step has no label
    assert native_wf["steps"]["0"]["label"] is None

    # Export to format2
    format2 = from_galaxy_native(copy.deepcopy(native_wf))

    # The format2 key should use the sentinel prefix
    assert "_unlabeled_input_0" in format2["inputs"]

    # Re-import to native
    native_rt = python_to_workflow(copy.deepcopy(format2))

    # The round-tripped step should have label=None, not "0" or "_unlabeled_input_0"
    assert native_rt["steps"]["0"]["label"] is None


def test_unlabeled_input_connections_round_trip():
    """Test that connections to unlabeled inputs survive round-trip."""
    example = example_path("real-basic-without-step-input-label.ga")
    with open(example) as f:
        native_wf = json.load(f)

    format2 = from_galaxy_native(copy.deepcopy(native_wf))

    # The cat step should reference the unlabeled input via sentinel
    cat_step = format2["steps"][0]
    assert "_unlabeled_input_0" in str(cat_step["in"]["input1"]["source"])

    # Re-import and verify connection still works
    native_rt = python_to_workflow(copy.deepcopy(format2))
    cat_step_rt = native_rt["steps"]["1"]
    input_conn = cat_step_rt["input_connections"]["input1"]
    if isinstance(input_conn, list):
        assert input_conn[0]["id"] == 0
    else:
        assert input_conn["id"] == 0


def test_convert_tool_state_callback_called():
    """Test that convert_tool_state callback is called for tool steps on export."""
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
    with open(sars_example) as f:
        native_wf = json.load(f)

    called_tool_ids = []

    def _callback(native_step):
        called_tool_ids.append(native_step.get("tool_id"))
        return {"custom_key": "custom_value"}

    result = from_galaxy_native(native_wf, convert_tool_state=_callback)

    # Callback should have been called for each tool step
    assert len(called_tool_ids) > 0
    # Tool steps should have "state" not "tool_state"
    for step in _tool_steps(result):
        assert "state" in step
        assert "tool_state" not in step
        assert step["state"] == {"custom_key": "custom_value"}


def test_convert_tool_state_callback_none_fallback():
    """Test that returning None from callback falls back to default tool_state."""
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
    with open(sars_example) as f:
        native_wf = json.load(f)

    def _callback(native_step):
        return None

    result = from_galaxy_native(native_wf, convert_tool_state=_callback)

    # All tool steps should have tool_state (default path)
    for step in _tool_steps(result):
        assert "tool_state" in step
        assert "state" not in step


def test_convert_tool_state_callback_exception_fallback():
    """Test that callback exceptions fall back to default tool_state."""
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
    with open(sars_example) as f:
        native_wf = json.load(f)

    def _callback(native_step):
        raise ValueError("conversion failed")

    result = from_galaxy_native(native_wf, convert_tool_state=_callback)

    # All tool steps should have tool_state (fallback on exception)
    for step in _tool_steps(result):
        assert "tool_state" in step
        assert "state" not in step


def test_convert_tool_state_callback_selective():
    """Test that callback can convert some steps and fall back on others."""
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
    with open(sars_example) as f:
        native_wf = json.load(f)

    target_tool_id = "__MERGE_COLLECTION__"

    def _callback(native_step):
        if native_step.get("tool_id") == target_tool_id:
            return {"converted": True}
        return None

    result = from_galaxy_native(native_wf, convert_tool_state=_callback)

    tool_steps = list(_tool_steps(result))
    converted_count = 0
    fallback_count = 0
    for step in tool_steps:
        if step.get("state") == {"converted": True}:
            converted_count += 1
            assert "tool_state" not in step
        else:
            fallback_count += 1
            assert "tool_state" in step
            assert "state" not in step
    assert converted_count >= 1
    assert fallback_count >= 1


def test_convert_tool_state_connections_always_present():
    """Test that _convert_input_connections runs regardless of callback."""
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
    with open(sars_example) as f:
        native_wf = json.load(f)

    def _callback(native_step):
        return {"converted": True}

    result = from_galaxy_native(native_wf, convert_tool_state=_callback)

    # Tool steps with connections should still have "in" populated by _convert_input_connections
    has_connections = False
    for step in _tool_steps(result):
        if step.get("in"):
            has_connections = True
            break
    assert has_connections, "Expected at least one tool step with input connections"


def test_convert_tool_state_no_callback_default_unchanged():
    """Test that omitting convert_tool_state preserves original behavior."""
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
    with open(sars_example) as f:
        native_wf = json.load(f)

    result_default = from_galaxy_native(copy.deepcopy(native_wf))
    result_none = from_galaxy_native(copy.deepcopy(native_wf), convert_tool_state=None)

    # Should be identical
    assert json.dumps(result_default, sort_keys=True) == json.dumps(result_none, sort_keys=True)


def test_convert_tool_state_subworkflow_recursion():
    """Test that convert_tool_state callback is passed through to subworkflows."""
    nested_f2 = """
class: GalaxyWorkflow
inputs:
  outer_input: data
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
      steps:
        inner_cat:
          tool_id: cat1
          in:
            input1: inner_input
    in:
      inner_input: first_cat/out_file1
"""
    # Build a native workflow with a subworkflow
    f2 = ordered_load(nested_f2)
    native_wf = python_to_workflow(f2)

    called_tool_ids = []

    def _callback(native_step):
        called_tool_ids.append(native_step.get("tool_id"))
        return {"from_callback": True}

    result = from_galaxy_native(native_wf, convert_tool_state=_callback)

    # Should have been called for outer tool AND inner subworkflow tool
    assert len(called_tool_ids) == 2
    assert all(tid == "cat1" for tid in called_tool_ids)

    # Check inner subworkflow step also got state from callback
    subworkflow_step = None
    for step in result.get("steps", {}).values() if isinstance(result.get("steps"), dict) else result.get("steps", []):
        if isinstance(step.get("run"), dict):
            subworkflow_step = step
            break
    assert subworkflow_step is not None
    inner_steps = subworkflow_step["run"].get("steps", {})
    if isinstance(inner_steps, dict):
        inner_tool = list(inner_steps.values())[0]
    else:
        inner_tool = inner_steps[0]
    assert inner_tool.get("state") == {"from_callback": True}


def _tool_steps(format2_wf):
    """Yield tool steps from a format2 workflow (handles both dict and list steps)."""
    steps = format2_wf.get("steps", {})
    if isinstance(steps, dict):
        step_list = steps.values()
    else:
        step_list = steps
    for step in step_list:
        if step.get("tool_id"):
            yield step


def _run_example_path(path, compact=False):
    out = _examples_path_for(path)
    argv = [path, out]
    if compact:
        argv.append("--compact")
    main(argv=argv)
    return out


def _examples_path_for(workflow_path):
    return to_example_path(workflow_path, "format2", "gxwf.yml")
