"""Command-line interface for Mermaid workflow diagram generation."""

import sys

from ._builder import workflow_to_mermaid

SCRIPT_DESCRIPTION = """
Convert a Galaxy workflow (Format 2 or native .ga) into a Mermaid flowchart
diagram.

Outputs Mermaid markdown to stdout by default, or to a file if an output
path is provided. If the output path ends with .md, the diagram is wrapped
in a fenced code block.
"""


def to_mermaid(workflow_path: str, output_path=None):
    """Produce mermaid output for the supplied workflow path."""
    diagram = workflow_to_mermaid(workflow_path)

    if output_path is None:
        print(diagram)
        return

    if output_path.endswith(".md"):
        content = f"```mermaid\n{diagram}\n```\n"
    else:
        content = diagram + "\n"

    with open(output_path, "w") as f:
        f.write(content)


def main(argv=None):
    """Entry point for generating Mermaid diagrams of Galaxy workflows."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)
    to_mermaid(args.input_path, args.output_path)


def _parser():
    import argparse

    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("input_path", metavar="INPUT", type=str, help="input workflow path (.ga/gxwf.yml)")
    parser.add_argument("output_path", metavar="OUTPUT", type=str, nargs="?", help="output path (.mmd/.md)")
    return parser
