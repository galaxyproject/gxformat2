"""Sphinx extension to generate workflow fixture documentation from catalog.yml."""

import json
import os
import string

import yaml
from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx

from gxformat2.cytoscape import cytoscape_elements
from gxformat2.examples import EXAMPLES_DIR, load_catalog
from gxformat2.mermaid import workflow_to_mermaid

GITHUB_BASE = "https://github.com/galaxyproject/gxformat2/blob/main"

# Minimal self-contained HTML template for embedding in an iframe.
# Uses a unique container ID per workflow to avoid conflicts.
EMBED_TEMPLATE = string.Template("""\
<!doctype html>
<html>
<head>
<link href="https://fonts.googleapis.com/css2?family=Atkinson+Hyperlegible:wght@400;700&display=swap" rel="stylesheet">
<script src="https://cdnjs.cloudflare.com/ajax/libs/cytoscape/3.9.4/cytoscape.min.js"></script>
<style>
body {
    margin: 0;
    font-family: "Atkinson Hyperlegible", sans-serif;
    background: #ffffff;
    background-image:
        linear-gradient(to right, rgba(37, 83, 123, 0.03) 1px, transparent 1px),
        linear-gradient(to bottom, rgba(37, 83, 123, 0.03) 1px, transparent 1px);
    background-size: 24px 24px;
}
#cy { width: 100%; height: calc(100% - 28px); position: absolute; top: 0; left: 0; }
.legend {
    position: absolute; bottom: 0; left: 0; right: 0;
    height: 28px; display: flex; align-items: center; gap: 16px;
    padding: 0 12px; font-size: 11px; color: #58585a;
    background: #f8f9fa; border-top: 1px solid #dee2e6;
}
.legend-item { display: flex; align-items: center; gap: 4px; }
.legend-swatch {
    width: 12px; height: 12px; border-radius: 2px;
}
.legend-swatch.input { background: #ffd700; transform: rotate(45deg); width: 10px; height: 10px; }
.legend-swatch.step { background: #2c3143; border-radius: 3px; }
</style>
</head>
<body>
<div id="cy"></div>
<div class="legend">
    <div class="legend-item"><div class="legend-swatch input"></div> Input</div>
    <div class="legend-item"><div class="legend-swatch step"></div> Step</div>
</div>
<script>
document.addEventListener("DOMContentLoaded", function() {
    cytoscape({
        container: document.getElementById('cy'),
        elements: $elements,
        layout: { name: 'preset' },
        style: [
            { selector: 'node', style: {
                'label': 'data(label)', 'font-size': '11px', 'font-family': '"Atkinson Hyperlegible", sans-serif',
                'text-wrap': 'wrap', 'text-max-width': '100px', 'text-valign': 'center',
                'border-width': 1, 'border-color': '#dee2e6'
            }},
            { selector: 'edge', style: {
                'curve-style': 'bezier', 'target-arrow-shape': 'vee', 'arrow-scale': 1.5,
                'width': 1.5, 'line-color': '#25537b', 'target-arrow-color': '#25537b', 'opacity': 0.6
            }},
            { selector: '.input', style: {
                shape: 'diamond', 'background-color': '#ffd700', 'color': '#2c3143',
                'border-color': '#d19e00'
            }},
            { selector: '.runnable', style: {
                shape: 'round-rectangle', 'background-color': '#2c3143', 'color': '#f8f9fa',
                'border-color': '#25537b'
            }}
        ]
    });
});
</script>
</body>
</html>""")


def _build_cytoscape_elements(workflow_path):
    """Build cytoscape elements JSON from a workflow file, returns list or None on failure."""
    try:
        elements = cytoscape_elements(workflow_path)
    except Exception:
        return None
    return elements.to_list()


EXPECTATIONS_DIR = os.path.join(EXAMPLES_DIR, "expectations")

DECLARATIVE_TEST = "tests/test_interop_tests.py"


def _load_fixture_expectations():
    """Build a mapping from fixture filename to list of (test_id, operation, expectation_file)."""
    fixture_map = {}
    if not os.path.isdir(EXPECTATIONS_DIR):
        return fixture_map
    for fname in sorted(os.listdir(EXPECTATIONS_DIR)):
        if not fname.endswith(".yml"):
            continue
        fpath = os.path.join(EXPECTATIONS_DIR, fname)
        with open(fpath) as f:
            suite = yaml.safe_load(f)
        if not suite:
            continue
        for test_id, case in suite.items():
            fixture = case.get("fixture", "")
            operation = case.get("operation", "")
            fixture_map.setdefault(fixture, []).append((test_id, operation, fname))
    return fixture_map


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
        self._fixture_expectations = _load_fixture_expectations()
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

            # Split tests into Python and Interoperable
            python_tests = [t for t in (entry.tests or []) if t != DECLARATIVE_TEST]
            interop_cases = self._fixture_expectations.get(entry.name, [])

            if python_tests:
                field_list += self._links_field(
                    "Python Tests",
                    [(t, f"{GITHUB_BASE}/{t}") for t in python_tests],
                )

            if interop_cases:
                items = []
                for test_id, operation, exp_file in interop_cases:
                    exp_url = f"{GITHUB_BASE}/gxformat2/examples/expectations/{exp_file}"
                    items.append((f"{test_id} ({operation})", exp_url))
                field_list += self._links_field("Interoperable Tests", items)

            entry_section += field_list

            # Cytoscape visualization
            viz_node = self._build_viz(entry)
            if viz_node is not None:
                entry_section += viz_node

            # Mermaid diagram
            mermaid_node = self._build_mermaid(entry)
            if mermaid_node is not None:
                entry_section += mermaid_node

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

    def _build_mermaid(self, entry):
        """Generate a mermaid diagram node, or None on failure."""
        try:
            diagram = workflow_to_mermaid(entry.path)
        except Exception:
            return None

        from sphinxcontrib.mermaid import mermaid as mermaid_node

        container = nodes.container(classes=["toggle"])
        container += nodes.caption(text="Mermaid diagram")
        node = mermaid_node()
        node["code"] = diagram
        node["options"] = {}
        container += node
        return container

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


class ExpectationsCatalogDirective(Directive):
    """Directive that renders the declarative expectation files as documentation.

    Usage in .rst::

        .. expectations-catalog::
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self):
        result_nodes = []
        expectations_dir = EXPECTATIONS_DIR
        if not os.path.isdir(expectations_dir):
            return result_nodes

        for fname in sorted(os.listdir(expectations_dir)):
            if not fname.endswith(".yml"):
                continue
            fpath = os.path.join(expectations_dir, fname)
            with open(fpath) as f:
                suite = yaml.safe_load(f)
            if not suite:
                continue

            section = nodes.section(ids=[nodes.make_id(fname)])
            section += nodes.title(text=fname)

            github_url = f"{GITHUB_BASE}/gxformat2/examples/expectations/{fname}"
            para = nodes.paragraph()
            para += nodes.reference("", "Source on GitHub", refuri=github_url)
            section += para

            # Summary table of test cases
            table = nodes.table()
            tgroup = nodes.tgroup(cols=3)
            table += tgroup
            for _ in range(3):
                tgroup += nodes.colspec(colwidth=1)
            thead = nodes.thead()
            tgroup += thead
            header_row = nodes.row()
            for header in ("Test", "Fixture", "Operation"):
                entry = nodes.entry()
                entry += nodes.paragraph(text=header)
                header_row += entry
            thead += header_row

            tbody = nodes.tbody()
            tgroup += tbody
            for test_id, case in suite.items():
                row = nodes.row()
                for val in (test_id, case.get("fixture", ""), case.get("operation", "")):
                    entry = nodes.entry()
                    entry += nodes.paragraph(text=str(val))
                    row += entry
                tbody += row
            section += table

            result_nodes.append(section)

        return result_nodes


def setup(app: Sphinx):
    app.add_directive("examples-catalog", ExamplesCatalogDirective)
    app.add_directive("expectations-catalog", ExpectationsCatalogDirective)
    return {"version": "0.2", "parallel_read_safe": True}
