"""CLI and HTML-render smoke tests for gxformat2.cytoscape.

Behavioral coverage of cytoscape_elements lives in declarative YAML
(gxformat2/examples/expectations/cytoscape.yml) and runs from
test_interop_tests.py — keep this file for things that aren't a pure
function of (workflow dict) -> result.
"""

import json
import os
import shutil
import tempfile

from gxformat2.cytoscape import cytoscape_elements, main, render_html
from gxformat2.cytoscape._builder import _input_type_str
from gxformat2.normalized import normalized_format2
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


def test_render_html():
    elements = cytoscape_elements(EXAMPLE_PATH)
    html = render_html(elements)
    assert "</body>" in html
    assert "cytoscape" in html


def test_multi_string_input_type():
    # Non-function-of-(wf_dict) helper: exercises the typed input directly,
    # which the declarative harness can't reach.
    nf2 = normalized_format2(ordered_load(MULTI_STRING_INPUT_WORKFLOW))
    inp = nf2.inputs[0]
    assert _input_type_str(inp) == "string[]"


def test_interop_generation():
    # not much of a test case but it will generate a directory of interoperability examples to
    # test Java against.
    write_cytoscape_elements(EXAMPLE_PATH)
    write_cytoscape_elements_for_string(WITH_REPORT, "with_report.gxwf.yml")


def write_cytoscape_elements_for_string(workflow_content, filename):
    # Stage the inline workflow at a stable, descriptive path before copying into
    # TEST_CYTOSCAPE_EXAMPLES — anonymous tempfile names leak into the interop fixture
    # directory and accumulate one tmp*.gxwf.yml per test run.
    if not os.path.exists(TEST_CYTOSCAPE_EXAMPLES):
        os.makedirs(TEST_CYTOSCAPE_EXAMPLES)
    workflow_path = os.path.join(TEST_CYTOSCAPE_EXAMPLES, filename)
    with open(workflow_path, "w") as f:
        f.write(workflow_content)
    write_cytoscape_elements(workflow_path)


def write_cytoscape_elements(workflow_path):
    if not os.path.exists(TEST_CYTOSCAPE_EXAMPLES):
        os.makedirs(TEST_CYTOSCAPE_EXAMPLES)
    base_name, ext = os.path.splitext(os.path.basename(workflow_path))
    staged_path = os.path.join(TEST_CYTOSCAPE_EXAMPLES, base_name + ext)
    if os.path.abspath(workflow_path) != os.path.abspath(staged_path):
        shutil.copyfile(workflow_path, staged_path)
    elements_path = os.path.join(TEST_CYTOSCAPE_EXAMPLES, base_name + ".cytoscape.json")
    main([workflow_path, elements_path])
