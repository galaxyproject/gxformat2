"""Layered (Sugiyama) layout for Galaxy workflow graphs.

This is an in-house implementation of the layer-assignment and barycenter
crossing-reduction halves of the Sugiyama layered graph drawing method. We
implement it ourselves rather than depend on ``grandalf`` -- the one clean
pure-Python Sugiyama library -- because grandalf appears effectively
unmaintained (last PyPI release ~0.8 around 2020), we already owned the
longest-path layering half (it is shared with ``topological``), and keeping
the layout dependency-free and deterministic matters for a baking tool whose
output lands in version-controlled workflow files.

Unlike ``gxformat2.cytoscape.topological_positions`` (which is byte-identical
with the TypeScript port and a cross-language contract), the coordinates
produced here are NOT a cross-language contract. They are validated only by the
structural graph properties in ``gxformat2/examples/expectations/layout.yml``,
so any conforming reimplementation is free to differ on exact coordinates.
"""

from __future__ import annotations

from typing import Dict, List, Tuple

from gxformat2.cytoscape.models import CytoscapeElements, CytoscapePosition

COL_STRIDE = 220
ROW_STRIDE = 100


class LayoutCycleError(ValueError):
    """Raised when a workflow graph contains a cycle.

    Galaxy workflows are DAGs; a cycle is invalid and rejected at load time.
    The ``gxwf-layout`` bake path refuses to lay out a cyclic graph rather than
    emit meaningless positions (the cytoscape *viz* path, by contrast, keeps a
    best-effort diagonal fallback for malformed input).
    """


Edge = Tuple[str, str]


def extract_graph(elements: CytoscapeElements) -> Tuple[List[str], List[Edge]]:
    """Pull ``(node_ids, edges)`` out of cytoscape elements.

    Edges referencing a node that is not in the element set (e.g. an output of
    a collapsed subworkflow) are dropped, matching
    ``cytoscape.topological_positions``.
    """
    node_ids = [n.data.id for n in elements.nodes]
    id_set = set(node_ids)
    edges: List[Edge] = []
    for edge in elements.edges:
        source = edge.data.source
        target = edge.data.target
        if source in id_set and target in id_set:
            edges.append((source, target))
    return node_ids, edges


def layer_assignment(node_ids: List[str], edges: List[Edge]) -> Dict[str, int]:
    """Longest-path layering via Kahn topological sort.

    Returns ``column`` mapping each node id to its 0-based layer (column =
    longest path from any root). Raises :class:`LayoutCycleError` when the graph
    is not a DAG -- i.e. some nodes never reach in-degree zero.

    The Kahn sweep here mirrors ``cytoscape.topological_positions`` (same
    declaration-index tie-break) so that, for an acyclic graph, the ``column``
    assignment is identical to what the topological layout would compute.
    """
    index_by_id = {node_id: i for i, node_id in enumerate(node_ids)}
    incoming: Dict[str, List[str]] = {node_id: [] for node_id in node_ids}
    dependents: Dict[str, List[str]] = {node_id: [] for node_id in node_ids}
    for source, target in edges:
        incoming[target].append(source)
        dependents[source].append(target)

    in_degree = {node_id: len(incoming[node_id]) for node_id in node_ids}
    column: Dict[str, int] = {}
    visited = 0

    queue = [node_id for node_id in node_ids if in_degree[node_id] == 0]
    while queue:
        # Pop the lowest declaration index for a deterministic, stable order.
        best = min(range(len(queue)), key=lambda i: index_by_id[queue[i]])
        node_id = queue.pop(best)
        visited += 1

        sources = incoming[node_id]
        column[node_id] = 0 if not sources else max(column[s] + 1 for s in sources)

        for dep in dependents[node_id]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    if visited != len(node_ids):
        unplaced = [node_id for node_id in node_ids if node_id not in column]
        raise LayoutCycleError(
            "Workflow graph contains a cycle; cannot compute a layout. "
            f"Nodes on or downstream of the cycle: {sorted(unplaced)}"
        )
    return column


def check_acyclic(elements: CytoscapeElements) -> None:
    """Raise :class:`LayoutCycleError` if ``elements`` describes a cyclic graph.

    Used by the ``topological`` bake path, which delegates coordinate math to
    the byte-identical cytoscape routine (that routine has a silent diagonal
    fallback for cycles); calling this first turns a cycle into a hard error
    before any positions are written.
    """
    node_ids, edges = extract_graph(elements)
    layer_assignment(node_ids, edges)


#: Barycenter sweeps to attempt. Workflow layers are small, and the heuristic
#: converges fast; the best ordering seen across sweeps is kept regardless.
MAX_SWEEPS = 8


def _count_crossings_between(upper: List[str], lower: List[str], successors: Dict[str, List[str]]) -> int:
    """Count edge crossings between two adjacent, ordered layers."""
    pos_lower = {node_id: i for i, node_id in enumerate(lower)}
    # Edges as (upper_index, lower_index), in upper order.
    edges = [(u_idx, pos_lower[v]) for u_idx, u in enumerate(upper) for v in successors[u] if v in pos_lower]
    crossings = 0
    for i in range(len(edges)):
        u_i, v_i = edges[i]
        for j in range(i + 1, len(edges)):
            u_j, v_j = edges[j]
            if (u_i < u_j and v_i > v_j) or (u_i > u_j and v_i < v_j):
                crossings += 1
    return crossings


def _count_all_crossings(layers: List[List[str]], successors: Dict[str, List[str]]) -> int:
    return sum(_count_crossings_between(layers[col], layers[col + 1], successors) for col in range(len(layers) - 1))


def _order_by_barycenter(layer: List[str], neighbors: Dict[str, List[str]], pos_in_fixed: Dict[str, int]) -> List[str]:
    """Reorder ``layer`` by the mean position of each node's fixed neighbors.

    Nodes with no neighbor in the fixed layer keep their current relative
    position (their key is their own index); ``sorted`` is stable, so ties --
    and isolated nodes -- preserve input order, making the result deterministic.
    """

    def key(indexed: Tuple[int, str]) -> float:
        idx, node_id = indexed
        fixed = [pos_in_fixed[m] for m in neighbors[node_id] if m in pos_in_fixed]
        return sum(fixed) / len(fixed) if fixed else float(idx)

    return [node_id for _, node_id in sorted(enumerate(layer), key=key)]


def _sweep(layers: List[List[str]], neighbors: Dict[str, List[str]], down: bool) -> None:
    """One barycenter sweep, reordering free layers in place.

    ``down`` sweeps left-to-right ordering each layer by its predecessors in the
    (already fixed) layer to the left; the up-sweep does the mirror with
    successors.
    """
    columns = range(1, len(layers)) if down else range(len(layers) - 2, -1, -1)
    for col in columns:
        fixed_col = col - 1 if down else col + 1
        pos_in_fixed = {node_id: i for i, node_id in enumerate(layers[fixed_col])}
        layers[col] = _order_by_barycenter(layers[col], neighbors, pos_in_fixed)


def layered_positions(elements: CytoscapeElements) -> Dict[str, CytoscapePosition]:
    """Sugiyama-style layered layout with barycenter crossing reduction.

    Phases: layer assignment (longest path, shared with ``topological``),
    crossing minimization (barycenter sweeps), coordinate assignment. Cycles
    raise :class:`LayoutCycleError` during layer assignment.

    Coordinate assignment is intentionally the simple pass -- order-index rows
    within each layer (``COL_STRIDE`` / ``ROW_STRIDE``). The structural layout
    properties hold for ordered rows; aesthetic barycenter *nudging* of the y
    coordinate toward neighbor means is a later, contract-preserving follow-up.

    Limitation: edges that span more than one layer are not split into dummy
    nodes, so crossing counts and barycenter means only consider
    immediately-adjacent-layer edges. Skip-level edges are therefore invisible
    to the heuristic -- the result can be suboptimal (a few avoidable crossings)
    but never wrong: longest-path layering keeps every edge pointing rightward
    regardless. Dummy-node routing is a possible future refinement.

    Returns a mapping keyed by node ``data.id`` (same ids as
    ``topological_positions``), so the apply step is strategy-agnostic.
    """
    node_ids, edges = extract_graph(elements)
    column = layer_assignment(node_ids, edges)  # raises LayoutCycleError on a cycle

    max_col = max(column.values(), default=-1)
    layers: List[List[str]] = [[] for _ in range(max_col + 1)]
    for node_id in node_ids:  # declaration order seeds a stable initial ordering
        layers[column[node_id]].append(node_id)

    predecessors: Dict[str, List[str]] = {node_id: [] for node_id in node_ids}
    successors: Dict[str, List[str]] = {node_id: [] for node_id in node_ids}
    for source, target in edges:
        successors[source].append(target)
        predecessors[target].append(source)

    best_layers = [list(layer) for layer in layers]
    best_crossings = _count_all_crossings(best_layers, successors)
    for sweep in range(MAX_SWEEPS):
        going_down = sweep % 2 == 0
        _sweep(layers, predecessors if going_down else successors, going_down)
        crossings = _count_all_crossings(layers, successors)
        if crossings < best_crossings:
            best_crossings = crossings
            best_layers = [list(layer) for layer in layers]
        if best_crossings == 0:
            break

    positions: Dict[str, CytoscapePosition] = {}
    for col, layer in enumerate(best_layers):
        for row, node_id in enumerate(layer):
            positions[node_id] = CytoscapePosition(x=col * COL_STRIDE, y=row * ROW_STRIDE)
    return positions
