"""Tests for native .ga workflow schema validation.

Validates that native Galaxy workflow documents can be loaded by the
schema-salad generated loader for the native_v0_1 schema.

When GXFORMAT2_TEST_IWC_DIRECTORY is set, also validates all .ga files
found in that IWC checkout.
"""

import json
import os
import tempfile

import pytest

from gxformat2.schema.native_v0_1 import load_document

from ._helpers import find_iwc_ga_files, IWC_DIR, iwc_fixture_ids


def _load_native(workflow_dict):
    """Inject class marker, remap hyphenated keys, write to temp file, validate."""
    doc = dict(workflow_dict)
    doc["class"] = "NativeGalaxyWorkflow"
    if "format-version" in doc:
        doc["format_version"] = doc.pop("format-version")
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json.dump(doc, f)
        f.flush()
        path = f.name
    try:
        from pathlib import Path

        return load_document(Path(os.path.abspath(path)).as_uri())
    finally:
        os.unlink(path)


MINIMAL_WORKFLOW = {
    "a_galaxy_workflow": "true",
    "format-version": "0.1",
    "name": "Minimal Test",
    "steps": {
        "0": {
            "id": 0,
            "type": "data_input",
            "name": "Input dataset",
            "label": "the_input",
            "tool_state": '{"optional": false}',
            "input_connections": {},
            "inputs": [{"name": "the_input", "description": ""}],
            "outputs": [],
            "workflow_outputs": [],
        }
    },
}

TOOL_STEP_WORKFLOW = {
    "a_galaxy_workflow": "true",
    "format-version": "0.1",
    "name": "Tool Step Test",
    "steps": {
        "0": {
            "id": 0,
            "type": "data_input",
            "name": "Input dataset",
            "label": "input1",
            "tool_state": '{"optional": false}',
            "input_connections": {},
            "inputs": [{"name": "input1", "description": ""}],
            "outputs": [],
            "workflow_outputs": [],
        },
        "1": {
            "id": 1,
            "type": "tool",
            "name": "Cat",
            "label": "cat_step",
            "tool_id": "cat1",
            "tool_version": "1.0.0",
            "tool_state": '{"input1": {"__class__": "ConnectedValue"}}',
            "input_connections": {"input1": {"id": 0, "output_name": "output"}},
            "inputs": [],
            "outputs": [{"name": "out_file1", "type": "input"}],
            "workflow_outputs": [{"label": "output1", "output_name": "out_file1", "uuid": None}],
        },
    },
}


class TestNativeSchemaBasic:

    def test_minimal_workflow(self):
        _load_native(MINIMAL_WORKFLOW)

    def test_tool_step(self):
        _load_native(TOOL_STEP_WORKFLOW)

    def test_with_tags(self):
        wf = dict(MINIMAL_WORKFLOW, tags=["test", "example"])
        _load_native(wf)

    def test_with_annotation(self):
        wf = dict(MINIMAL_WORKFLOW, annotation="A test workflow")
        _load_native(wf)

    def test_with_comments(self):
        wf = dict(
            MINIMAL_WORKFLOW,
            comments=[
                {
                    "id": 0,
                    "type": "text",
                    "position": [100, 200],
                    "size": [200, 50],
                    "color": "none",
                    "data": {"text": "A note", "bold": False, "italic": False, "size": 1},
                }
            ],
        )
        _load_native(wf)

    def test_with_report(self):
        wf = dict(MINIMAL_WORKFLOW, report={"markdown": "# Report\nSome content."})
        _load_native(wf)

    def test_with_source_metadata_url(self):
        wf = dict(
            MINIMAL_WORKFLOW,
            source_metadata={"url": "https://example.com/workflow.ga"},
        )
        _load_native(wf)

    def test_with_source_metadata_trs(self):
        wf = dict(
            MINIMAL_WORKFLOW,
            source_metadata={
                "trs_tool_id": "#workflow/github.com/user/repo/workflow",
                "trs_version_id": "master",
                "trs_server": "dockstore",
                "trs_url": "https://dockstore.org/api/ga4gh/trs/v2/tools/...",
            },
        )
        _load_native(wf)

    def test_with_creator_person(self):
        wf = dict(
            MINIMAL_WORKFLOW,
            creator=[
                {
                    "class": "Person",
                    "name": "Jane Doe",
                    "identifier": "https://orcid.org/0000-0001-2345-6789",
                    "url": "https://github.com/janedoe",
                }
            ],
        )
        _load_native(wf)

    def test_with_creator_person_full(self):
        wf = dict(
            MINIMAL_WORKFLOW,
            creator=[
                {
                    "class": "Person",
                    "name": "Dr. Jane Doe",
                    "givenName": "Jane",
                    "familyName": "Doe",
                    "honorificPrefix": "Dr",
                    "honorificSuffix": "PhD",
                    "jobTitle": "Research Scientist",
                    "identifier": "https://orcid.org/0000-0001-2345-6789",
                    "email": "mailto:jane@example.com",
                    "url": "https://example.com/jane",
                    "image": "https://example.com/jane.jpg",
                    "alternateName": "J. Doe",
                }
            ],
        )
        _load_native(wf)

    def test_with_creator_organization(self):
        wf = dict(
            MINIMAL_WORKFLOW,
            creator=[
                {
                    "class": "Organization",
                    "name": "Galaxy Project",
                    "url": "https://galaxyproject.org",
                }
            ],
        )
        _load_native(wf)

    def test_with_creator_mixed(self):
        wf = dict(
            MINIMAL_WORKFLOW,
            creator=[
                {
                    "class": "Person",
                    "name": "Jane Doe",
                    "identifier": "https://orcid.org/0000-0001-2345-6789",
                },
                {
                    "class": "Organization",
                    "name": "Galaxy Project",
                    "url": "https://galaxyproject.org",
                    "image": "https://galaxyproject.org/logo.png",
                },
            ],
        )
        _load_native(wf)


# --- IWC integration tests ---

GA_FILES = find_iwc_ga_files()


@pytest.mark.skipif(IWC_DIR is None, reason="GXFORMAT2_TEST_IWC_DIRECTORY not set")
class TestIWCWorkflows:

    @pytest.fixture(
        params=GA_FILES,
        ids=iwc_fixture_ids(GA_FILES),
    )
    def ga_workflow(self, request):
        with open(request.param) as f:
            return json.load(f)

    def test_validates(self, ga_workflow):
        _load_native(ga_workflow)
