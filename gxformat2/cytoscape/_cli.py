"""Command-line interface for Cytoscape workflow visualization."""

import json
import os
import sys

from ._builder import cytoscape_elements
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


def to_cytoscape(workflow_path: str, output_path=None):
    """Produce cytoscape output for supplied workflow path."""
    if output_path is None:
        output_path, _ = os.path.splitext(workflow_path)
        output_path += ".html"

    elements = cytoscape_elements(workflow_path)

    if output_path.endswith(".html"):
        with open(output_path, "w") as f:
            f.write(render_html(elements))
    else:
        with open(output_path, "w") as f:
            json.dump(elements.to_list(), f)


def main(argv=None):
    """Entry point for building Cytoscape visualizations of Galaxy workflows."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)
    to_cytoscape(args.input_path, args.output_path)


def _parser():
    import argparse

    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("input_path", metavar="INPUT", type=str, help="input workflow path (.ga/gxwf.yml)")
    parser.add_argument("output_path", metavar="OUTPUT", type=str, nargs="?", help="output viz path (.json/.html)")
    return parser
