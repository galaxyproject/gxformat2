"""Build standalone visualization for Galaxy workflows."""
import json
import os
import string
import sys

import pkg_resources

from gxformat2._scripts import ensure_format2
from gxformat2._yaml import ordered_load
from gxformat2.converter import convert_inputs_to_steps, ensure_step_position, steps_as_list

CYTOSCAPE_JS_TEMPLATE = pkg_resources.resource_filename(__name__, 'cytoscape.html')
MAIN_TS_PREFIX = "toolshed.g2.bx.psu.edu/repos/"


def main(argv=None):
    """Entry point for building Cytoscape visualizations of Galaxy workflows."""
    if argv is None:
        argv = sys.argv[1:]

    workflow_path = argv[0]
    with open(workflow_path, "r") as f:
        workflow_dict = ordered_load(f)

    workflow_dict = ensure_format2(workflow_dict)
    elements = []

    steps = steps_as_list(workflow_dict)
    convert_inputs_to_steps(workflow_dict, steps)

    for i, step in enumerate(steps):
        step_id = step.get("id") or step.get("label") or str(i)
        step_type = step.get("type") or 'tool'
        classes = ["type_%s" % step_type]
        if step_type in ['tool', 'subworkflow']:
            classes.append("runnable")
        else:
            classes.append("input")

        tool_id = step.get("tool_id")
        if tool_id and tool_id.startswith(MAIN_TS_PREFIX):
            tool_id = tool_id[len(MAIN_TS_PREFIX):]
        label = step.get("id") or step.get("label") or ("tool:%s" % tool_id) or str(i)
        ensure_step_position(step, i)
        node_position = dict(x=int(step["position"]["left"]), y=int(step["position"]["top"]))
        repo_link = None
        if "tool_shed_repository" in step:
            repo = step["tool_shed_repository"]
            repo_link = "https://" + repo["tool_shed"] + "/view/" + repo["owner"] + "/" + repo["name"] + "/" + repo["changeset_revision"]
        node_data = {
            "id": step_id,
            "label": label,
            "doc": step.get("doc"),
            "tool_id": step.get("tool_id"),
            "step_type": step_type,
            "repo_link": repo_link
        }
        elements.append({"group": "nodes", "data": node_data, "classes": classes, "position": node_position})
        for key, value in (step.get("in") or {}).items():
            # handle lists?
            if isinstance(value, dict) and 'source' in value:
                value = value["source"]
            elif isinstance(value, dict):
                continue
            if "/" in value:
                from_step, output = value.split("/", 1)
            else:
                from_step, output = value, None
            edge_id = "%s__to__%s" % (step_id, from_step)
            edge_data = {"id": edge_id, "source": from_step, "target": step_id, "input": key, "output": output}
            elements.append({"group": "edges", "data": edge_data})

    if len(argv) > 1:
        output_path = argv[1]
    else:
        output_path, _ = os.path.splitext(workflow_path)
        output_path += ".html"

    if output_path.endswith(".html"):
        with open(CYTOSCAPE_JS_TEMPLATE, "r") as f:
            template = f.read()
        viz = string.Template(template).safe_substitute(elements=json.dumps(elements))
        with open(output_path, "w") as f:
            f.write(viz)
    else:
        with open(output_path, "w") as f:
            json.dump(elements, f)


if __name__ == "__main__":
    main()
