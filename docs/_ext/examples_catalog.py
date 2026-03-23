"""Sphinx extension to generate example workflow documentation from catalog.yml."""

import json

from docutils import nodes
from docutils.parsers.rst import Directive
from sphinx.application import Sphinx

from gxformat2.examples import load_catalog


class ExamplesCatalogDirective(Directive):
    """Directive that renders the examples catalog as rich documentation.

    Usage in .rst or .md::

        .. examples-catalog::
    """

    has_content = False
    required_arguments = 0
    optional_arguments = 0

    def run(self):
        catalog = load_catalog()
        result_nodes = []

        format2_entries = [e for e in catalog if e.format == "format2"]
        native_entries = [e for e in catalog if e.format == "native"]

        if format2_entries:
            result_nodes.extend(self._section("Format2 Examples", format2_entries))
        if native_entries:
            result_nodes.extend(self._section("Native Examples", native_entries))

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
            field_list += self._field("Path", entry.file)

            label = entry.workflow_label
            if label:
                field_list += self._field("Workflow Label", label)

            annotation = entry.workflow_annotation
            if annotation:
                field_list += self._field("Annotation", annotation)

            if entry.tests:
                field_list += self._field("Tests", ", ".join(entry.tests))

            entry_section += field_list

            # Workflow content
            contents = entry.load_contents()
            if entry.format == "format2":
                lang = "yaml"
            else:
                # Re-format JSON for readability (the raw files may not be pretty-printed)
                try:
                    parsed = json.loads(contents)
                    contents = json.dumps(parsed, indent=2)
                except json.JSONDecodeError:
                    pass
                lang = "json"

            # Collapse long content
            container = nodes.container(classes=["toggle"])
            container += nodes.caption(text="Workflow source")
            container += nodes.literal_block(contents, contents, language=lang)
            entry_section += container

            section += entry_section

        return [section]

    def _field(self, name, value):
        field = nodes.field()
        field += nodes.field_name(text=name)
        body = nodes.field_body()
        body += nodes.paragraph(text=value)
        field += body
        return field


def setup(app: Sphinx):
    app.add_directive("examples-catalog", ExamplesCatalogDirective)
    return {"version": "0.1", "parallel_read_safe": True}
