"""Build standalone visualization for Galaxy workflows."""

import argparse
import json
import os
import string
import sys
from typing import Any

from gxformat2.normalized import normalized_format2, NormalizedFormat2, NormalizedWorkflowStep
from gxformat2.schema.gxformat2 import WorkflowInputParameter

CYTOSCAPE_JS_TEMPLATE = os.path.join(os.path.dirname(__file__), "cytoscape.html")
MAIN_TS_PREFIX = "toolshed.g2.bx.psu.edu/repos/"
SCRIPT_DESCRIPTION = """
This script converts an executable Galaxy workflow (in either format - Format 2
or native .ga) into a format for visualization with Cytoscape
(https://cytoscape.org/).

If the target output path ends with .html this script will output a HTML
page with the workflow visualized using cytoscape.js. Otherwise, this script
will output a JSON description of the workflow elements for consumption by
Cytoscape.
"""


def to_cytoscape(workflow_path: str, output_path=None):
    """Produce cytoscape output for supplied workflow path."""
    if output_path is None:
        output_path, _ = os.path.splitext(workflow_path)
        output_path += ".html"

    nf2 = normalized_format2(workflow_path)
    elements: list[dict[str, Any]] = []

    for i, inp in enumerate(nf2.inputs):
        elements.append(_input_node(inp, i))

    inputs_offset = len(nf2.inputs)
    for i, step in enumerate(nf2.steps):
        elements.append(_step_node(step, i + inputs_offset))
        for edge in _step_edges(step, nf2):
            elements.append(edge)

    if output_path.endswith(".html"):
        with open(CYTOSCAPE_JS_TEMPLATE) as f:
            template = f.read()
        viz = string.Template(template).safe_substitute(elements=json.dumps(elements))
        with open(output_path, "w") as f:
            f.write(viz)
    else:
        with open(output_path, "w") as f:
            json.dump(elements, f)


def _fallback_position(order_index: int) -> dict[str, int]:
    return {"x": 10 * order_index, "y": 10 * order_index}


def _position_dict(step_position, order_index: int) -> dict[str, int]:
    if step_position is None:
        return _fallback_position(order_index)
    return {"x": int(step_position.left), "y": int(step_position.top)}


def _input_type_str(inp: WorkflowInputParameter) -> str:
    if inp.type_ is None:
        return "input"
    if isinstance(inp.type_, list):
        for t in inp.type_:
            return t.value + "[]"
        return "input"
    return inp.type_.value


def _input_node(inp: WorkflowInputParameter, order_index: int) -> dict[str, Any]:
    input_id = inp.id or str(order_index)
    type_str = _input_type_str(inp)
    return {
        "group": "nodes",
        "data": {
            "id": input_id,
            "label": input_id,
            "doc": inp.doc if isinstance(inp.doc, str) else None,
            "tool_id": None,
            "step_type": type_str,
            "repo_link": None,
        },
        "classes": [f"type_{type_str}", "input"],
        "position": _position_dict(inp.position, order_index),
    }


def _step_node(step: NormalizedWorkflowStep, order_index: int) -> dict[str, Any]:
    step_id = step.label or step.id
    step_type = step.type_.value if step.type_ else "tool"

    tool_id = step.tool_id
    if tool_id and tool_id.startswith(MAIN_TS_PREFIX):
        tool_id = tool_id[len(MAIN_TS_PREFIX) :]

    label = step.label or step.id or (f"tool:{tool_id}" if tool_id else str(order_index))

    repo_link = None
    if step.tool_shed_repository:
        repo = step.tool_shed_repository
        repo_link = f"https://{repo.tool_shed}/view/{repo.owner}/{repo.name}/{repo.changeset_revision}"

    return {
        "group": "nodes",
        "data": {
            "id": step_id,
            "label": label,
            "doc": step.doc,
            "tool_id": step.tool_id,
            "step_type": step_type,
            "repo_link": repo_link,
        },
        "classes": [f"type_{step_type}", "runnable"],
        "position": _position_dict(step.position, order_index),
    }


def _step_edges(step: NormalizedWorkflowStep, nf2: NormalizedFormat2) -> list[dict[str, Any]]:
    step_id = step.label or step.id
    edges = []
    for step_input in step.in_:
        if step_input.source is None:
            continue
        sources = step_input.source if isinstance(step_input.source, list) else [step_input.source]
        for source in sources:
            ref = nf2.resolve_source(source)
            output = ref.output_name if ref.output_name != "output" else None
            edge_id = f"{step_id}__to__{ref.step_label}"
            edges.append(
                {
                    "group": "edges",
                    "data": {
                        "id": edge_id,
                        "source": ref.step_label,
                        "target": step_id,
                        "input": step_input.id,
                        "output": output,
                    },
                }
            )
    return edges


def main(argv=None):
    """Entry point for building Cytoscape visualizations of Galaxy workflows."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)

    workflow_path = args.input_path
    output_path = args.output_path
    to_cytoscape(workflow_path, output_path)


def _parser():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("input_path", metavar="INPUT", type=str, help="input workflow path (.ga/gxwf.yml)")
    parser.add_argument("output_path", metavar="OUTPUT", type=str, nargs="?", help="output viz path (.json/.html)")
    return parser


if __name__ == "__main__":
    main()
