"""Build Mermaid flowchart diagrams from Galaxy workflows."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from gxformat2._labels import Labels
from gxformat2.normalized import ensure_format2, NormalizedFormat2
from gxformat2.schema.gxformat2 import BaseInputParameter, FrameComment, GalaxyWorkflow

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
    label = label.replace('"', "#quot;")
    for ch in "()[]{}<>":
        label = label.replace(ch, f"#{ord(ch)};")
    return label


def _input_type_str(inp: BaseInputParameter) -> str:
    type_ = getattr(inp, "type_", None)
    if type_ is None:
        return "input"
    if isinstance(type_, list):
        if not type_:
            return "input"
        type_ = type_[0]
    return getattr(type_, "value", type_)


def _node_line(node_id: str, label: str, shape: tuple[str, str]) -> str:
    open_br, close_br = shape
    return f'{node_id}{open_br}"{label}"{close_br}'


def workflow_to_mermaid(
    workflow: dict[str, Any] | str | Path | GalaxyWorkflow | NormalizedFormat2,
    *,
    comments: bool = False,
) -> str:
    """Convert a Galaxy workflow to a Mermaid flowchart string.

    Accepts anything ``ensure_format2()`` supports, plus an already
    normalized ``NormalizedFormat2`` instance.

    When *comments* is True, FrameComment objects are rendered as
    Mermaid subgraphs that group their contained steps.
    """
    if isinstance(workflow, NormalizedFormat2):
        nf2 = workflow
    else:
        nf2 = ensure_format2(workflow)

    lines = ["graph LR"]

    # Build node ID mappings and collect node declaration lines
    input_ids: dict[str, str] = {}
    input_lines: dict[str, str] = {}
    for i, inp in enumerate(nf2.inputs):
        node_id = f"input_{i}"
        inp_label = inp.id or str(i)
        input_ids[inp_label] = node_id
        label = _sanitize_label(inp_label)
        type_str = _input_type_str(inp)
        input_lines[inp_label] = _node_line(
            node_id, f"{label}<br/><i>{type_str}</i>", STEP_TYPE_SHAPES.get(type_str, SHAPE_INPUT)
        )

    step_ids: dict[str, str] = {}
    step_lines: dict[str, str] = {}
    for i, step in enumerate(nf2.steps):
        node_id = f"step_{i}"
        step_label = step.label or step.id
        step_ids[step_label] = node_id

        tool_id = step.tool_id
        if tool_id and tool_id.startswith(MAIN_TS_PREFIX):
            tool_id = tool_id[len(MAIN_TS_PREFIX) :]

        display_id = step.id if step.id and not Labels.is_unlabeled(step.id) else None
        label = _sanitize_label(step.label or display_id or (f"tool:{tool_id}" if tool_id else str(i)))
        step_type = step.type_.value if step.type_ else "tool"
        step_lines[step_label] = _node_line(node_id, label, STEP_TYPE_SHAPES.get(step_type, SHAPE_TOOL))

    # Collect frame comments and which labels they claim
    framed: set[str] = set()
    frames: list[FrameComment] = []
    if comments:
        for comment in nf2.comments:
            if isinstance(comment, FrameComment) and comment.contains_steps:
                frames.append(comment)
                for ref in comment.contains_steps:
                    framed.add(str(ref))

    # Emit nodes — framed ones go inside subgraph blocks, others at top level
    for inp_label, line in input_lines.items():
        if inp_label not in framed:
            lines.append(f"    {line}")

    for step_label, line in step_lines.items():
        if step_label not in framed:
            lines.append(f"    {line}")

    for i, frame in enumerate(frames):
        title = _sanitize_label(frame.title or f"Group {i}")
        lines.append(f'    subgraph sub_{i} ["{title}"]')
        for ref in frame.contains_steps or []:
            ref_str = str(ref)
            if ref_str in input_lines:
                lines.append(f"        {input_lines[ref_str]}")
            elif ref_str in step_lines:
                lines.append(f"        {step_lines[ref_str]}")
        lines.append("    end")

    # Build edges (deduplicate identical connections)
    seen_edges: set[tuple[str, str]] = set()
    for i, step in enumerate(nf2.steps):
        node_id = f"step_{i}"
        for step_input in step.in_:
            if step_input.source is None:
                continue
            sources = step_input.source if isinstance(step_input.source, list) else [step_input.source]
            for source in sources:
                source_ref = nf2.resolve_source(source)
                source_id = input_ids.get(source_ref.step_label) or step_ids.get(source_ref.step_label)
                if source_id:
                    edge_key = (source_id, node_id)
                    if edge_key not in seen_edges:
                        seen_edges.add(edge_key)
                        lines.append(f"    {source_id} --> {node_id}")

    return "\n".join(lines)
