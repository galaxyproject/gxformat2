"""Layout for Galaxy workflows.

Computes node positions and merges them into workflow documents, replacing the
degenerate diagonal fallback. Two strategies: ``topological`` (the dependency-
free, cross-language layering from ``gxformat2.cytoscape``) and ``layered`` (an
in-house barycenter Sugiyama pass that reduces edge crossings). Cyclic
workflows are rejected with ``LayoutCycleError``.
"""

from ._builder import apply_layout, AUTO, layout_positions
from ._cli import main, to_layout
from ._properties import GRAPH_PROPERTY_CHECKERS
from ._sugiyama import layered_positions, LayoutCycleError

__all__ = (
    "AUTO",
    "GRAPH_PROPERTY_CHECKERS",
    "LayoutCycleError",
    "apply_layout",
    "layered_positions",
    "layout_positions",
    "main",
    "to_layout",
)
