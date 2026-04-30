"""Cross-language topological layout for Cytoscape elements.

Mirror of the TypeScript port at
``galaxy-tool-util-ts/packages/schema/src/workflow/cytoscape-layout.ts``.

Both implementations MUST produce byte-identical (x, y) coordinates for a
given input. The normative spec lives in the galaxy-tool-util-ts repo at
``docs/architecture/cytoscape-layout.md``. Any change here is a breaking
visual diff and must land in lockstep with that file.
"""

from __future__ import annotations

from typing import get_args, Literal

from .models import CytoscapeElements, CytoscapePosition

COL_STRIDE = 220
ROW_STRIDE = 100

LayoutName = Literal[
    "preset",
    "topological",
    "dagre",
    "breadthfirst",
    "grid",
    "cose",
    "random",
]

LAYOUT_NAMES: tuple[str, ...] = get_args(LayoutName)


def is_layout_name(value: str) -> bool:
    """Return True if ``value`` is one of the supported Cytoscape layout names."""
    return value in LAYOUT_NAMES


def bakes_coordinates(layout: str) -> bool:
    """Layouts that bake coordinates into ``data.position``.

    All other layouts are hint-only and rely on the runtime renderer.
    """
    return layout in ("preset", "topological")


def topological_positions(elements: CytoscapeElements) -> dict[str, CytoscapePosition]:
    """Compute positions per the topological layering spec.

    Returns a mapping keyed by node ``data.id``.
    """
    nodes = elements.nodes
    node_ids = [n.data.id for n in nodes]
    index_by_id = {node_id: i for i, node_id in enumerate(node_ids)}

    incoming: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for edge in elements.edges:
        source = edge.data.source
        target = edge.data.target
        if source not in index_by_id or target not in index_by_id:
            continue
        incoming[target].append(source)

    in_degree: dict[str, int] = {node_id: len(srcs) for node_id, srcs in incoming.items()}

    dependents: dict[str, list[str]] = {node_id: [] for node_id in node_ids}
    for target, sources in incoming.items():
        for s in sources:
            dependents[s].append(target)

    column: dict[str, int] = {}
    visited: set[str] = set()

    # Kahn topo sort, declaration-index tie break.
    queue: list[str] = [node_id for node_id in node_ids if in_degree[node_id] == 0]
    queue.sort(key=lambda nid: index_by_id[nid])

    while queue:
        # Pop lowest declaration index.
        best = 0
        for i in range(1, len(queue)):
            if index_by_id[queue[i]] < index_by_id[queue[best]]:
                best = i
        node_id = queue.pop(best)
        visited.add(node_id)

        sources = incoming[node_id]
        if not sources:
            column[node_id] = 0
        else:
            max_col = 0
            for s in sources:
                c = column.get(s)
                if c is not None and c + 1 > max_col:
                    max_col = c + 1
            column[node_id] = max_col

        for dep in dependents[node_id]:
            in_degree[dep] -= 1
            if in_degree[dep] == 0:
                queue.append(dep)

    # Cycle fallback: any unvisited node gets column = declaration index.
    for node_id in node_ids:
        if node_id not in visited:
            column[node_id] = index_by_id[node_id]

    # Row assignment: per column, declaration order.
    rows_by_column: dict[int, list[str]] = {}
    for node_id in node_ids:
        c = column[node_id]
        rows_by_column.setdefault(c, []).append(node_id)

    positions: dict[str, CytoscapePosition] = {}
    for c, ids in rows_by_column.items():
        for row, node_id in enumerate(ids):
            positions[node_id] = CytoscapePosition(x=c * COL_STRIDE, y=row * ROW_STRIDE)
    return positions
