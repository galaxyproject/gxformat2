"""Render Cytoscape elements as a standalone HTML visualization."""

import json
import os
import string

from .models import CytoscapeElements

CYTOSCAPE_JS_TEMPLATE = os.path.join(os.path.dirname(__file__), "cytoscape.html")


def render_html(elements: CytoscapeElements, layout: str = "preset") -> str:
    """Return a standalone HTML page visualizing the workflow with Cytoscape.js.

    The returned string is a complete HTML document suitable for writing
    to a file or embedding in a Jupyter notebook.
    """
    with open(CYTOSCAPE_JS_TEMPLATE) as f:
        template = f.read()
    return string.Template(template).safe_substitute(
        elements=json.dumps(elements.to_list()),
        layout=json.dumps(layout),
    )
