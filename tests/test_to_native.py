import json

from gxformat2._scripts import ensure_format2_from_path
from gxformat2.converter import ImportOptions, main, python_to_workflow
from gxformat2.lint import lint_ga_path
from gxformat2.linting import LintContext
from gxformat2.yaml import ordered_dump, ordered_load
from ._helpers import example_path, MockGalaxyInterface, to_example_path
from .example_wfs import (
    BASIC_WORKFLOW,
    INT_INPUT,
    MULTI_DATA_INPUT_WORKFLOW,
    MULTI_STRING_INPUT_WORKFLOW,
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
    sars_example = example_path("real-sars-cov2-variant-calling.ga")
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


def test_multiple_string():
    format2_path = to_example_path("multi_string_example", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(MULTI_STRING_INPUT_WORKFLOW)
    out = _run_example_path(format2_path)
    with open(out) as f:
        as_native = json.load(f)
    multi_text_step = as_native["steps"]["0"]
    tool_state = json.loads(multi_text_step["tool_state"])
    assert tool_state["parameter_type"] == "text"
    assert tool_state["multiple"]


def test_unencoded_tool_state():
    """Test that encode_tool_state_json=False produces dict tool_state instead of JSON string."""
    import_options = ImportOptions()
    import_options.encode_tool_state_json = False
    format2_path = to_example_path("unencoded_basic", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(BASIC_WORKFLOW)
    with open(format2_path) as f:
        as_python = ordered_load(f)
    as_native = python_to_workflow(as_python, MockGalaxyInterface(), import_options=import_options)

    for step in as_native["steps"].values():
        tool_state = step.get("tool_state")
        if tool_state is not None:
            assert isinstance(tool_state, dict), f"Expected dict tool_state, got {type(tool_state)}"


def test_unencoded_int_input():
    """Test that encode_tool_state_json=False preserves parameter values as dicts."""
    import_options = ImportOptions()
    import_options.encode_tool_state_json = False
    format2_path = to_example_path("unencoded_int", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(INT_INPUT)
    with open(format2_path) as f:
        as_python = ordered_load(f)
    as_native = python_to_workflow(as_python, MockGalaxyInterface(), import_options=import_options)

    int_step = as_native["steps"]["1"]
    tool_state = int_step["tool_state"]
    assert isinstance(tool_state, dict)
    assert tool_state["parameter_type"] == "integer"


def test_native_state_encoder_callback_called():
    """Test that native_state_encoder callback is called for tool steps with state."""
    import_options = ImportOptions()
    called_with = []

    def _encoder(step, state):
        called_with.append((step.get("tool_id"), dict(state)))
        return {k: json.dumps(v) for k, v in state.items()}

    import_options.native_state_encoder = _encoder
    format2_path = to_example_path("encoder_basic", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(INT_INPUT)
    with open(format2_path) as f:
        as_python = ordered_load(f)
    python_to_workflow(as_python, MockGalaxyInterface(), import_options=import_options)

    assert len(called_with) > 0
    assert called_with[0][0] == "random_lines1"


def test_native_state_encoder_callback_none_fallback():
    """Test that returning None falls back to default json.dumps encoding."""
    import_options = ImportOptions()
    import_options.native_state_encoder = lambda step, state: None

    format2_path = to_example_path("encoder_none", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(INT_INPUT)
    with open(format2_path) as f:
        as_python = ordered_load(f)
    as_native = python_to_workflow(as_python, MockGalaxyInterface(), import_options=import_options)

    # Should produce same result as without callback
    format2_path2 = to_example_path("encoder_none2", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path2, "w") as f:
        f.write(INT_INPUT)
    with open(format2_path2) as f:
        as_python2 = ordered_load(f)
    as_native2 = python_to_workflow(as_python2, MockGalaxyInterface())

    # Compare tool_state of the tool step
    for step_id in as_native["steps"]:
        step = as_native["steps"][step_id]
        step2 = as_native2["steps"][step_id]
        if step.get("type") == "tool":
            assert step["tool_state"] == step2["tool_state"]


def test_native_state_encoder_callback_exception_fallback():
    """Test that encoder exceptions fall back to default json.dumps encoding."""
    import_options = ImportOptions()

    def _encoder(step, state):
        raise ValueError("encoding failed")

    import_options.native_state_encoder = _encoder

    format2_path = to_example_path("encoder_exc", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(BASIC_WORKFLOW)
    with open(format2_path) as f:
        as_python = ordered_load(f)

    # Should not raise — falls back to default
    as_native = python_to_workflow(as_python, MockGalaxyInterface(), import_options=import_options)
    assert "steps" in as_native


def test_native_state_encoder_connected_values():
    """Test that encoder receives ConnectedValue markers from setup_connected_values."""
    from .example_wfs import RUNTIME_INPUTS

    import_options = ImportOptions()
    seen_states = []

    def _encoder(step, state):
        seen_states.append((step.get("tool_id"), dict(state)))
        return None  # fall back to default

    import_options.native_state_encoder = _encoder

    format2_path = to_example_path("encoder_connected", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(RUNTIME_INPUTS)
    with open(format2_path) as f:
        as_python = ordered_load(f)
    python_to_workflow(as_python, MockGalaxyInterface(), import_options=import_options)

    # RUNTIME_INPUTS has random_lines1 with state containing $link for input
    random_lines_state = None
    for tool_id, state in seen_states:
        if tool_id == "random_lines1":
            random_lines_state = state
            break
    assert random_lines_state is not None
    # 'input' was a $link in state, so setup_connected_values should have replaced it
    assert random_lines_state.get("input") == {"__class__": "ConnectedValue"}


def test_native_state_encoder_custom_encoding():
    """Test that encoder result is used in tool_state."""
    import_options = ImportOptions()

    def _encoder(step, state):
        # Custom encoding: wrap every value in a tag
        return {k: json.dumps({"custom_encoded": v}) for k, v in state.items()}

    import_options.native_state_encoder = _encoder

    format2_path = to_example_path("encoder_custom", EXAMPLES_DIR_NAME, "gxwf.yml")
    with open(format2_path, "w") as f:
        f.write(BASIC_WORKFLOW)
    with open(format2_path) as f:
        as_python = ordered_load(f)
    as_native = python_to_workflow(as_python, MockGalaxyInterface(), import_options=import_options)

    # Find the cat1 tool step
    for step in as_native["steps"].values():
        if step.get("tool_id") == "cat1":
            tool_state = json.loads(step["tool_state"])
            # __page__ is set before the callback, custom values merged on top
            assert "__page__" in tool_state
            break


def _run_example_path(path):
    out = _examples_path_for(path)
    main(argv=[path, out])
    return out


def _examples_path_for(workflow_path):
    return to_example_path(workflow_path, EXAMPLES_DIR_NAME, "ga")
