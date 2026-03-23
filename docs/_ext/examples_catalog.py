"""Sphinx extension to generate workflow fixture documentation from catalog.yml."""

import json
import os
import string

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx

from gxformat2.cytoscape import CYTOSCAPE_JS_TEMPLATE
from gxformat2.examples import load_catalog
from gxformat2.model import ensure_step_position, resolve_source_reference
from gxformat2.normalize import steps_normalized

GITHUB_BASE = "https://github.com/galaxyproject/gxformat2/blob/main"
MAIN_TS_PREFIX = "toolshed.g2.bx.psu.edu/repos/"

# Minimal self-contained HTML template for embedding in an iframe.
# Uses a unique container ID per workflow to avoid conflicts.
EMBED_TEMPLATE = string.Template("""\
<!doctype html>
<html>
<head>
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.9.4/cytoscape.min.js"></script>
<style>
body { margin: 0; }
#cy { width: 100%; height: 100%; position: absolute; top: 0; left: 0; }
</style>
</head>
<body>
<div id="cy"></div>
<script>
document.addEventListener("DOMContentLoaded", function() {
    cytoscape({
        container: document.getElementById('cy'),
        elements: $elements,
        layout: { name: 'preset' },
        style: [
            { selector: 'node', style: { 'label': 'data(label)', 'font-size': '10px', 'text-wrap': 'wrap', 'text-max-width': '100px' } },
            { selector: 'edge', style: { 'curve-style': 'bezier', 'target-arrow-shape': 'vee', 'arrow-scale': 1.5, 'width': 1.5 } },
            { selector: '.input', style: { shape: 'diamond', 'background-color': '#d0bb46' } },
            { selector: '.runnable', style: { shape: 'round-rectangle', 'background-color': '#2c3143' } }
        ]
    });
});
</script>
</body>
</html>""")


def _build_cytoscape_elements(workflow_path):
    """Build cytoscape elements JSON from a workflow file, returns list or None on failure."""
    try:
        steps = steps_normalized(workflow_path=workflow_path)
    except Exception:
        return None

    known_labels = {str(s.get("id") or s.get("label") or i) for i, s in enumerate(steps)}
    elements = []
    for i, step in enumerate(steps):
        step_id = step.get("id") or step.get("label") or str(i)
        step_type = step.get("type") or "tool"
        classes = [f"type_{step_type}"]
        classes.append("runnable" if step_type in ["tool", "subworkflow"] else "input")

        tool_id = step.get("tool_id")
        if tool_id and tool_id.startswith(MAIN_TS_PREFIX):
            tool_id = tool_id[len(MAIN_TS_PREFIX):]
        label = step.get("id") or step.get("label") or (f"tool:{tool_id}" if tool_id else str(i))
        ensure_step_position(step, i)
        node_position = dict(x=int(step["position"]["left"]), y=int(step["position"]["top"]))
        node_data = {"id": step_id, "label": label, "step_type": step_type, "tool_id": step.get("tool_id")}
        elements.append({"group": "nodes", "data": node_data, "classes": classes, "position": node_position})

        for key, value in (step.get("in") or {}).items():
            if isinstance(value, dict) and "source" in value:
                value = value["source"]
            elif isinstance(value, dict):
                continue
            try:
                from_step, output = resolve_source_reference(value, known_labels)
            except Exception:
                continue
            if output == "output":
                output = None
            edge_id = f"{step_id}__to__{from_step}"
            edge_data = {"id": edge_id, "source": from_step, "target": step_id, "input": key, "output": output}
            elements.append({"group": "edges", "data": edge_data})

    return elements


class ExamplesCatalogDirective(Directive):
    """Directive that renders the examples catalog as rich documentation.

    Usage in .rst or .md::

        .. examples-catalog::
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def _ensure_viz_dir(self):
        outdir = os.path.join(self.state.document.settings.env.app.outdir, "_static", "workflow_viz")
        os.makedirs(outdir, exist_ok=True)
        return outdir

    def run(self):
        catalog = load_catalog()
        result_nodes = []

        format2_entries = [e for e in catalog if e.format == "format2"]
        native_entries = [e for e in catalog if e.format == "native"]

        if format2_entries:
            result_nodes.extend(self._section("Format2 Fixtures", format2_entries))
        if native_entries:
            result_nodes.extend(self._section("Native Fixtures", native_entries))

        return result_nodes

    def _section(self, title, entries):
        section = nodes.section(ids=[nodes.make_id(title)])
        section += nodes.title(text=title)

        for entry in entries:
            entry_section = nodes.section(ids=[nodes.make_id(entry.name)])
            entry_section += nodes.title(text=entry.name)

            # Metadata table
            field_list = nodes.field_list()
            field_list += self._field("Origin", entry.origin.value)
            field_list += self._field("Format", entry.format.value)
            field_list += self._link_field("Path", entry.file, f"{GITHUB_BASE}/gxformat2/examples/{entry.file}")

            label = entry.workflow_label
            if label:
                field_list += self._field("Workflow Label", label)

            annotation = entry.workflow_annotation
            if annotation:
                field_list += self._field("Description", annotation)

            if entry.tests:
                field_list += self._links_field("Tests", [(t, f"{GITHUB_BASE}/{t}") for t in entry.tests])

            entry_section += field_list

            # Cytoscape visualization
            viz_node = self._build_viz(entry)
            if viz_node is not None:
                entry_section += viz_node

            # Workflow source (collapsible)
            contents = entry.load_contents()
            if entry.format == "format2":
                lang = "yaml"
            else:
                try:
                    parsed = json.loads(contents)
                    contents = json.dumps(parsed, indent=2)
                except json.JSONDecodeError:
                    pass
                lang = "json"

            container = nodes.container(classes=["toggle"])
            container += nodes.caption(text="Workflow source")
            container += nodes.literal_block(contents, contents, language=lang)
            entry_section += container

            section += entry_section

        return [section]

    def _build_viz(self, entry):
        """Generate a cytoscape HTML file and return an iframe raw node, or None."""
        elements = _build_cytoscape_elements(entry.path)
        if not elements:
            return None

        viz_dir = self._ensure_viz_dir()
        viz_filename = entry.name.replace(".", "_") + ".html"
        viz_path = os.path.join(viz_dir, viz_filename)

        html = EMBED_TEMPLATE.safe_substitute(elements=json.dumps(elements))
        with open(viz_path, "w") as f:
            f.write(html)

        iframe_html = (
            f'<iframe src="_static/workflow_viz/{viz_filename}" '
            f'style="width:100%;height:400px;border:1px solid #ccc;border-radius:4px;" '
            f'loading="lazy"></iframe>'
        )
        return nodes.raw("", iframe_html, format="html")

    def _field(self, name, value):
        field = nodes.field()
        field += nodes.field_name(text=name)
        body = nodes.field_body()
        body += nodes.paragraph(text=value)
        field += body
        return field

    def _link_field(self, name, text, url):
        field = nodes.field()
        field += nodes.field_name(text=name)
        body = nodes.field_body()
        para = nodes.paragraph()
        para += nodes.reference("", text, refuri=url)
        body += para
        field += body
        return field

    def _links_field(self, name, text_url_pairs):
        field = nodes.field()
        field += nodes.field_name(text=name)
        body = nodes.field_body()
        bl = nodes.bullet_list()
        for text, url in text_url_pairs:
            item = nodes.list_item()
            para = nodes.paragraph()
            para += nodes.reference("", text, refuri=url)
            item += para
            bl += item
        body += bl
        field += body
        return field


def setup(app: Sphinx):
    app.add_directive("examples-catalog", ExamplesCatalogDirective)
    return {"version": "0.1", "parallel_read_safe": True}
