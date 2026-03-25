"""Tests for gxformat2.normalized models."""

import base64
import copy

import pytest
import yaml

from gxformat2.normalized import (
    expanded_format2,
    expanded_native,
    ExpandedFormat2,
    ExpandedNativeWorkflow,
    normalized_format2,
    normalized_native,
)
from gxformat2.options import ConversionOptions
from gxformat2.to_format2 import ensure_format2


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
        original = copy.deepcopy(self.GRAPH_WITH_SUBWORKFLOW)
        normalized_format2(self.GRAPH_WITH_SUBWORKFLOW)
        assert self.GRAPH_WITH_SUBWORKFLOW == original

    def test_graph_missing_main_raises(self):
        bad = {
            "format-version": "v2.0",
            "$graph": [{"id": "not_main", "class": "GalaxyWorkflow", "inputs": {}, "outputs": {}, "steps": {}}],
        }
        with pytest.raises(Exception, match="no 'main' workflow"):
            normalized_format2(bad)

    def test_graph_missing_id_raises(self):
        bad = {"format-version": "v2.0", "$graph": [{"class": "GalaxyWorkflow"}]}
        with pytest.raises(Exception, match="No subworkflow ID"):
            normalized_format2(bad)

    def test_graph_bad_ref_raises(self):
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

    def test_url_run_passes_through(self):
        wf = normalized_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"nested": {"run": "https://example.com/wf.ga", "in": {"x": "x"}}},
            }
        )
        assert wf.steps[0].run == "https://example.com/wf.ga"


INNER_WORKFLOW = {
    "class": "GalaxyWorkflow",
    "inputs": {"inner_input": "data"},
    "outputs": {},
    "steps": {"inner_tool": {"tool_id": "random_lines1", "in": {"input": "inner_input"}}},
}

INNER_NATIVE = {
    "a_galaxy_workflow": "true",
    "format-version": "0.1",
    "name": "Inner",
    "steps": {
        "0": {
            "id": 0,
            "type": "data_input",
            "label": "inner_input",
            "tool_state": "{}",
            "input_connections": {},
            "inputs": [],
            "outputs": [],
            "workflow_outputs": [],
        },
        "1": {
            "id": 1,
            "type": "tool",
            "tool_id": "random_lines1",
            "input_connections": {"input": {"id": 0, "output_name": "output"}},
        },
    },
}


class TestExpandedFormat2:
    """expanded_format2 resolves references."""

    def test_inline_subworkflow_preserved(self):
        wf = expanded_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"nested": {"run": INNER_WORKFLOW, "in": {"x": "x"}}},
            }
        )
        assert isinstance(wf, ExpandedFormat2)
        assert wf.steps[0].run is not None
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_url_resolved_via_resolver(self):
        def mock_resolver(url):
            assert url == "https://example.com/wf.yml"
            return INNER_WORKFLOW.copy()

        opts = ConversionOptions(url_resolver=mock_resolver)
        wf = expanded_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"nested": {"run": "https://example.com/wf.yml", "in": {"x": "x"}}},
            },
            options=opts,
        )
        assert isinstance(wf, ExpandedFormat2)
        assert wf.steps[0].run is not None
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_base64_url_resolved(self):
        encoded = base64.b64encode(yaml.dump(INNER_WORKFLOW).encode()).decode()
        wf = expanded_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"nested": {"run": f"base64://{encoded}", "in": {"x": "x"}}},
            },
        )
        assert wf.steps[0].run is not None
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_import_resolved(self, tmp_path):
        inner_path = tmp_path / "inner.gxwf.yml"
        inner_path.write_text(yaml.dump(INNER_WORKFLOW))

        opts = ConversionOptions(workflow_directory=str(tmp_path))
        wf = expanded_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"nested": {"run": {"@import": "inner.gxwf.yml"}, "in": {"x": "x"}}},
            },
            options=opts,
        )
        assert wf.steps[0].run is not None
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_cycle_detection(self):
        call_count = 0

        def cyclic_resolver(url):
            nonlocal call_count
            call_count += 1
            return {
                "class": "GalaxyWorkflow",
                "inputs": {},
                "outputs": {},
                "steps": {"s": {"run": url}},
            }

        opts = ConversionOptions(url_resolver=cyclic_resolver)
        with pytest.raises(ValueError, match="Circular"):
            expanded_format2(
                {
                    "class": "GalaxyWorkflow",
                    "inputs": {},
                    "outputs": {},
                    "steps": {"s": {"run": "https://example.com/cyclic.yml"}},
                },
                options=opts,
            )

    def test_steps_without_run_unchanged(self):
        wf = expanded_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"cat": {"tool_id": "cat1", "in": {"input1": "x"}}},
            }
        )
        assert wf.steps[0].run is None
        assert wf.steps[0].tool_id == "cat1"


class TestEnsureFormat2Expansion:
    """ensure_format2 with expand=True vs expand=False."""

    def _base64_workflow(self, inner=None):
        inner = inner or INNER_WORKFLOW
        encoded = base64.b64encode(yaml.dump(inner).encode()).decode()
        return {
            "class": "GalaxyWorkflow",
            "inputs": {"x": "data"},
            "outputs": {},
            "steps": {"nested": {"run": f"base64://{encoded}", "in": {"x": "x"}}},
        }

    def test_no_expand_leaves_run_as_string(self):
        wf = ensure_format2(self._base64_workflow())
        step = wf.steps[0]
        assert isinstance(step.run, str)
        assert step.run.startswith("base64://")
        assert step.is_subworkflow_step

    def test_expand_resolves_base64_run(self):
        wf = ensure_format2(self._base64_workflow(), expand=True)
        step = wf.steps[0]
        assert isinstance(step.run, ExpandedFormat2)
        assert step.run.steps[0].tool_id == "random_lines1"
        assert step.is_subworkflow_step

    def test_expand_resolves_file_run(self, tmp_path):
        from gxformat2.to_format2 import ensure_format2

        inner_path = tmp_path / "inner.gxwf.yml"
        inner_path.write_text(yaml.dump(INNER_WORKFLOW))
        outer = {
            "class": "GalaxyWorkflow",
            "inputs": {"x": "data"},
            "outputs": {},
            "steps": {"nested": {"run": "inner.gxwf.yml", "in": {"x": "x"}}},
        }
        opts = ConversionOptions(workflow_directory=str(tmp_path))
        wf = ensure_format2(outer, options=opts, expand=True)
        assert isinstance(wf.steps[0].run, ExpandedFormat2)
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_no_expand_leaves_file_run_as_string(self):
        from gxformat2.to_format2 import ensure_format2

        outer = {
            "class": "GalaxyWorkflow",
            "inputs": {"x": "data"},
            "outputs": {},
            "steps": {"nested": {"run": "inner.gxwf.yml", "in": {"x": "x"}}},
        }
        wf = ensure_format2(outer)
        assert wf.steps[0].run == "inner.gxwf.yml"
        assert wf.steps[0].is_subworkflow_step

    def test_expand_nested_base64(self):
        """Nested subworkflow: outer run refs base64 which itself has an inline subworkflow."""
        from gxformat2.to_format2 import ensure_format2

        inner_with_sub = {
            "class": "GalaxyWorkflow",
            "inputs": {"y": "data"},
            "outputs": {},
            "steps": {
                "inner_sub": {
                    "run": INNER_WORKFLOW,
                    "in": {"inner_input": "y"},
                },
            },
        }
        wf = ensure_format2(self._base64_workflow(inner_with_sub), expand=True)
        step = wf.steps[0]
        assert isinstance(step.run, ExpandedFormat2)
        inner_step = step.run.steps[0]
        assert isinstance(inner_step.run, ExpandedFormat2)
        assert inner_step.run.steps[0].tool_id == "random_lines1"


class TestExpandedNative:
    """expanded_native resolves subworkflow references."""

    def test_inline_subworkflow_expanded(self):
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "Outer",
            "steps": {
                "0": {"id": 0, "type": "data_input", "label": "inp", "tool_state": "{}"},
                "1": {
                    "id": 1,
                    "type": "subworkflow",
                    "subworkflow": INNER_NATIVE,
                },
            },
        }
        wf = expanded_native(native)
        assert isinstance(wf, ExpandedNativeWorkflow)
        assert wf.steps["1"].subworkflow is not None
        assert wf.steps["1"].subworkflow.steps["1"].tool_id == "random_lines1"

    def test_url_content_id_resolved(self):
        def mock_resolver(url):
            return INNER_NATIVE.copy()

        opts = ConversionOptions(url_resolver=mock_resolver)
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "Outer",
            "steps": {
                "0": {"id": 0, "type": "data_input", "label": "inp", "tool_state": "{}"},
                "1": {
                    "id": 1,
                    "type": "subworkflow",
                    "content_id": "https://example.com/inner.ga",
                },
            },
        }
        wf = expanded_native(native, options=opts)
        assert wf.steps["1"].subworkflow is not None
        assert wf.steps["1"].subworkflow.steps["1"].tool_id == "random_lines1"

    def test_non_url_content_id_unchanged(self):
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "Outer",
            "steps": {
                "0": {
                    "id": 0,
                    "type": "subworkflow",
                    "content_id": "$local_ref",
                },
            },
        }
        wf = expanded_native(native)
        assert wf.steps["0"].subworkflow is None
        assert wf.steps["0"].content_id == "$local_ref"


NATIVE_INNER = {
    "a_galaxy_workflow": "true",
    "format-version": "0.1",
    "name": "NativeInner",
    "steps": {
        "0": {"id": 0, "type": "data_input", "label": "inner_input", "tool_state": "{}"},
        "1": {
            "id": 1,
            "type": "tool",
            "tool_id": "random_lines1",
            "tool_state": "{}",
            "input_connections": {"input": {"id": 0, "output_name": "output"}},
        },
    },
}


class TestCrossFormatExpansion:
    """Expansion converts across formats when needed."""

    def test_format2_fetches_native_url(self):
        """Format2 step with run: URL that returns native .ga content."""

        def mock_resolver(url):
            return NATIVE_INNER

        opts = ConversionOptions(url_resolver=mock_resolver)
        wf = expanded_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"sub": {"run": "https://example.com/inner.ga", "in": {"x": "x"}}},
            },
            options=opts,
        )
        assert isinstance(wf.steps[0].run, ExpandedFormat2)
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_format2_fetches_native_base64(self):
        """Format2 step with run: base64 that contains native .ga content."""
        encoded = base64.b64encode(yaml.dump(NATIVE_INNER).encode()).decode()
        wf = expanded_format2(
            {
                "class": "GalaxyWorkflow",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {"sub": {"run": f"base64://{encoded}", "in": {"x": "x"}}},
            },
        )
        assert isinstance(wf.steps[0].run, ExpandedFormat2)
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_native_fetches_format2_url(self):
        """Native step with content_id URL that returns format2 content."""

        def mock_resolver(url):
            return INNER_WORKFLOW

        opts = ConversionOptions(url_resolver=mock_resolver)
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "Outer",
            "steps": {
                "0": {"id": 0, "type": "data_input", "label": "inp", "tool_state": "{}"},
                "1": {
                    "id": 1,
                    "type": "subworkflow",
                    "content_id": "https://example.com/inner.gxwf.yml",
                },
            },
        }
        wf = expanded_native(native, options=opts)
        assert isinstance(wf.steps["1"].subworkflow, ExpandedNativeWorkflow)
        assert wf.steps["1"].subworkflow.steps["1"].tool_id == "random_lines1"

    def test_fetch_failure_is_fatal(self):
        """Fetch failure raises instead of silently leaving as reference."""

        def failing_resolver(url):
            raise ConnectionError("unreachable")

        opts = ConversionOptions(url_resolver=failing_resolver)
        native = {
            "a_galaxy_workflow": "true",
            "format-version": "0.1",
            "name": "Outer",
            "steps": {
                "0": {
                    "id": 0,
                    "type": "subworkflow",
                    "content_id": "https://example.com/inner.ga",
                },
            },
        }
        with pytest.raises(ConnectionError):
            expanded_native(native, options=opts)
