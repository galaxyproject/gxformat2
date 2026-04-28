"""Integration of ``layout`` through the cytoscape builder.

Asserts:
  - default emit equals layout="preset" (back-compat for the JSON shape).
  - topological overwrites coordinates and sets the layout hint.
  - hint-only layouts (dagre) drop ``position`` and set the layout hint.
"""

import pytest

from gxformat2.cytoscape import cytoscape_elements

WORKFLOW = {
    "class": "GalaxyWorkflow",
    "inputs": {"input_a": "data"},
    "steps": [
        {
            "id": "tool_a",
            "label": "tool_a",
            "tool_id": "cat1",
            "in": {"in": "input_a"},
        },
        {
            "id": "tool_b",
            "label": "tool_b",
            "tool_id": "cat1",
            "in": {"in": "tool_a/output"},
        },
    ],
}


def test_default_equals_preset():
    a = cytoscape_elements(WORKFLOW)
    b = cytoscape_elements(WORKFLOW, layout="preset")
    assert a.to_list() == b.to_list()
    assert a.layout is None


def test_topological_overwrites_positions():
    elements = cytoscape_elements(WORKFLOW, layout="topological")
    assert elements.layout is not None
    assert elements.layout.name == "topological"
    by_id = {n.data.id: (n.position.x, n.position.y) for n in elements.nodes}
    assert by_id["input_a"] == (0, 0)
    assert by_id["tool_a"] == (220, 0)
    assert by_id["tool_b"] == (440, 0)


def test_dagre_drops_positions():
    elements = cytoscape_elements(WORKFLOW, layout="dagre")
    assert elements.layout is not None
    assert elements.layout.name == "dagre"
    for node in elements.nodes:
        assert node.position is None
    # to_list() drops the ``position`` key entirely for hint-only layouts.
    for el in elements.to_list():
        if el["group"] == "nodes":
            assert "position" not in el


def test_unknown_layout_rejected():
    with pytest.raises(ValueError):
        cytoscape_elements(WORKFLOW, layout="bogus")


def test_to_dict_wraps_with_layout_hint():
    elements = cytoscape_elements(WORKFLOW, layout="topological")
    payload = elements.to_dict()
    assert payload["layout"] == {"name": "topological"}
    assert isinstance(payload["elements"], list)
    assert len(payload["elements"]) == len(elements.nodes) + len(elements.edges)
