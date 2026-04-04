"""Build Mermaid flowchart diagrams from Galaxy workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gxformat2.normalized import ensure_format2, NormalizedFormat2
from gxformat2.schema.gxformat2 import GalaxyWorkflow, WorkflowInputParameter

# Standard Mermaid shape wrappers: (open, close) bracket pairs.
#   >label]   = asymmetric / flag (inputs)
#   [[label]] = subroutine (subworkflows)
#   [label]   = rectangle (tool steps, default)
SHAPE_INPUT = (">", "]")
SHAPE_PARAM = ("{{", "}}")
SHAPE_TOOL = ("[", "]")
SHAPE_SUBWORKFLOW = ("[[", "]]")

STEP_TYPE_SHAPES = {
    "data": SHAPE_INPUT,
    "collection": SHAPE_INPUT,
    "integer": SHAPE_PARAM,
    "float": SHAPE_PARAM,
    "text": SHAPE_PARAM,
    "boolean": SHAPE_PARAM,
    "color": SHAPE_PARAM,
    "input": SHAPE_INPUT,
    "tool": SHAPE_TOOL,
    "subworkflow": SHAPE_SUBWORKFLOW,
}

MAIN_TS_PREFIX = "toolshed.g2.bx.psu.edu/repos/"


def _sanitize_label(label: str) -> str:
    """Escape characters that have special meaning in Mermaid labels."""
    label = label.replace('"', '#quot;')
    for ch in "()[]{}<>":
        label = label.replace(ch, f"#{ord(ch)};")
    return label


def _input_type_str(inp: WorkflowInputParameter) -> str:
    if inp.type_ is None:
        return "input"
    if isinstance(inp.type_, list):
        if inp.type_:
            return inp.type_[0].value
        return "input"
    return inp.type_.value


def workflow_to_mermaid(
    workflow: dict[str, Any] | str | Path | GalaxyWorkflow | NormalizedFormat2,
) -> str:
    """Convert a Galaxy workflow to a Mermaid flowchart string.

    Accepts anything ``ensure_format2()`` supports, plus an already
    normalized ``NormalizedFormat2`` instance.
    """
    if isinstance(workflow, NormalizedFormat2):
        nf2 = workflow
    else:
        nf2 = ensure_format2(workflow)

    lines = ["graph LR"]

    input_ids: dict[str, str] = {}
    for i, inp in enumerate(nf2.inputs):
        node_id = f"input_{i}"
        input_ids[inp.id or str(i)] = node_id
        label = _sanitize_label(inp.id or str(i))
        type_str = _input_type_str(inp)
        open_br, close_br = STEP_TYPE_SHAPES.get(type_str, SHAPE_INPUT)
        lines.append(f'    {node_id}{open_br}"{label}<br/><i>{type_str}</i>"{close_br}')

    step_ids: dict[str, str] = {}
    for i, step in enumerate(nf2.steps):
        node_id = f"step_{i}"
        step_label = step.label or step.id
        step_ids[step_label] = node_id

        tool_id = step.tool_id
        if tool_id and tool_id.startswith(MAIN_TS_PREFIX):
            tool_id = tool_id[len(MAIN_TS_PREFIX):]

        label = _sanitize_label(step.label or step.id or (f"tool:{tool_id}" if tool_id else str(i)))
        step_type = step.type_.value if step.type_ else "tool"
        open_br, close_br = STEP_TYPE_SHAPES.get(step_type, SHAPE_TOOL)
        lines.append(f'    {node_id}{open_br}"{label}"{close_br}')

    # Build edges (deduplicate identical connections)
    seen_edges: set[tuple[str, str]] = set()
    for i, step in enumerate(nf2.steps):
        node_id = f"step_{i}"
        for step_input in step.in_:
            if step_input.source is None:
                continue
            sources = step_input.source if isinstance(step_input.source, list) else [step_input.source]
            for source in sources:
                ref = nf2.resolve_source(source)
                source_id = input_ids.get(ref.step_label) or step_ids.get(ref.step_label)
                if source_id:
                    edge_key = (source_id, node_id)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        lines.append(f"    {source_id} --> {node_id}")

    return "\n".join(lines)
