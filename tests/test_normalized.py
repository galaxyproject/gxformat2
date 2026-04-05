"""Tests for gxformat2.normalized models."""

import base64
import copy

import pytest
from pydantic import ValidationError

from gxformat2.examples import load, load_contents
from gxformat2.normalized import (
    ensure_format2,
    ensure_native,
    expanded_format2,
    expanded_native,
    ExpandedFormat2,
    ExpandedNativeWorkflow,
    normalized_format2,
    normalized_native,
    to_format2,
    to_native,
    ToolReference,
)
from gxformat2.options import ConversionOptions


class TestNormalizedFormat2Graph:
    """$graph handling in normalized_format2."""

    def test_graph_does_not_mutate_input(self):
        wf_dict = load("synthetic-graph-with-subworkflow.gxwf.yml")
        original = copy.deepcopy(wf_dict)
        normalized_format2(wf_dict)
        assert wf_dict == original

    def test_graph_missing_main_raises(self):
        wf_dict = load("synthetic-graph-simple.gxwf.yml")
        wf_dict["$graph"][0]["id"] = "not_main"
        with pytest.raises(Exception, match="no 'main' workflow"):
            normalized_format2(wf_dict)

    def test_graph_missing_id_raises(self):
        wf_dict = load("synthetic-graph-simple.gxwf.yml")
        del wf_dict["$graph"][0]["id"]
        with pytest.raises(Exception, match="No subworkflow ID"):
            normalized_format2(wf_dict)

    def test_graph_bad_ref_raises(self):
        wf_dict = load("synthetic-graph-simple.gxwf.yml")
        wf_dict["$graph"][0]["steps"]["cat"]["run"] = "#nonexistent"
        with pytest.raises(Exception, match="not found"):
            normalized_format2(wf_dict)


class TestNormalizedNativeBasics:
    """Basic normalized_native guarantees."""

    def test_connected_paths(self):
        wf_dict = load("synthetic-minimal-tool.ga")
        wf_dict["steps"]["0"]["input_connections"] = {
            "input1": {"id": 1, "output_name": "output"},
        }
        wf = normalized_native(wf_dict)
        assert wf.steps["0"].connected_paths == frozenset({"input1"})


class TestNormalizedFormat2Basics:
    """Basic normalized_format2 guarantees."""

    def test_dict_steps_become_list(self):
        wf_dict = load("synthetic-input-shorthand.gxwf.yml")
        wf_dict["steps"]["s1"] = {"tool_id": "cat1"}
        wf = normalized_format2(wf_dict)
        assert isinstance(wf.steps, list)
        assert wf.steps[0].id == "s1"

    def test_connected_paths(self):
        wf_dict = load("synthetic-step-in-shorthand.gxwf.yml")
        wf_dict["steps"]["s"]["in"]["input2"] = {"default": 42}
        wf = normalized_format2(wf_dict)
        assert wf.steps[0].connected_paths == frozenset({"input1"})

    def test_connected_paths_empty(self):
        wf_dict = load("synthetic-input-shorthand.gxwf.yml")
        wf_dict["steps"]["s1"] = {"tool_id": "cat1"}
        wf = normalized_format2(wf_dict)
        assert wf.steps[0].connected_paths == frozenset()

    def test_native_dict_rejected(self):
        with pytest.raises(ValueError, match="native Galaxy workflow"):
            normalized_format2(load("synthetic-native-data-input.ga"))

    def test_native_dict_via_ensure_format2(self):
        wf = ensure_format2(load("synthetic-native-data-input.ga"))
        assert len(wf.inputs) >= 1


class TestExpandedFormat2:
    """expanded_format2 resolves references."""

    def test_inline_subworkflow_preserved(self):
        wf_dict = load("synthetic-url-run-yml.gxwf.yml")
        wf_dict["steps"]["nested"]["run"] = load("synthetic-inner-subworkflow.gxwf.yml")
        wf = expanded_format2(wf_dict)
        assert isinstance(wf, ExpandedFormat2)
        assert wf.steps[0].run is not None
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_url_resolved_via_resolver(self):
        def mock_resolver(url):
            assert url == "https://example.com/wf.yml"
            return load("synthetic-inner-subworkflow.gxwf.yml")

        opts = ConversionOptions(url_resolver=mock_resolver)
        wf = expanded_format2(load("synthetic-url-run-yml.gxwf.yml"), options=opts)
        assert isinstance(wf, ExpandedFormat2)
        assert wf.steps[0].run is not None
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_base64_url_resolved(self):
        encoded = base64.b64encode(load_contents("synthetic-inner-subworkflow.gxwf.yml").encode()).decode()
        wf_dict = load("synthetic-url-run-yml.gxwf.yml")
        wf_dict["steps"]["nested"]["run"] = f"base64://{encoded}"
        wf = expanded_format2(wf_dict)
        assert wf.steps[0].run is not None
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_import_resolved(self, tmp_path):
        inner_path = tmp_path / "inner.gxwf.yml"
        inner_path.write_text(load_contents("synthetic-inner-subworkflow.gxwf.yml"))

        wf_dict = load("synthetic-url-run-yml.gxwf.yml")
        wf_dict["steps"]["nested"]["run"] = {"@import": "inner.gxwf.yml"}
        opts = ConversionOptions(workflow_directory=str(tmp_path))
        wf = expanded_format2(wf_dict, options=opts)
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
            expanded_format2(load("synthetic-url-run-yml.gxwf.yml"), options=opts)


class TestEnsureFormat2Expansion:
    """ensure_format2 with expand=True vs expand=False."""

    def _base64_workflow(self, inner_contents=None):
        inner_contents = inner_contents or load_contents("synthetic-inner-subworkflow.gxwf.yml")
        encoded = base64.b64encode(inner_contents.encode()).decode()
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
        inner_path = tmp_path / "inner.gxwf.yml"
        inner_path.write_text(load_contents("synthetic-inner-subworkflow.gxwf.yml"))

        wf_dict = load("synthetic-url-run-yml.gxwf.yml")
        wf_dict["steps"]["nested"]["run"] = "inner.gxwf.yml"
        opts = ConversionOptions(workflow_directory=str(tmp_path))
        wf = ensure_format2(wf_dict, options=opts, expand=True)
        assert isinstance(wf.steps[0].run, ExpandedFormat2)
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_no_expand_leaves_file_run_as_string(self):
        wf_dict = load("synthetic-url-run-yml.gxwf.yml")
        wf_dict["steps"]["nested"]["run"] = "inner.gxwf.yml"
        wf = ensure_format2(wf_dict)
        assert wf.steps[0].run == "inner.gxwf.yml"
        assert wf.steps[0].is_subworkflow_step

    def test_expand_nested_base64(self):
        """Nested subworkflow: outer run refs base64 which itself has an inline subworkflow."""
        wf = ensure_format2(
            self._base64_workflow(load_contents("synthetic-inner-nested-subworkflow.gxwf.yml")),
            expand=True,
        )
        step = wf.steps[0]
        assert isinstance(step.run, ExpandedFormat2)
        inner_step = step.run.steps[0]
        assert isinstance(inner_step.run, ExpandedFormat2)
        assert inner_step.run.steps[0].tool_id == "random_lines1"


class TestExpandedNative:
    """expanded_native resolves subworkflow references."""

    def test_url_content_id_resolved(self):
        def mock_resolver(url):
            return load("synthetic-inner-subworkflow.ga")

        opts = ConversionOptions(url_resolver=mock_resolver)
        wf = expanded_native(load("synthetic-outer-url-subworkflow.ga"), options=opts)
        assert wf.steps["1"].subworkflow is not None
        assert wf.steps["1"].subworkflow.steps["1"].tool_id == "random_lines1"

    def test_non_url_content_id_unchanged(self):
        wf_dict = load("synthetic-outer-url-subworkflow.ga")
        wf_dict["steps"]["1"]["content_id"] = "$local_ref"
        wf = expanded_native(wf_dict)
        assert wf.steps["1"].subworkflow is None
        assert wf.steps["1"].content_id == "$local_ref"


class TestCrossFormatExpansion:
    """Expansion converts across formats when needed."""

    def test_format2_fetches_native_url(self):
        """Format2 step with run: URL that returns native .ga content."""

        def mock_resolver(url):
            return load("synthetic-inner-subworkflow.ga")

        opts = ConversionOptions(url_resolver=mock_resolver)
        wf = expanded_format2(load("synthetic-url-run-yml.gxwf.yml"), options=opts)
        assert isinstance(wf.steps[0].run, ExpandedFormat2)
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_format2_fetches_native_base64(self):
        """Format2 step with run: base64 that contains native .ga content."""
        encoded = base64.b64encode(load_contents("synthetic-inner-subworkflow.ga").encode()).decode()
        wf_dict = load("synthetic-url-run-yml.gxwf.yml")
        wf_dict["steps"]["nested"]["run"] = f"base64://{encoded}"
        wf = expanded_format2(wf_dict)
        assert isinstance(wf.steps[0].run, ExpandedFormat2)
        assert wf.steps[0].run.steps[0].tool_id == "random_lines1"

    def test_native_fetches_format2_url(self):
        """Native step with content_id URL that returns format2 content."""

        def mock_resolver(url):
            return load("synthetic-inner-subworkflow.gxwf.yml")

        opts = ConversionOptions(url_resolver=mock_resolver)
        wf = expanded_native(load("synthetic-outer-url-subworkflow.ga"), options=opts)
        assert isinstance(wf.steps["1"].subworkflow, ExpandedNativeWorkflow)
        assert wf.steps["1"].subworkflow.steps["1"].tool_id == "random_lines1"

    def test_fetch_failure_is_fatal(self):
        """Fetch failure raises instead of silently leaving as reference."""

        def failing_resolver(url):
            raise ConnectionError("unreachable")

        opts = ConversionOptions(url_resolver=failing_resolver)
        with pytest.raises(ConnectionError):
            expanded_native(load("synthetic-outer-url-subworkflow.ga"), options=opts)


class TestUniqueToolsFormat2:

    def test_deduplicates(self):
        wf_dict = load("synthetic-single-versioned-tool.gxwf.yml")
        wf_dict["steps"]["step2"] = dict(wf_dict["steps"]["step1"])
        wf = normalized_format2(wf_dict)
        assert wf.unique_tools == frozenset({ToolReference("cat1", "1.0")})

    def test_multiple_tools(self):
        wf_dict = load("synthetic-single-versioned-tool.gxwf.yml")
        wf_dict["steps"]["step2"] = {"tool_id": "sort1", "tool_version": "2.0", "in": {"x": "x"}}
        wf = normalized_format2(wf_dict)
        assert wf.unique_tools == frozenset(
            {
                ToolReference("cat1", "1.0"),
                ToolReference("sort1", "2.0"),
            }
        )

    def test_unresolved_ref_skipped(self):
        wf_dict = load("synthetic-single-versioned-tool.gxwf.yml")
        wf_dict["steps"]["nested"] = {
            "type": "subworkflow",
            "run": "https://example.com/wf.gxwf.yml",
            "in": {"y": "x"},
        }
        wf = normalized_format2(wf_dict)
        assert wf.unique_tools == frozenset({ToolReference("cat1", "1.0")})


class TestStrictStructure:
    """Tests for strict_structure parameter on normalization and conversion."""

    # --- normalized_format2 ---

    def test_format2_extra_field_accepted_by_default(self):
        wf_dict = load("synthetic-extra-field.gxwf.yml")
        result = normalized_format2(wf_dict)
        assert result.label == "Extra field workflow"

    def test_format2_extra_field_rejected_when_strict(self):
        wf_dict = load("synthetic-extra-field.gxwf.yml")
        with pytest.raises(ValidationError):
            normalized_format2(wf_dict, strict_structure=True)

    def test_format2_clean_input_passes_strict(self):
        wf_dict = load("synthetic-basic.gxwf.yml")
        result = normalized_format2(wf_dict, strict_structure=True)
        assert result is not None

    # --- normalized_native ---

    def test_native_extra_field_accepted_by_default(self):
        wf_dict = load("synthetic-extra-field.ga")
        result = normalized_native(wf_dict)
        assert result.name == "Extra field native"

    def test_native_extra_field_rejected_when_strict(self):
        wf_dict = load("synthetic-extra-field.ga")
        with pytest.raises(ValidationError):
            normalized_native(wf_dict, strict_structure=True)

    def test_native_clean_input_passes_strict(self):
        wf_dict = load("real-unicycler-assembly.ga")
        result = normalized_native(wf_dict, strict_structure=True)
        assert result is not None

    # --- extra="ignore" on normalized models ---

    def test_extra_fields_silently_dropped(self):
        """extra="ignore" means extras are never stored or emitted."""
        wf_dict = load("synthetic-extra-field.gxwf.yml")
        result = normalized_format2(wf_dict)
        dumped = result.to_dict()
        assert "not_a_real_field" not in dumped

    def test_native_extra_fields_silently_dropped(self):
        wf_dict = load("synthetic-extra-field.ga")
        result = normalized_native(wf_dict)
        dumped = result.to_dict()
        assert "not_a_real_field" not in dumped

    # --- threaded through conversion ---

    def test_to_native_strict_rejects_extra_fields(self):
        wf_dict = load("synthetic-extra-field.gxwf.yml")
        opts = ConversionOptions(strict_structure=True)
        with pytest.raises(ValidationError):
            to_native(wf_dict, options=opts)

    def test_to_format2_strict_rejects_extra_fields(self):
        wf_dict = load("synthetic-extra-field.ga")
        opts = ConversionOptions(strict_structure=True)
        with pytest.raises(ValidationError):
            to_format2(wf_dict, options=opts)

    def test_ensure_format2_strict_rejects_extra_fields(self):
        wf_dict = load("synthetic-extra-field.gxwf.yml")
        opts = ConversionOptions(strict_structure=True)
        with pytest.raises(ValidationError):
            ensure_format2(wf_dict, options=opts)

    def test_ensure_native_strict_rejects_extra_fields(self):
        wf_dict = load("synthetic-extra-field.ga")
        opts = ConversionOptions(strict_structure=True)
        with pytest.raises(ValidationError):
            ensure_native(wf_dict, options=opts)

    # --- output validation ---

    def test_to_native_strict_validates_output(self):
        """Strict conversion on clean input succeeds (output sanity check passes)."""
        wf_dict = load("synthetic-basic.gxwf.yml")
        opts = ConversionOptions(strict_structure=True)
        result = to_native(wf_dict, options=opts)
        assert result is not None

    def test_to_format2_strict_validates_output(self):
        wf_dict = load("real-unicycler-assembly.ga")
        opts = ConversionOptions(strict_structure=True)
        result = to_format2(wf_dict, options=opts)
        assert result is not None

    # --- sub-workflow / $graph paths ---

    def test_to_native_graph_subworkflow_strict_rejects(self):
        """$graph dedup path threads strict_structure into sub-workflow normalization."""
        wf_dict = load("synthetic-graph-simple.gxwf.yml")
        # Inject extra field into a sub-workflow entry (not main)
        wf_dict["$graph"].append(
            {
                "id": "sub1",
                "class": "GalaxyWorkflow",
                "not_a_real_field": "bad",
                "inputs": {"x": "data"},
                "outputs": {},
                "steps": {},
            }
        )
        opts = ConversionOptions(strict_structure=True, deduplicate_subworkflows=True)
        with pytest.raises(ValidationError):
            to_native(wf_dict, options=opts)

    def test_to_native_inline_subworkflow_strict_rejects(self):
        """Inline `run:` dict sub-workflow threads strict_structure."""
        wf_dict = load("synthetic-basic.gxwf.yml")
        wf_dict["steps"]["nested"] = {
            "type": "subworkflow",
            "run": {
                "class": "GalaxyWorkflow",
                "not_a_real_field": "bad",
                "inputs": {"y": "data"},
                "outputs": {},
                "steps": {},
            },
            "in": {"y": "the_input"},
        }
        opts = ConversionOptions(strict_structure=True)
        with pytest.raises(ValidationError):
            to_native(wf_dict, options=opts)

    # --- ensure_* output validation + typed-model paths ---

    def test_ensure_format2_strict_validates_clean_input(self):
        wf_dict = load("synthetic-basic.gxwf.yml")
        opts = ConversionOptions(strict_structure=True)
        result = ensure_format2(wf_dict, options=opts)
        assert result is not None

    def test_ensure_native_strict_validates_clean_input(self):
        wf_dict = load("real-unicycler-assembly.ga")
        opts = ConversionOptions(strict_structure=True)
        result = ensure_native(wf_dict, options=opts)
        assert result is not None

    def test_ensure_format2_strict_typed_galaxy_workflow(self):
        """GalaxyWorkflow typed input still gets output-validated in strict mode."""
        from gxformat2.schema.gxformat2 import GalaxyWorkflow

        wf_dict = load("synthetic-basic.gxwf.yml")
        gw = GalaxyWorkflow.model_validate(wf_dict)
        opts = ConversionOptions(strict_structure=True)
        result = ensure_format2(gw, options=opts)
        assert result is not None

    def test_ensure_native_strict_typed_native_workflow(self):
        """NativeGalaxyWorkflow typed input still gets output-validated in strict mode."""
        from gxformat2.schema.native import NativeGalaxyWorkflow

        wf_dict = load("real-unicycler-assembly.ga")
        nw = NativeGalaxyWorkflow.model_validate(wf_dict)
        opts = ConversionOptions(strict_structure=True)
        result = ensure_native(nw, options=opts)
        assert result is not None
