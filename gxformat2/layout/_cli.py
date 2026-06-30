"""Command-line interface for laying out Galaxy workflows.

``gxwf-layout`` computes node positions and merges them back into a workflow
document. For Format2 ``.gxwf.yml`` files it uses a round-trip YAML loader so
comments, key order, and quoting in hand-authored sources are preserved -- only
``position`` records are added/updated. Native ``.ga`` files are JSON and are
rewritten with ``json``.

See galaxyproject/galaxy#22954.
"""

from __future__ import annotations

import argparse
import json
import sys
from typing import Optional, Sequence

from ruamel.yaml import YAML

from ._builder import apply_layout

SCRIPT_DESCRIPTION = """
This script computes node positions for a Galaxy workflow (Format 2
.gxwf.yml or native .ga) and merges them back into the document, replacing the
degenerate diagonal layout applied when positions are absent.

For Format 2 YAML the original file's comments and formatting are preserved;
only position records are added or updated. Steps/inputs with an explicit
position are left untouched unless --overwrite is given; a "position: auto"
marker is always replaced.
"""


def _is_native_path(path: str) -> bool:
    return path.endswith(".ga")


def to_layout(
    input_path: str,
    output_path: Optional[str] = None,
    *,
    strategy: str = "topological",
    overwrite: bool = False,
) -> None:
    """Apply layout to the workflow at ``input_path``, writing to ``output_path``.

    When ``output_path`` is None the input file is updated in place.
    """
    if output_path is None:
        output_path = input_path

    if _is_native_path(input_path):
        with open(input_path) as f:
            workflow = json.load(f)
        apply_layout(workflow, strategy=strategy, overwrite=overwrite)
        with open(output_path, "w") as f:
            f.write(json.dumps(workflow, indent=4) + "\n")
    else:
        yaml = YAML()
        yaml.preserve_quotes = True
        with open(input_path) as f:
            workflow = yaml.load(f)
        apply_layout(workflow, strategy=strategy, overwrite=overwrite)
        with open(output_path, "w") as f:
            yaml.dump(workflow, f)


def main(argv: Optional[Sequence[str]] = None) -> None:
    """Entry point for laying out Galaxy workflows."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)
    to_layout(
        args.input_path,
        args.output_path,
        strategy=args.strategy,
        overwrite=args.overwrite,
    )


def _parser():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("input_path", metavar="INPUT", type=str, help="input workflow path (.ga/.gxwf.yml)")
    parser.add_argument(
        "output_path",
        metavar="OUTPUT",
        type=str,
        nargs="?",
        help="output path (defaults to updating INPUT in place)",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        default="topological",
        choices=["topological", "layered"],
        help=(
            "layout strategy (default: topological). 'topological' is the "
            "dependency-free, cross-language layering; 'layered' adds barycenter "
            "crossing reduction for fewer edge crossings on wide workflows."
        ),
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="overwrite existing explicit positions (default: only fill missing / 'auto')",
    )
    return parser
