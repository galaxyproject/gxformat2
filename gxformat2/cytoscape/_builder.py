"""Build typed Cytoscape elements from a Galaxy workflow."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gxformat2.normalized import normalized_format2, NormalizedFormat2, NormalizedWorkflowStep
from gxformat2.schema.gxformat2 import GalaxyWorkflow, WorkflowInputParameter

from .models import (
    CytoscapeEdge,
    CytoscapeEdgeData,
    CytoscapeElements,
    CytoscapeNode,
    CytoscapeNodeData,
    CytoscapePosition,
)

MAIN_TS_PREFIX = "toolshed.g2.bx.psu.edu/repos/"


def cytoscape_elements(
    workflow: dict[str, Any] | str | Path | GalaxyWorkflow | NormalizedFormat2,
) -> CytoscapeElements:
    """Build Cytoscape visualization elements from a Galaxy workflow.

    Accepts anything ``normalized_format2()`` supports, plus an already
    normalized ``NormalizedFormat2`` instance.
    """
    if isinstance(workflow, NormalizedFormat2):
        nf2 = workflow
    else:
        nf2 = normalized_format2(workflow)

    nodes: list[CytoscapeNode] = []
    edges: list[CytoscapeEdge] = []

    for i, inp in enumerate(nf2.inputs):
        nodes.append(_input_node(inp, i))

    inputs_offset = len(nf2.inputs)
    for i, step in enumerate(nf2.steps):
        nodes.append(_step_node(step, i + inputs_offset))
        edges.extend(_step_edges(step, nf2))

    return CytoscapeElements(nodes=nodes, edges=edges)


def _fallback_position(order_index: int) -> CytoscapePosition:
    return CytoscapePosition(x=10 * order_index, y=10 * order_index)


def _to_position(step_position, order_index: int) -> CytoscapePosition:
    if step_position is None:
        return _fallback_position(order_index)
    return CytoscapePosition(x=int(step_position.left), y=int(step_position.top))


def _input_type_str(inp: WorkflowInputParameter) -> str:
    if inp.type_ is None:
        return "input"
    if isinstance(inp.type_, list):
        if inp.type_:
            return inp.type_[0].value + "[]"
        return "input"
    return inp.type_.value


def _input_node(inp: WorkflowInputParameter, order_index: int) -> CytoscapeNode:
    input_id = inp.id or str(order_index)
    type_str = _input_type_str(inp)
    return CytoscapeNode(
        data=CytoscapeNodeData(
            id=input_id,
            label=input_id,
            doc=inp.doc if isinstance(inp.doc, str) else None,
            tool_id=None,
            step_type=type_str,
            repo_link=None,
        ),
        classes=[f"type_{type_str}", "input"],
        position=_to_position(inp.position, order_index),
    )


def _step_node(step: NormalizedWorkflowStep, order_index: int) -> CytoscapeNode:
    step_id = step.label or step.id
    step_type = step.type_.value if step.type_ else "tool"

    tool_id = step.tool_id
    if tool_id and tool_id.startswith(MAIN_TS_PREFIX):
        tool_id = tool_id[len(MAIN_TS_PREFIX):]

    label = step.label or step.id or (f"tool:{tool_id}" if tool_id else str(order_index))

    repo_link = None
    if step.tool_shed_repository:
        repo = step.tool_shed_repository
        repo_link = f"https://{repo.tool_shed}/view/{repo.owner}/{repo.name}/{repo.changeset_revision}"

    return CytoscapeNode(
        data=CytoscapeNodeData(
            id=step_id,
            label=label,
            doc=step.doc,
            tool_id=step.tool_id,
            step_type=step_type,
            repo_link=repo_link,
        ),
        classes=[f"type_{step_type}", "runnable"],
        position=_to_position(step.position, order_index),
    )


def _step_edges(step: NormalizedWorkflowStep, nf2: NormalizedFormat2) -> list[CytoscapeEdge]:
    step_id = step.label or step.id
    edges: list[CytoscapeEdge] = []
    for step_input in step.in_:
        if step_input.source is None:
            continue
        input_id = step_input.id or "unknown"
        sources = step_input.source if isinstance(step_input.source, list) else [step_input.source]
        for source in sources:
            ref = nf2.resolve_source(source)
            output = ref.output_name if ref.output_name != "output" else None
            edge_id = f"{step_id}__{input_id}__from__{ref.step_label}"
            edges.append(CytoscapeEdge(
                data=CytoscapeEdgeData(
                    id=edge_id,
                    source=ref.step_label,
                    target=step_id,
                    input=input_id,
                    output=output,
                ),
            ))
    return edges
