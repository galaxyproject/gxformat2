"""Tests for generated schema (v19_09.py) validation of Format2 workflows.

Validates that example workflows with pick_value steps and comments
are accepted or rejected by the schema-salad generated load_document.
"""

import os
import tempfile

import pytest
from schema_salad.exceptions import SchemaSaladException

from gxformat2.schema.v19_09 import load_document
from gxformat2.yaml import ordered_dump, ordered_load
from .example_wfs import (
    BASIC_WORKFLOW,
    RUNTIME_INPUTS,
    WORKFLOW_WITH_COMMENTS_DICT,
    WORKFLOW_WITH_COMMENTS_LIST,
    WORKFLOW_WITH_FRAME_MIXED_REFS,
)


def _load_format2(yaml_str):
    """Write workflow YAML to a temp file and validate via load_document."""
    as_dict = ordered_load(yaml_str)
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        ordered_dump(as_dict, f)
        f.flush()
        path = f.name
    try:
        from pathlib import Path

        file_uri = Path(os.path.abspath(path)).as_uri()
        return load_document(file_uri)
    finally:
        os.unlink(path)


def _load_format2_dict(as_dict):
    """Write workflow dict to a temp file and validate via load_document."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yml", delete=False) as f:
        ordered_dump(as_dict, f)
        f.flush()
        path = f.name
    try:
        from pathlib import Path

        file_uri = Path(os.path.abspath(path)).as_uri()
        return load_document(file_uri)
    finally:
        os.unlink(path)


class TestBasicSchemaValidation:

    def test_basic_workflow_validates(self):
        _load_format2(BASIC_WORKFLOW)

    def test_pause_step_validates(self):
        _load_format2(RUNTIME_INPUTS)


class TestPickValueSchema:

    PICK_VALUE_WORKFLOW = """\
class: GalaxyWorkflow
inputs:
  input_a: data
  input_b: data
outputs:
  the_output:
    outputSource: pick/output
steps:
  pick:
    type: pick_value
    in:
      input_a: input_a
      input_b: input_b
"""

    PICK_VALUE_WITH_PJA = """\
class: GalaxyWorkflow
inputs:
  input_a: data
  input_b: data
outputs:
  the_output:
    outputSource: pick/output
steps:
  pick:
    type: pick_value
    in:
      input_a: input_a
      input_b: input_b
    out:
      output:
        rename: "picked_value"
        hide: true
"""

    def test_pick_value_step_validates(self):
        _load_format2(self.PICK_VALUE_WORKFLOW)

    def test_pick_value_with_pja_validates(self):
        _load_format2(self.PICK_VALUE_WITH_PJA)

    def test_invalid_step_type_rejected(self):
        wf = ordered_load(self.PICK_VALUE_WORKFLOW)
        wf["steps"]["pick"]["type"] = "not_a_real_type"
        with pytest.raises(SchemaSaladException):
            _load_format2_dict(wf)


class TestCommentsSchema:

    def test_comments_list_validates(self):
        _load_format2(WORKFLOW_WITH_COMMENTS_LIST)

    def test_comments_dict_validates(self):
        _load_format2(WORKFLOW_WITH_COMMENTS_DICT)

    def test_comments_frame_mixed_refs_validates(self):
        _load_format2(WORKFLOW_WITH_FRAME_MIXED_REFS)

    def test_text_comment_minimal(self):
        wf = ordered_load(BASIC_WORKFLOW)
        wf["comments"] = [
            {"type": "text", "text": "hello"},
        ]
        _load_format2_dict(wf)

    def test_markdown_comment(self):
        wf = ordered_load(BASIC_WORKFLOW)
        wf["comments"] = [
            {
                "type": "markdown",
                "position": [10, 20],
                "size": [300, 200],
                "text": "# Title\nSome content.",
            },
        ]
        _load_format2_dict(wf)

    def test_frame_comment(self):
        wf = ordered_load(BASIC_WORKFLOW)
        wf["comments"] = [
            {
                "type": "frame",
                "position": [0, 0],
                "size": [800, 600],
                "title": "My Frame",
                "color": "green",
                "contains_steps": ["cat"],
            },
        ]
        _load_format2_dict(wf)

    def test_freehand_comment(self):
        wf = ordered_load(BASIC_WORKFLOW)
        wf["comments"] = [
            {
                "type": "freehand",
                "position": [100, 100],
                "size": [50, 50],
                "thickness": 2,
                "line": [[100, 100], [120, 130], [150, 160]],
            },
        ]
        _load_format2_dict(wf)

    def test_no_comments_still_valid(self):
        """Workflows without comments should still validate."""
        _load_format2(BASIC_WORKFLOW)

    def test_empty_comments_list(self):
        wf = ordered_load(BASIC_WORKFLOW)
        wf["comments"] = []
        _load_format2_dict(wf)
