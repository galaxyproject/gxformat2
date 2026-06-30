"""Topological layout for Galaxy workflows.

Computes node positions (reusing the cross-language layout from
``gxformat2.cytoscape``) and merges them into workflow documents, replacing the
degenerate diagonal fallback. See galaxyproject/galaxy#22954.
"""

from ._builder import apply_layout, AUTO, layout_positions
from ._cli import main, to_layout

__all__ = (
    "AUTO",
    "apply_layout",
    "layout_positions",
    "main",
    "to_layout",
)
