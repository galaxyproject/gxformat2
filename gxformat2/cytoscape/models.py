"""Pydantic models for Cytoscape.js workflow visualization elements."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CytoscapePosition(BaseModel):
    """Cytoscape node position (x/y coordinates)."""

    x: int = Field(default=0)
    y: int = Field(default=0)


class CytoscapePlanReason(BaseModel):
    """Planning context of a planned (draft) step node."""

    todos: list[str] = Field(default_factory=list)
    plan_fields: dict[str, str] = Field(default_factory=dict)


# Draft-only fields: emitted only when set, so concrete output is unchanged.
_DRAFT_NODE_DATA_FIELDS = ("planned", "plan_reason")
_DRAFT_EDGE_DATA_FIELDS = ("planned",)


class CytoscapeNodeData(BaseModel):
    """Data payload for a Cytoscape node (input or step)."""

    id: str
    label: str
    doc: str | None = Field(default=None)
    tool_id: str | None = Field(default=None)
    step_type: str = Field(default="tool")
    repo_link: str | None = Field(default=None)
    planned: bool | None = Field(default=None)
    plan_reason: CytoscapePlanReason | None = Field(default=None)


class CytoscapeEdgeData(BaseModel):
    """Data payload for a Cytoscape edge (step connection)."""

    id: str
    source: str
    target: str
    input: str
    output: str | None = Field(default=None)
    planned: bool | None = Field(default=None)


class CytoscapeNode(BaseModel):
    """A Cytoscape.js node element."""

    group: Literal["nodes"] = "nodes"
    data: CytoscapeNodeData
    classes: list[str] = Field(default_factory=list)
    # Present for ``preset`` and ``topological`` layouts; omitted for hint-only
    # layouts (``dagre``, ``breadthfirst``, ``grid``, ``cose``, ``random``) so
    # the runtime renderer is responsible for placement.
    position: CytoscapePosition | None = Field(default=None)


class CytoscapeEdge(BaseModel):
    """A Cytoscape.js edge element."""

    group: Literal["edges"] = "edges"
    data: CytoscapeEdgeData
    classes: list[str] | None = Field(default=None)


class CytoscapeLayout(BaseModel):
    """Layout hint emitted on non-default layouts."""

    name: str


class CytoscapeElements(BaseModel):
    """Complete set of Cytoscape.js elements for a workflow visualization."""

    nodes: list[CytoscapeNode] = Field(default_factory=list)
    edges: list[CytoscapeEdge] = Field(default_factory=list)
    # Present only when the builder was invoked with a non-``preset`` layout.
    # Carried out-of-band so ``to_list()`` keeps the flat-list contract.
    layout: CytoscapeLayout | None = Field(default=None)

    def to_list(self) -> list[dict]:
        """Serialize to the flat list-of-dicts format Cytoscape.js expects."""
        elements: list[dict] = []
        for node in self.nodes:
            # Drop ``position`` only when it's None (hint-only layouts). We
            # avoid ``exclude_none`` because it would also strip nested nulls
            # like ``tool_id: null``, breaking byte-parity for the default flow.
            if node.position is None:
                element = node.model_dump(exclude={"position"})
            else:
                element = node.model_dump()
            _drop_none(element["data"], _DRAFT_NODE_DATA_FIELDS)
            elements.append(element)
        for edge in self.edges:
            element = edge.model_dump()
            _drop_none(element, ("classes",))
            _drop_none(element["data"], _DRAFT_EDGE_DATA_FIELDS)
            elements.append(element)
        return elements

    def to_dict(self) -> dict:
        """Serialize as ``{"elements": [...], "layout": {...}}`` wrapper.

        Used by the CLI when ``--layout`` is non-default so the layout hint
        travels alongside the elements.
        """
        result: dict = {"elements": self.to_list()}
        if self.layout is not None:
            result["layout"] = self.layout.model_dump()
        return result


def _drop_none(payload: dict, keys: tuple[str, ...]) -> None:
    for key in keys:
        if payload.get(key) is None:
            payload.pop(key, None)
