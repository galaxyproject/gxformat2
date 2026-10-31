"""Command-line interface for Cytoscape workflow visualization."""

import json
import os
import sys

from ._builder import cytoscape_elements
from ._layout import LAYOUT_NAMES
from ._render import render_html

SCRIPT_DESCRIPTION = """
This script converts an executable Galaxy workflow (in either format - Format 2
or native .ga) into a format for visualization with Cytoscape
(https://cytoscape.org/).

If the target output path ends with .html this script will output a HTML
page with the workflow visualized using cytoscape.js. Otherwise, this script
will output a JSON description of the workflow elements for consumption by
Cytoscape.
"""


def to_cytoscape(workflow_path: str, output_path=None, layout: str = "preset"):
    """Produce cytoscape output for supplied workflow path."""
    if output_path is None:
        output_path, _ = os.path.splitext(workflow_path)
        output_path += ".html"

    elements = cytoscape_elements(workflow_path, layout=layout)

    if output_path.endswith(".html"):
        with open(output_path, "w") as f:
            f.write(render_html(elements, layout=layout))
    else:
        # Bare flat list for ``preset`` (back-compat); wrapped {elements, layout}
        # otherwise so the layout hint travels with the JSON.
        payload = elements.to_list() if layout == "preset" else elements.to_dict()
        with open(output_path, "w") as f:
            json.dump(payload, f)


def main(argv=None):
    """Entry point for building Cytoscape visualizations of Galaxy workflows."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)
    to_cytoscape(args.input_path, args.output_path, layout=args.layout)


def _parser():
    import argparse

    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("input_path", metavar="INPUT", type=str, help="input workflow path (.ga/gxwf.yml)")
    parser.add_argument("output_path", metavar="OUTPUT", type=str, nargs="?", help="output viz path (.json/.html)")
    parser.add_argument(
        "--layout",
        type=str,
        default="preset",
        choices=list(LAYOUT_NAMES),
        help=(
            "Layout strategy: preset (default; honors workflow positions), "
            "topological (computed leveled layout), dagre, breadthfirst, grid, cose, random"
        ),
    )
    return parser
