gxwf-layout
===========

``gxwf-layout`` computes node positions for a Galaxy workflow (Format 2
``.gxwf.yml`` or native ``.ga``) and merges ``{left, top}`` position records
back into the document, replacing the degenerate diagonal layout Galaxy applies
when positions are absent. For Format 2 YAML the original comments, key order,
and quoting are preserved; only position records are added or updated.

Cyclic workflows are invalid in Galaxy and are rejected with an error rather
than laid out.

Strategies
----------

``topological`` (default)
   Strict layering: column is the longest path from any input, row is
   declaration order within the column. Dependency-free and identical to
   ``gxwf-viz --layout topological`` (a cross-language layout shared with the
   TypeScript port). Legible but applies no crossing reduction, so wide
   workflows can show more edge crossings.

``layered``
   Sugiyama-style layered layout: the same longest-path layering plus a
   barycenter crossing-reduction pass that reorders rows to align each node
   with its neighbors. Fewer edge crossings on wide/real workflows. The exact
   coordinates are not a cross-language contract; both strategies satisfy the
   same structural properties (every edge points rightward, roots are leftmost,
   no overlapping nodes).

.. argparse::
   :module: gxformat2.layout._cli
   :func: _parser
   :prog: gxwf-layout
