"""Pydantic models for Cytoscape.js workflow visualization elements."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class CytoscapePosition(BaseModel):
    """Cytoscape node position (x/y coordinates)."""

    x: int = Field(default=0)
    y: int = Field(default=0)


class CytoscapeNodeData(BaseModel):
    """Data payload for a Cytoscape node (input or step)."""

    id: str
    label: str
    doc: str | None = Field(default=None)
    tool_id: str | None = Field(default=None)
    step_type: str = Field(default="tool")
    repo_link: str | None = Field(default=None)


class CytoscapeEdgeData(BaseModel):
    """Data payload for a Cytoscape edge (step connection)."""

    id: str
    source: str
    target: str
    input: str
    output: str | None = Field(default=None)


class CytoscapeNode(BaseModel):
    """A Cytoscape.js node element."""

    group: Literal["nodes"] = "nodes"
    data: CytoscapeNodeData
    classes: list[str] = Field(default_factory=list)
    position: CytoscapePosition = Field(default_factory=CytoscapePosition)


class CytoscapeEdge(BaseModel):
    """A Cytoscape.js edge element."""

    group: Literal["edges"] = "edges"
    data: CytoscapeEdgeData


class CytoscapeElements(BaseModel):
    """Complete set of Cytoscape.js elements for a workflow visualization."""

    nodes: list[CytoscapeNode] = Field(default_factory=list)
    edges: list[CytoscapeEdge] = Field(default_factory=list)

    def to_list(self) -> list[dict]:
        """Serialize to the flat list-of-dicts format Cytoscape.js expects."""
        elements: list[dict] = []
        for node in self.nodes:
            elements.append(node.model_dump())
        for edge in self.edges:
            elements.append(edge.model_dump())
        return elements
