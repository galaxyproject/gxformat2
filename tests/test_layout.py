"""Tests for gxformat2.layout.

Declarative coordinate assertions live in
``gxformat2/examples/expectations/layout.yml``; these cover the Python-specific
concerns: ruamel comment preservation, the ``position: auto`` sentinel, and the
overwrite policy.
"""

import json

import pytest

from gxformat2.cytoscape import cytoscape_elements, COL_STRIDE, topological_positions
from gxformat2.examples import get_path, load
from gxformat2.layout import apply_layout, AUTO, layout_positions, LayoutCycleError
from gxformat2.layout._cli import main, to_layout
from gxformat2.layout._sugiyama import _count_all_crossings, extract_graph, layer_assignment


def test_layout_positions_topological():
    positions = layout_positions(load("synthetic-basic.gxwf.yml"))
    assert positions == {
        "the_input": {"left": 0, "top": 0},
        "cat": {"left": 220, "top": 0},
    }


def test_apply_layout_expands_shorthand_input():
    wf = {
        "class": "GalaxyWorkflow",
        "inputs": {"the_input": "data"},
        "steps": {"cat": {"tool_id": "cat1", "in": {"input1": "the_input"}}},
    }
    apply_layout(wf)
    assert wf["inputs"]["the_input"] == {"type": "data", "position": {"left": 0, "top": 0}}
    assert wf["steps"]["cat"]["position"] == {"left": 220, "top": 0}


def test_apply_layout_preserves_explicit_position_by_default():
    wf = {
        "class": "GalaxyWorkflow",
        "inputs": {"the_input": {"type": "data", "position": {"left": 5, "top": 7}}},
        "steps": {"cat": {"tool_id": "cat1", "in": {"input1": "the_input"}}},
    }
    apply_layout(wf)
    assert wf["inputs"]["the_input"]["position"] == {"left": 5, "top": 7}
    assert wf["steps"]["cat"]["position"] == {"left": 220, "top": 0}


def test_apply_layout_overwrite_replaces_explicit_position():
    wf = {
        "class": "GalaxyWorkflow",
        "inputs": {"the_input": {"type": "data", "position": {"left": 5, "top": 7}}},
        "steps": {"cat": {"tool_id": "cat1", "in": {"input1": "the_input"}}},
    }
    apply_layout(wf, overwrite=True)
    assert wf["inputs"]["the_input"]["position"] == {"left": 0, "top": 0}


def test_apply_layout_auto_sentinel_is_replaced_without_overwrite():
    wf = {
        "class": "GalaxyWorkflow",
        "inputs": {"the_input": {"type": "data", "position": AUTO}},
        "steps": {"cat": {"tool_id": "cat1", "in": {"input1": "the_input"}, "position": AUTO}},
    }
    apply_layout(wf)
    assert wf["inputs"]["the_input"]["position"] == {"left": 0, "top": 0}
    assert wf["steps"]["cat"]["position"] == {"left": 220, "top": 0}


def test_apply_layout_list_form_inputs_and_steps():
    wf = {
        "class": "GalaxyWorkflow",
        "inputs": [{"id": "the_input", "type": "data"}],
        "steps": [{"label": "cat", "tool_id": "cat1", "in": {"input1": "the_input"}}],
    }
    apply_layout(wf)
    assert wf["inputs"][0]["position"] == {"left": 0, "top": 0}
    assert wf["steps"][0]["position"] == {"left": 220, "top": 0}


def test_apply_layout_disconnected_components_share_column_zero():
    wf = {
        "class": "GalaxyWorkflow",
        "inputs": {"a": "data", "b": "data"},
        "steps": {
            "first": {"tool_id": "cat1", "in": {"input1": "a"}},
            "second": {"tool_id": "cat1", "in": {"input1": "b"}},
        },
    }
    apply_layout(wf)
    # Two parallel chains stack as rows within their columns.
    assert wf["inputs"]["a"]["position"] == {"left": 0, "top": 0}
    assert wf["inputs"]["b"]["position"] == {"left": 0, "top": 100}
    assert wf["steps"]["first"]["position"] == {"left": 220, "top": 0}
    assert wf["steps"]["second"]["position"] == {"left": 220, "top": 100}


def test_layout_positions_unknown_strategy():
    with pytest.raises(ValueError):
        layout_positions(load("synthetic-basic.gxwf.yml"), strategy="dagre")


def test_layout_cycle_raises():
    with pytest.raises(LayoutCycleError):
        layout_positions(load("synthetic-cycle.gxwf.yml"))


def test_layered_cycle_raises():
    with pytest.raises(LayoutCycleError):
        layout_positions(load("synthetic-cycle.gxwf.yml"), strategy="layered")


def test_layered_positions_basic():
    positions = layout_positions(load("synthetic-basic.gxwf.yml"), strategy="layered")
    assert positions == {
        "the_input": {"left": 0, "top": 0},
        "cat": {"left": 220, "top": 0},
    }


def test_layered_positions_uncrosses_reversed_chains():
    # Python-local exact-coordinate golden: barycenter reordering aligns each
    # step's row with its input's row, eliminating the crossings topological
    # would produce from the reversed declaration order.
    positions = layout_positions(load("synthetic-crossing-reversed.gxwf.yml"), strategy="layered")
    assert positions == {
        "a": {"left": 0, "top": 0},
        "b": {"left": 0, "top": 100},
        "c": {"left": 0, "top": 200},
        "step_a": {"left": 220, "top": 0},
        "step_b": {"left": 220, "top": 100},
        "step_c": {"left": 220, "top": 200},
    }


def test_layered_is_deterministic():
    fixture = "synthetic-crossing-reversed.gxwf.yml"
    first = layout_positions(load(fixture), strategy="layered")
    second = layout_positions(load(fixture), strategy="layered")
    assert first == second


def test_layer_assignment_agrees_with_cytoscape_columns():
    # The in-house longest-path layering (layer_assignment) and cytoscape's
    # byte-locked topological_positions are deliberately separate Kahn
    # implementations; they must agree on column assignment for acyclic graphs.
    # Pin that mirror on a multi-level, branching DAG so a future edit to either
    # file can't silently drift them apart.
    wf = {
        "class": "GalaxyWorkflow",
        "inputs": {"in1": "data"},
        "steps": {
            "s1": {"tool_id": "cat1", "in": {"input1": "in1"}},
            "s2": {"tool_id": "cat1", "in": {"input1": "s1/out_file1"}},
            "s3": {"tool_id": "cat1", "in": {"input1": "s2/out_file1"}},
            "branch": {"tool_id": "cat1", "in": {"input1": "in1"}},
        },
    }
    elements = cytoscape_elements(wf, layout="preset")
    node_ids, edges = extract_graph(elements)
    columns = layer_assignment(node_ids, edges)
    cyto_columns = {nid: pos.x // COL_STRIDE for nid, pos in topological_positions(elements).items()}
    assert columns == cyto_columns


def test_layered_reduces_crossings_vs_topological():
    fixture = "synthetic-crossing-reversed.gxwf.yml"

    def crossings(strategy):
        node_ids, edges = extract_graph(cytoscape_elements(load(fixture), layout="preset"))
        successors: dict = {n: [] for n in node_ids}
        for source, target in edges:
            successors[source].append(target)
        positions = layout_positions(load(fixture), strategy=strategy)
        by_col: dict = {}
        for node_id, pos in positions.items():
            by_col.setdefault(pos["left"], []).append((pos["top"], node_id))
        layers = [[nid for _, nid in sorted(by_col[left])] for left in sorted(by_col)]
        return _count_all_crossings(layers, successors)

    assert crossings("topological") > 0
    assert crossings("layered") == 0


def test_layered_reduces_crossings_on_real_workflow():
    # Real IWC workflow (bacterial_genomics/amr_gene_detection): a dense,
    # 4-layer graph where barycenter reordering materially untangles the edges.
    # topological is the byte-locked cross-language layout so its count is
    # stable (13); layered coordinates are not a contract, so assert only that
    # it stays well below topological rather than pinning an exact value.
    fixture = "real-amr-gene-detection.ga"

    def crossings(strategy):
        node_ids, edges = extract_graph(cytoscape_elements(load(fixture), layout="preset"))
        successors: dict = {n: [] for n in node_ids}
        for source, target in edges:
            successors[source].append(target)
        positions = layout_positions(load(fixture), strategy=strategy)
        by_col: dict = {}
        for node_id, pos in positions.items():
            by_col.setdefault(pos["left"], []).append((pos["top"], node_id))
        layers = [[nid for _, nid in sorted(by_col[left])] for left in sorted(by_col)]
        return _count_all_crossings(layers, successors)

    assert crossings("topological") == 13
    assert crossings("layered") <= 3
    assert crossings("layered") < crossings("topological")


def test_apply_layout_recurses_into_format2_embedded_run():
    wf = load("synthetic-tool-with-inline-subworkflow.gxwf.yml")
    apply_layout(wf, overwrite=True)
    sub = wf["steps"]["nested"]["run"]
    # Inner nodes laid out in the subworkflow's own coordinate space.
    assert sub["inputs"]["y"]["position"] == {"left": 0, "top": 0}
    assert sub["steps"]["inner_tool"]["position"] == {"left": 220, "top": 0}


def test_apply_layout_recurses_into_native_subworkflow():
    wf = load("synthetic-outer-inline-subworkflow.ga")
    apply_layout(wf, overwrite=True)
    inner = wf["steps"]["1"]["subworkflow"]["steps"]
    assert inner["0"]["position"] == {"left": 0, "top": 0}
    assert inner["1"]["position"] == {"left": 220, "top": 0}


def test_apply_layout_lays_out_every_graph_entry():
    wf = load("synthetic-graph-with-subworkflow.gxwf.yml")
    apply_layout(wf, overwrite=True)
    by_id = {entry["id"]: entry for entry in wf["$graph"]}
    assert by_id["subworkflow1"]["steps"]["inner_tool"]["position"] == {"left": 220, "top": 0}
    assert by_id["main"]["steps"]["nested_workflow"]["position"] == {"left": 440, "top": 0}


def test_apply_layout_recursive_false_skips_subworkflows():
    wf = load("synthetic-tool-with-inline-subworkflow.gxwf.yml")
    apply_layout(wf, overwrite=True, recursive=False)
    # Outer subworkflow step still positioned...
    assert wf["steps"]["nested"]["position"] == {"left": 220, "top": 100}
    # ...but the embedded workflow's nodes are left untouched.
    assert "position" not in wf["steps"]["nested"]["run"]["steps"]["inner_tool"]


def test_apply_layout_does_not_follow_external_run_reference():
    # A string run: (external URL/file) is a single node here and is not
    # descended into -- only the outer step gets a position.
    wf = load("synthetic-url-run-yml.gxwf.yml")
    apply_layout(wf, overwrite=True)
    assert wf["steps"]["nested"]["position"] == {"left": 220, "top": 0}
    assert isinstance(wf["steps"]["nested"]["run"], str)


def test_cli_no_recursive_flag_skips_subworkflows(tmp_path):
    src = get_path("synthetic-tool-with-inline-subworkflow.gxwf.yml")
    dest = tmp_path / "wf.gxwf.yml"
    dest.write_text(open(src).read())
    main([str(dest), "--overwrite", "--no-recursive"])
    laid = load(str(dest))
    assert "position" not in laid["steps"]["nested"]["run"]["steps"]["inner_tool"]


def test_cli_preserves_comments(tmp_path):
    src = get_path("synthetic-comments-dict.gxwf.yml")
    dest = tmp_path / "out.gxwf.yml"
    to_layout(str(src), str(dest))
    text = dest.read_text()
    # Comment-block content and quoting survive the round-trip.
    assert "Check adapters" in text
    assert "# Preprocessing Pipeline" in text
    assert "contains_steps" in text
    # Positions were merged into the step / input.
    laid = load(str(dest))
    assert laid["steps"]["cat"]["position"] == {"left": 220, "top": 0}


def test_cli_format2_in_place_adds_positions(tmp_path):
    src = get_path("synthetic-basic.gxwf.yml")
    dest = tmp_path / "wf.gxwf.yml"
    dest.write_text(open(src).read())
    main([str(dest)])
    laid = load(str(dest))
    assert laid["steps"]["cat"]["position"] == {"left": 220, "top": 0}
    assert laid["inputs"]["the_input"]["position"] == {"left": 0, "top": 0}


def test_cli_native_overwrite(tmp_path):
    src = get_path("real-basic-without-step-input-label.ga")
    dest = tmp_path / "wf.ga"
    dest.write_text(open(src).read())
    main([str(dest), "--overwrite"])
    with open(dest) as f:
        wf = json.load(f)
    assert wf["steps"]["0"]["position"] == {"left": 0, "top": 0}
    assert wf["steps"]["1"]["position"] == {"left": 220, "top": 0}
