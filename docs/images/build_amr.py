"""Regenerate the topological-vs-layered layout comparison figures.

Loads the ``real-amr-gene-detection.ga`` example fixture, strips its baked
positions, and re-lays it out with each strategy. For every strategy it writes
the laid-out ``.ga`` and a cytoscape ``.html`` preset render next to this
script; ``layout-amr-topological.png`` / ``layout-amr-layered.png`` (used by
docs/cli_layout.rst) are screenshots of those HTML renders.

Run from the repo with the ``test`` deps available::

    uv run python docs/images/build_amr.py
"""

import copy
import json
import os

from gxformat2.cytoscape import cytoscape_elements
from gxformat2.cytoscape._layout import topological_positions
from gxformat2.cytoscape._render import render_html
from gxformat2.examples import get_path
from gxformat2.layout._builder import _strip_positions, apply_layout
from gxformat2.layout._sugiyama import (
    _count_all_crossings,
    extract_graph,
    layered_positions,
)

SRC = get_path("real-amr-gene-detection.ga")
OUT = os.path.dirname(os.path.abspath(__file__))


def crossings(node_ids, edges, positions):
    cols = {}
    for nid in node_ids:
        p = positions[nid]
        cols.setdefault(p.x, []).append((p.y, nid))
    layers = [[nid for _, nid in sorted(cols[x], key=lambda t: t[0])] for x in sorted(cols)]
    succ = {nid: [] for nid in node_ids}
    for s, t in edges:
        succ[s].append(t)
    return _count_all_crossings(layers, succ)


with open(SRC) as f:
    original = json.load(f)

# Strip all baked positions -> clean input, so each strategy lays out from scratch.
stripped = _strip_positions(original)

results = {}
for strategy in ("topological", "layered"):
    wf = copy.deepcopy(stripped)
    apply_layout(wf, strategy=strategy, overwrite=True)
    ga_path = os.path.join(OUT, f"amr.{strategy}.ga")
    with open(ga_path, "w") as f:
        f.write(json.dumps(wf, indent=4) + "\n")
    # Render via cytoscape preset (honors the baked positions).
    elements = cytoscape_elements(wf, layout="preset")
    html = render_html(elements, layout="preset")
    html_path = os.path.join(OUT, f"amr.{strategy}.html")
    with open(html_path, "w") as f:
        f.write(html)
    results[strategy] = (ga_path, html_path)

# Metrics
elements = cytoscape_elements(stripped, layout="preset")
node_ids, edges = extract_graph(elements)
topo = topological_positions(elements)
lay = layered_positions(elements)
print("workflow :", os.path.basename(SRC))
print("nodes    :", len(node_ids), " edges:", len(edges))
print("topological crossings:", crossings(node_ids, edges, topo))
print("layered     crossings:", crossings(node_ids, edges, lay))
for s, (ga, html) in results.items():
    print(f"{s:12s}: {os.path.basename(ga)}  {os.path.basename(html)}")
