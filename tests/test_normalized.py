"""Tests for gxformat2.normalized models."""

from gxformat2.normalized import normalized_format2, normalized_native


class TestNormalizedFormat2Graph:
    """$graph handling in normalized_format2."""

    SIMPLE_GRAPH = {
        "format-version": "v2.0",
        "$graph": [
            {
                "id": "main",
                "class": "GalaxyWorkflow",
                "inputs": {"the_input": "data"},
                "outputs": {},
                "steps": {"cat": {"tool_id": "cat1", "in": {"input1": "the_input"}}},
            }
        ],
    }

    GRAPH_WITH_SUBWORKFLOW = {
        "format-version": "v2.0",
        "$graph": [
            {
                "id": "subworkflow1",
                "class": "GalaxyWorkflow",
                "inputs": {"inner_input": "data"},
                "outputs": {},
                "steps": {
                    "inner_tool": {
                        "tool_id": "random_lines1",
                        "in": {"input": "inner_input"},
                    }
                },
            },
            {
                "id": "main",
                "class": "GalaxyWorkflow",
                "inputs": {"outer_input": "data"},
                "outputs": {},
                "steps": {
                    "first_cat": {"tool_id": "cat1", "in": {"input1": "outer_input"}},
                    "nested_workflow": {"run": "#subworkflow1", "in": {"inner_input": "first_cat/out_file1"}},
                },
            },
        ],
    }

    def test_simple_graph_extracts_main(self):
        wf = normalized_format2(self.SIMPLE_GRAPH)
        assert wf.label is None
        assert len(wf.inputs) == 1
        assert wf.inputs[0].id == "the_input"
        assert len(wf.steps) == 1
        assert wf.steps[0].tool_id == "cat1"

    def test_graph_inlines_subworkflow_ref(self):
        wf = normalized_format2(self.GRAPH_WITH_SUBWORKFLOW)
        assert len(wf.steps) == 2
        nested = [s for s in wf.steps if s.id == "nested_workflow"][0]
        assert nested.run is not None
        assert len(nested.run.inputs) == 1
        assert nested.run.inputs[0].id == "inner_input"
        assert len(nested.run.steps) == 1
        assert nested.run.steps[0].tool_id == "random_lines1"

    def test_graph_does_not_mutate_input(self):
        import copy

        original = copy.deepcopy(self.GRAPH_WITH_SUBWORKFLOW)
        normalized_format2(self.GRAPH_WITH_SUBWORKFLOW)
        assert self.GRAPH_WITH_SUBWORKFLOW == original

    def test_graph_missing_main_raises(self):
        import pytest

        bad = {
            "format-version": "v2.0",
            "$graph": [{"id": "not_main", "class": "GalaxyWorkflow", "inputs": {}, "outputs": {}, "steps": {}}],
        }
        with pytest.raises(Exception, match="no 'main' workflow"):
            normalized_format2(bad)

    def test_graph_missing_id_raises(self):
        import pytest

        bad = {"format-version": "v2.0", "$graph": [{"class": "GalaxyWorkflow"}]}
        with pytest.raises(Exception, match="No subworkflow ID"):
            normalized_format2(bad)

    def test_graph_bad_ref_raises(self):
        import pytest

        bad = {
            "format-version": "v2.0",
            "$graph": [
                {
                    "id": "main",
                    "class": "GalaxyWorkflow",
                    "inputs": {},
                    "outputs": {},
                    "steps": {"s": {"run": "#nonexistent"}},
                }
            ],
        }
        with pytest.raises(Exception, match="not found"):
            normalized_format2(bad)


class TestNormalizedNativeBasics:
    """Basic normalized_native guarantees."""

    MINIMAL = {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "Test",
        "steps": {
            "0": {
                "id": 0,
                "type": "tool",
                "tool_id": "cat1",
                "tool_state": '{"input1": {"__class__": "ConnectedValue"}}',
            }
        },
    }

    def test_tool_state_always_dict(self):
        wf = normalized_native(self.MINIMAL)
        assert isinstance(wf.steps["0"].tool_state, dict)
        assert wf.steps["0"].tool_state["input1"] == {"__class__": "ConnectedValue"}

    def test_containers_never_none(self):
        wf = normalized_native(self.MINIMAL)
        step = wf.steps["0"]
        assert step.input_connections == {}
        assert step.inputs == []
        assert step.outputs == []
        assert step.workflow_outputs == []
        assert step.post_job_actions == {}

    def test_tags_never_none(self):
        wf = normalized_native(self.MINIMAL)
        assert wf.tags == []


class TestNormalizedFormat2Basics:
    """Basic normalized_format2 guarantees."""

    def test_dict_steps_become_list(self):
        wf = normalized_format2(
            {"class": "GalaxyWorkflow", "inputs": {}, "outputs": {}, "steps": {"s1": {"tool_id": "cat1"}}}
        )
        assert isinstance(wf.steps, list)
        assert wf.steps[0].id == "s1"

    def test_input_shorthand_expanded(self):
        wf = normalized_format2({"class": "GalaxyWorkflow", "inputs": {"x": "data"}, "outputs": {}, "steps": {}})
        assert len(wf.inputs) == 1
        assert wf.inputs[0].id == "x"

    def test_step_in_shorthand_expanded(self):
        wf = normalized_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"s": {"tool_id": "cat1", "in": {"input1": "x"}}},
            }
        )
        assert len(wf.steps[0].in_) == 1
        assert wf.steps[0].in_[0].id == "input1"
        assert wf.steps[0].in_[0].source == "x"

    def test_native_dict_auto_detected(self):
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "Test",
            "steps": {
                "0": {
                    "id": 0,
                    "type": "data_input",
                    "label": "inp",
                    "tool_state": "{}",
                    "input_connections": {},
                    "inputs": [],
                    "outputs": [],
                    "workflow_outputs": [],
                }
            },
        }
        wf = normalized_format2(native)
        assert len(wf.inputs) >= 1
