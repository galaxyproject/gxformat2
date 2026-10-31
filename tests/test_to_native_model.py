"""Tests for gxformat2.to_native — model-returning conversion."""

from gxformat2.normalized import ensure_native, NormalizedNativeWorkflow, to_native

from .example_wfs import (
    BASIC_WORKFLOW,
    MULTI_DATA_INPUT_WORKFLOW,
    MULTI_STRING_INPUT_WORKFLOW,
)


def _to_native_model(yaml_str, **kwds):
    from gxformat2.yaml import ordered_load

    as_python = ordered_load(yaml_str)
    return to_native(as_python, **kwds)


class TestToNativeBasic:

    def test_all_tool_state_are_dicts(self):
        result = _to_native_model(BASIC_WORKFLOW)
        for step in result.steps.values():
            assert isinstance(step.tool_state, dict), f"Step {step.id} tool_state is {type(step.tool_state)}"

    def test_tool_step_has_connections(self):
        result = _to_native_model(BASIC_WORKFLOW)
        # Find a tool step
        tool_steps = [s for s in result.steps.values() if s.type_ == "tool"]
        assert len(tool_steps) > 0
        # Should have at least one input connection
        tool_step = tool_steps[0]
        assert len(tool_step.input_connections) > 0

    def test_workflow_outputs_wired(self):
        result = _to_native_model(BASIC_WORKFLOW)
        all_outputs = []
        for step in result.steps.values():
            all_outputs.extend(step.workflow_outputs)
        assert len(all_outputs) > 0

    def test_multi_data_input(self):
        result = _to_native_model(MULTI_DATA_INPUT_WORKFLOW)
        assert isinstance(result, NormalizedNativeWorkflow)

    def test_multi_string_input(self):
        result = _to_native_model(MULTI_STRING_INPUT_WORKFLOW)
        # Should have a parameter_input with multiple=True
        param_steps = [s for s in result.steps.values() if s.type_ == "parameter_input"]
        assert len(param_steps) > 0
        assert param_steps[0].tool_state.get("multiple") is True


class TestEnsureNative:

    def test_expand_true_returns_expanded_type(self):
        from gxformat2.normalized import ExpandedNativeWorkflow
        from gxformat2.yaml import ordered_load

        fmt2 = ordered_load(BASIC_WORKFLOW)
        result = ensure_native(fmt2, expand=True)
        assert isinstance(result, ExpandedNativeWorkflow)


class TestToNativePickValue:

    def test_pick_value_step(self):
        result = _to_native_model("""
class: GalaxyWorkflow
inputs:
  input1: data
  input2: data
steps:
  pick:
    type: pick_value
    in:
      data1: input1
      data2: input2
""")
        pick_steps = [s for s in result.steps.values() if s.type_ == "pick_value"]
        assert len(pick_steps) == 1
        assert pick_steps[0].tool_state.get("num_inputs", 0) >= 2


class TestToNativeUserTool:

    def test_user_defined_tool(self):
        result = _to_native_model("""
class: GalaxyWorkflow
inputs:
  the_input: data
outputs: {}
steps:
  my_tool:
    run:
      class: GalaxyUserTool
      name: My Tool
      shell_command: cat '$input1' > '$output1'
      inputs:
        - name: input1
          type: data
      outputs:
        - name: output1
    in:
      input1: the_input
""")
        tool_steps = [s for s in result.steps.values() if s.type_ == "tool"]
        assert len(tool_steps) == 1
        assert tool_steps[0].tool_representation is not None
        assert tool_steps[0].tool_representation["class"] == "GalaxyUserTool"
        assert tool_steps[0].tool_id is None
