"""Structural graph properties any conforming workflow layout must satisfy.

These replace exact-coordinate goldens as the *cross-language* contract for the
bake path. The ``topological`` and ``layered`` strategies produce different
coordinates, but both must satisfy the same named properties here; a TypeScript
(or any other) reimplementation reimplements these checkers, not the
coordinates. The property names are the contract; this module is the Python
implementation.

Each checker takes a laid-out workflow document (the result of
``apply_layout``), reads node ids + edges from the cytoscape element view, reads
positions back from the document itself (not from cytoscape, which would
synthesize defaults), and raises ``AssertionError`` on violation.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, Iterator, Tuple

from gxformat2.cytoscape import cytoscape_elements
from gxformat2.layout._builder import (
    _format2_node_id,
    _is_graph_document,
    _is_native,
    _iter_subworkflows,
    _native_node_id,
)
from gxformat2.layout._sugiyama import extract_graph


def _read_node_positions(workflow: dict) -> Dict[str, dict]:
    """Read ``{node_id: position}`` straight from the laid-out document.

    Mirrors the id derivation in ``_builder`` (``_format2_node_id`` /
    ``_native_node_id``) so the keys line up with the cytoscape node ids used
    for edges. Nodes without a ``position`` are simply absent from the result.
    """
    positions: Dict[str, dict] = {}
    if _is_native(workflow):
        steps = workflow.get("steps")
        if isinstance(steps, dict):
            for key, step in steps.items():
                if isinstance(step, dict) and step.get("position") is not None:
                    positions[_native_node_id(key, step)] = step["position"]
        return positions

    for container_key in ("inputs", "steps"):
        container = workflow.get(container_key)
        is_input = container_key == "inputs"
        if isinstance(container, dict):
            for key, item in container.items():
                node_id = _format2_node_id(item, key, is_input=is_input)
                if isinstance(item, dict) and item.get("position") is not None and node_id is not None:
                    positions[node_id] = item["position"]
        elif isinstance(container, list):
            for item in container:
                if not isinstance(item, dict):
                    continue
                node_id = _format2_node_id(item, None, is_input=is_input)
                if item.get("position") is not None and node_id is not None:
                    positions[node_id] = item["position"]
    return positions


def _graph(workflow: dict) -> Tuple[list, list, Dict[str, dict]]:
    """Return ``(node_ids, edges, positions)`` for ``workflow``."""
    node_ids, edges = extract_graph(cytoscape_elements(workflow, layout="preset"))
    return node_ids, edges, _read_node_positions(workflow)


def downstream_right_of_upstream(workflow: dict) -> None:
    """Every edge points strictly rightward: ``target.left > source.left``.

    The core correctness property of a left-to-right layered layout. Holds
    unconditionally because cycles are rejected before layout (see
    ``LayoutCycleError``).
    """
    _node_ids, edges, positions = _graph(workflow)
    for source, target in edges:
        source_pos = positions.get(source)
        target_pos = positions.get(target)
        assert source_pos is not None, f"edge {source}->{target}: source {source!r} has no position"
        assert target_pos is not None, f"edge {source}->{target}: target {target!r} has no position"
        assert target_pos["left"] > source_pos["left"], (
            f"edge {source}->{target}: target.left {target_pos['left']} "
            f"not strictly right of source.left {source_pos['left']}"
        )


def all_nodes_positioned(workflow: dict) -> None:
    """Every node in the graph has a position in the document.

    Also catches a silent id mismatch between layout and apply (a node whose
    computed id never matched a document entry would be left unpositioned).
    """
    node_ids, _edges, positions = _graph(workflow)
    missing = [node_id for node_id in node_ids if node_id not in positions]
    assert not missing, f"nodes missing a position: {sorted(missing)}"


def no_position_collisions(workflow: dict) -> None:
    """No two nodes occupy the same ``{left, top}`` coordinate."""
    _node_ids, _edges, positions = _graph(workflow)
    seen: Dict[Tuple[int, int], str] = {}
    for node_id, pos in positions.items():
        key = (pos["left"], pos["top"])
        assert key not in seen, f"nodes {seen[key]!r} and {node_id!r} share position {key}"
        seen[key] = node_id


def roots_leftmost(workflow: dict) -> None:
    """Nodes with no incoming edge sit at the minimum ``left`` (column 0)."""
    node_ids, edges, positions = _graph(workflow)
    targets = {target for _source, target in edges}
    roots = [node_id for node_id in node_ids if node_id not in targets]
    if not roots or not positions:
        return
    min_left = min(pos["left"] for pos in positions.values())
    for node_id in roots:
        pos = positions.get(node_id)
        assert pos is not None, f"root {node_id!r} has no position"
        assert pos["left"] == min_left, f"root {node_id!r} at left {pos['left']} is not at the minimum left {min_left}"


#: Base checkers, each validating a single workflow's own node set. Exported for
#: direct unit testing; the registry below wraps them to recurse into
#: subworkflows.
_BASE_CHECKERS: Dict[str, Callable[[dict], None]] = {
    "downstream_right_of_upstream": downstream_right_of_upstream,
    "all_nodes_positioned": all_nodes_positioned,
    "no_position_collisions": no_position_collisions,
    "roots_leftmost": roots_leftmost,
}


def _iter_layout_units(workflow: dict) -> Iterator[dict]:
    """Yield every workflow whose nodes get their own coordinate space.

    The document itself plus, recursively, each in-file subworkflow -- and each
    entry of a ``$graph`` document. Mirrors what ``apply_layout(recursive=True)``
    lays out, so the property contract covers exactly what was positioned.
    """
    if _is_graph_document(workflow):
        graph = workflow["$graph"]
        entries = graph.values() if isinstance(graph, dict) else graph
        for entry in entries or []:
            if isinstance(entry, dict):
                yield from _iter_layout_units(entry)
        return
    yield workflow
    for subworkflow in _iter_subworkflows(workflow):
        yield from _iter_layout_units(subworkflow)


def _recursive_checker(checker: Callable[[dict], None]) -> Callable[[Any], None]:
    """Wrap a single-workflow checker to run against every laid-out unit."""

    def wrapped(workflow: dict) -> None:
        for unit in _iter_layout_units(workflow):
            checker(unit)

    return wrapped


GRAPH_PROPERTY_CHECKERS: Dict[str, Callable[[Any], None]] = {
    name: _recursive_checker(checker) for name, checker in _BASE_CHECKERS.items()
}
