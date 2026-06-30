"""Tests for gxformat2.layout.

Declarative coordinate assertions live in
``gxformat2/examples/expectations/layout.yml``; these cover the Python-specific
concerns: ruamel comment preservation, the ``position: auto`` sentinel, and the
overwrite policy.
"""

import json

import pytest

from gxformat2.examples import get_path, load
from gxformat2.layout import apply_layout, AUTO, layout_positions
from gxformat2.layout._cli import main, to_layout


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
