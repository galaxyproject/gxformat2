import json
import os
import shutil
import tempfile

from gxformat2.cytoscape import cytoscape_elements, CytoscapeElements, main
from gxformat2.cytoscape._builder import _input_type_str
from gxformat2.normalized import ensure_format2, normalized_format2
from gxformat2.yaml import ordered_load

from ._helpers import example_path, TEST_INTEROP_EXAMPLES
from .example_wfs import MULTI_STRING_INPUT_WORKFLOW
from .test_lint import WITH_REPORT

EXAMPLE_PATH = example_path("real-hacked-unicycler-assembly-extra-annotations.ga")
TEST_CYTOSCAPE_EXAMPLES = os.path.join(TEST_INTEROP_EXAMPLES, "cytoscape")


def test_main_output_json():
    out_file = tempfile.NamedTemporaryFile(prefix="cytoscape_elements", suffix=".json")
    main([EXAMPLE_PATH, out_file.name])
    with open(out_file.name) as f:
        elements = json.load(f)
    assert isinstance(elements, list)
    assert "</body>" not in open(out_file.name).read()


def test_main_output_html():
    out_file = tempfile.NamedTemporaryFile(prefix="cytoscape_elements", suffix=".html")
    main([EXAMPLE_PATH, out_file.name])
    assert "</body>" in open(out_file.name).read()


def test_interop_generation():
    # not much of a test case but it will generate a directory of interoperability examples to
    # test Java against.
    write_cytoscape_elements(EXAMPLE_PATH)
    write_cytoscape_elements_for_string(WITH_REPORT)


def test_cytoscape_elements_returns_typed_model():
    elements = cytoscape_elements(EXAMPLE_PATH)
    assert isinstance(elements, CytoscapeElements)
    assert len(elements.nodes) > 0
    assert len(elements.edges) > 0
    # to_list round-trips to the flat format cytoscape.js expects
    flat = elements.to_list()
    assert isinstance(flat, list)
    assert all(e["group"] in ("nodes", "edges") for e in flat)


def test_cytoscape_elements_from_nf2():
    nf2 = ensure_format2(EXAMPLE_PATH)
    elements = cytoscape_elements(nf2)
    assert isinstance(elements, CytoscapeElements)
    assert len(elements.nodes) == len(nf2.inputs) + len(nf2.steps)


def test_render_html():
    from gxformat2.cytoscape import render_html

    elements = cytoscape_elements(EXAMPLE_PATH)
    html = render_html(elements)
    assert "</body>" in html
    assert "cytoscape" in html


def test_multi_string_input_type():
    nf2 = normalized_format2(ordered_load(MULTI_STRING_INPUT_WORKFLOW))
    inp = nf2.inputs[0]
    assert _input_type_str(inp) == "string[]"


def write_cytoscape_elements_for_string(workflow_content):
    f = tempfile.NamedTemporaryFile(mode="w", suffix=".gxwf.yml")
    f.write(workflow_content)
    f.flush()
    write_cytoscape_elements(f.name)


def write_cytoscape_elements(workflow_path):
    if not os.path.exists(TEST_CYTOSCAPE_EXAMPLES):
        os.makedirs(TEST_CYTOSCAPE_EXAMPLES)
    base_name, ext = os.path.splitext(os.path.basename(workflow_path))
    shutil.copyfile(workflow_path, os.path.join(TEST_CYTOSCAPE_EXAMPLES, base_name + ext))
    elements_path = os.path.join(TEST_CYTOSCAPE_EXAMPLES, base_name + ".cytoscape.json")
    main([workflow_path, elements_path])
