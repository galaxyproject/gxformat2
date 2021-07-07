import json
import os
import shutil
import tempfile

from gxformat2.cytoscape import main
from ._helpers import TEST_INTEROP_EXAMPLES, TEST_PATH
from .test_lint import WITH_REPORT

EXAMPLE_PATH = os.path.join(TEST_PATH, "unicycler-extra-annotations.ga")
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
