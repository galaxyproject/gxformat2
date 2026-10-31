"""Cross-language parity tests for the topological layout.

Mirrors galaxy-tool-util-ts's
``packages/schema/test/cytoscape-layout.test.ts``. Coordinates are hard-coded
and MUST be byte-identical with the TS implementation.
"""

from gxformat2.cytoscape._layout import (
    COL_STRIDE,
    ROW_STRIDE,
    topological_positions,
)
from gxformat2.cytoscape.models import (
    CytoscapeEdge,
    CytoscapeEdgeData,
    CytoscapeElements,
    CytoscapeNode,
    CytoscapeNodeData,
)


def _n(node_id: str) -> CytoscapeNode:
    return CytoscapeNode(
        data=CytoscapeNodeData(
            id=node_id,
            label=node_id,
            doc=None,
            tool_id=None,
            step_type="input",
            repo_link=None,
        ),
        classes=[],
    )


def _e(source: str, target: str) -> CytoscapeEdge:
    return CytoscapeEdge(
        data=CytoscapeEdgeData(
            id=f"{target}__in__from__{source}",
            source=source,
            target=target,
            input="in",
            output=None,
        )
    )


def _positions(nodes: list[CytoscapeNode], edges: list[CytoscapeEdge]) -> dict[str, tuple[int, int]]:
    elements = CytoscapeElements(nodes=nodes, edges=edges)
    return {nid: (p.x, p.y) for nid, p in topological_positions(elements).items()}


def test_stride_constants():
    assert COL_STRIDE == 220
    assert ROW_STRIDE == 100


def test_linear_chain():
    assert _positions(
        [_n("A"), _n("B"), _n("C")],
        [_e("A", "B"), _e("B", "C")],
    ) == {"A": (0, 0), "B": (220, 0), "C": (440, 0)}


def test_diamond():
    assert _positions(
        [_n("A"), _n("B"), _n("C"), _n("D")],
        [_e("A", "B"), _e("A", "C"), _e("B", "D"), _e("C", "D")],
    ) == {"A": (0, 0), "B": (220, 0), "C": (220, 100), "D": (440, 0)}


def test_fan_out():
    assert _positions(
        [_n("A"), _n("B"), _n("C")],
        [_e("A", "B"), _e("A", "C")],
    ) == {"A": (0, 0), "B": (220, 0), "C": (220, 100)}


def test_fan_in():
    assert _positions(
        [_n("A"), _n("B"), _n("C")],
        [_e("A", "C"), _e("B", "C")],
    ) == {"A": (0, 0), "B": (0, 100), "C": (220, 0)}


def test_disconnected_components_stack_vertically():
    assert _positions(
        [_n("A"), _n("B"), _n("X"), _n("Y")],
        [_e("A", "B"), _e("X", "Y")],
    ) == {"A": (0, 0), "B": (220, 0), "X": (0, 100), "Y": (220, 100)}


def test_longest_path_layering():
    # A → B → D and A → D directly; D's column = max(B, A) + 1 = 2.
    assert _positions(
        [_n("A"), _n("B"), _n("D")],
        [_e("A", "B"), _e("A", "D"), _e("B", "D")],
    ) == {"A": (0, 0), "B": (220, 0), "D": (440, 0)}


def test_ignores_unknown_source_nodes():
    assert _positions(
        [_n("A"), _n("B")],
        [_e("A", "B"), _e("ghost", "B")],
    ) == {"A": (0, 0), "B": (220, 0)}
