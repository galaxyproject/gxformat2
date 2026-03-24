"""Tests for workflow comment support."""

import pytest

from gxformat2._comment_helpers import (
    flatten_comment_data,
    unflatten_comment_data,
)
from gxformat2.export import from_galaxy_native

from ._helpers import (
    from_native,
    round_trip,
    to_native,
)
from .example_wfs import (
    WORKFLOW_WITH_COMMENTS_DICT,
    WORKFLOW_WITH_COMMENTS_LIST,
    WORKFLOW_WITH_FRAME_MIXED_REFS,
)

# -- flatten / unflatten helpers --


def test_flatten_text_comment():
    native = {
        "id": 0,
        "type": "text",
        "position": [100, 200],
        "size": [200, 50],
        "color": "blue",
        "data": {"text": "Hello", "size": 2, "bold": True, "italic": False},
    }
    flat = flatten_comment_data(native)
    assert flat["text"] == "Hello"
    assert flat["text_size"] == 2
    assert flat["bold"] is True
    assert flat["italic"] is False
    assert "data" not in flat
    assert flat["type"] == "text"
    assert flat["position"] == [100, 200]


def test_unflatten_text_comment():
    flat = {
        "type": "text",
        "position": [100, 200],
        "size": [200, 50],
        "color": "blue",
        "text": "Hello",
        "text_size": 2,
        "bold": True,
    }
    native = unflatten_comment_data(flat)
    assert native["data"]["text"] == "Hello"
    assert native["data"]["size"] == 2
    assert native["data"]["bold"] is True
    assert "text" not in native
    assert "text_size" not in native
    assert "bold" not in native


def test_flatten_markdown_comment():
    native = {
        "id": 0,
        "type": "markdown",
        "position": [0, 0],
        "size": [400, 300],
        "color": "none",
        "data": {"text": "# Title\nBody"},
    }
    flat = flatten_comment_data(native)
    assert flat["text"] == "# Title\nBody"
    assert "data" not in flat


def test_flatten_frame_comment():
    native = {
        "id": 0,
        "type": "frame",
        "position": [50, 50],
        "size": [600, 400],
        "color": "green",
        "data": {"title": "My Frame"},
        "child_steps": [0, 1],
        "child_comments": [2],
    }
    flat = flatten_comment_data(native)
    assert flat["title"] == "My Frame"
    assert flat["contains_steps"] == [0, 1]
    assert flat["contains_comments"] == [2]
    assert "child_steps" not in flat
    assert "child_comments" not in flat
    assert "data" not in flat


def test_unflatten_frame_comment():
    flat = {
        "type": "frame",
        "position": [50, 50],
        "size": [600, 400],
        "color": "green",
        "title": "My Frame",
        "contains_steps": [0, 1],
        "contains_comments": [2],
    }
    native = unflatten_comment_data(flat)
    assert native["data"]["title"] == "My Frame"
    assert native["child_steps"] == [0, 1]
    assert native["child_comments"] == [2]
    assert "contains_steps" not in native
    assert "contains_comments" not in native


def test_flatten_freehand_comment():
    native = {
        "id": 0,
        "type": "freehand",
        "position": [200, 300],
        "size": [100, 80],
        "color": "red",
        "data": {"thickness": 3, "line": [[210, 310], [220, 330]]},
    }
    flat = flatten_comment_data(native)
    assert flat["thickness"] == 3
    assert flat["line"] == [[210, 310], [220, 330]]
    assert "data" not in flat


def test_roundtrip_flatten_unflatten():
    """All 4 types round-trip through flatten/unflatten."""
    natives = [
        {
            "id": 0,
            "type": "text",
            "position": [100, 200],
            "size": [200, 50],
            "color": "blue",
            "data": {"text": "Hello", "size": 2, "bold": True},
        },
        {
            "id": 1,
            "type": "markdown",
            "position": [0, 0],
            "size": [400, 300],
            "color": "none",
            "data": {"text": "# Title"},
        },
        {
            "id": 2,
            "type": "frame",
            "position": [50, 50],
            "size": [600, 400],
            "color": "green",
            "data": {"title": "Frame"},
            "child_steps": [0],
            "child_comments": [0, 1],
        },
        {
            "id": 3,
            "type": "freehand",
            "position": [200, 300],
            "size": [100, 80],
            "color": "red",
            "data": {"thickness": 3, "line": [[1, 2], [3, 4]]},
        },
    ]
    for native in natives:
        flat = flatten_comment_data(native)
        restored = unflatten_comment_data(flat)
        # id is stripped during flatten, add it back for comparison
        restored["id"] = native["id"]
        assert restored == native, f"Round-trip failed for type={native['type']}"


# -- native -> format2 (export) --


def _make_native_workflow_with_comments(comments, steps=None):
    """Build a minimal native workflow dict with comments."""
    if steps is None:
        steps = {
            "0": {
                "id": 0,
                "type": "data_input",
                "label": "the_input",
                "annotation": "",
                "tool_state": '{"name": "the_input"}',
                "input_connections": {},
                "workflow_outputs": [],
            },
            "1": {
                "id": 1,
                "type": "tool",
                "label": "cat",
                "annotation": "",
                "tool_id": "cat1",
                "tool_version": "1.0",
                "tool_state": '{"__page__": 0}',
                "input_connections": {"input1": [{"id": 0, "output_name": "output"}]},
                "workflow_outputs": [],
            },
        }
    return {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "Test",
        "steps": steps,
        "comments": comments,
    }


def test_native_to_format2_text_comment():
    native = _make_native_workflow_with_comments(
        [
            {
                "id": 0,
                "type": "text",
                "position": [100, 200],
                "size": [200, 50],
                "color": "blue",
                "data": {"text": "Check adapters", "size": 2, "bold": True},
            }
        ]
    )
    fmt2 = from_native(native)
    assert "comments" in fmt2
    comments = fmt2["comments"]
    assert isinstance(comments, list)
    assert len(comments) == 1
    c = comments[0]
    assert c["type"] == "text"
    assert c["text"] == "Check adapters"
    assert c["text_size"] == 2
    assert c["bold"] is True
    assert "data" not in c


def test_native_to_format2_frame_labels():
    """Frame child_steps/child_comments indices resolve to step/comment labels."""
    native = _make_native_workflow_with_comments(
        [
            {
                "id": 0,
                "type": "text",
                "position": [100, 200],
                "size": [200, 50],
                "color": "none",
                "data": {"text": "A note", "size": 1},
                "label": "my_note",
            },
            {
                "id": 1,
                "type": "frame",
                "position": [50, 50],
                "size": [600, 400],
                "color": "green",
                "data": {"title": "Preprocessing"},
                "child_steps": [1],  # step index 1 = "cat"
                "child_comments": [0],  # comment index 0 = "my_note"
                "label": "my_frame",
            },
        ]
    )
    fmt2 = from_native(native)
    comments = fmt2["comments"]
    # all labeled -> should be dict
    assert isinstance(comments, dict)
    frame = comments["my_frame"]
    assert frame["contains_steps"] == ["cat"]
    assert frame["contains_comments"] == ["my_note"]


def test_native_to_format2_comments_as_dict():
    """All comments labeled -> dict output."""
    native = _make_native_workflow_with_comments(
        [
            {
                "id": 0,
                "type": "text",
                "position": [100, 200],
                "size": [200, 50],
                "color": "none",
                "data": {"text": "Note 1", "size": 1},
                "label": "note1",
            },
            {
                "id": 1,
                "type": "text",
                "position": [200, 300],
                "size": [200, 50],
                "color": "none",
                "data": {"text": "Note 2", "size": 1},
                "label": "note2",
            },
        ]
    )
    fmt2 = from_native(native)
    assert isinstance(fmt2["comments"], dict)
    assert "note1" in fmt2["comments"]
    assert "note2" in fmt2["comments"]


def test_native_to_format2_comments_as_list():
    """Unlabeled comments -> list output."""
    native = _make_native_workflow_with_comments(
        [
            {
                "id": 0,
                "type": "text",
                "position": [100, 200],
                "size": [200, 50],
                "color": "none",
                "data": {"text": "Note 1", "size": 1},
            },
        ]
    )
    fmt2 = from_native(native)
    assert isinstance(fmt2["comments"], list)


def test_native_to_format2_no_comments():
    """No comments key if native has empty or missing comments."""
    native = _make_native_workflow_with_comments([])
    fmt2 = from_native(native)
    assert "comments" not in fmt2


# -- format2 -> native (converter) --


def test_format2_to_native_text_comment():
    native = to_native(WORKFLOW_WITH_COMMENTS_LIST)
    assert "comments" in native
    comments = native["comments"]
    assert len(comments) == 3
    text_comment = comments[0]
    assert text_comment["type"] == "text"
    assert text_comment["data"]["text"] == "Check adapters"
    assert text_comment["data"]["size"] == 2
    assert text_comment["data"]["bold"] is True
    assert text_comment["id"] == 0


def test_format2_to_native_comments_dict():
    native = to_native(WORKFLOW_WITH_COMMENTS_DICT)
    assert "comments" in native
    comments = native["comments"]
    assert len(comments) == 3
    # Find frame comment
    frame = [c for c in comments if c["type"] == "frame"][0]
    assert frame["data"]["title"] == "Preprocessing"


def test_format2_to_native_frame_references():
    """contains_steps label strings resolve to step integer indices."""
    native = to_native(WORKFLOW_WITH_COMMENTS_DICT)
    comments = native["comments"]
    frame = [c for c in comments if c["type"] == "frame"][0]
    # "cat" step is step index 1 (index 0 is the_input)
    assert 1 in frame["child_steps"]
    # adapter_warning and preprocessing_docs are comment indices 0 and 1
    assert 0 in frame["child_comments"]
    assert 1 in frame["child_comments"]


def test_format2_to_native_mixed_frame_refs():
    """Frame contains_comments with mix of label strings and integer indices."""
    native = to_native(WORKFLOW_WITH_FRAME_MIXED_REFS)
    comments = native["comments"]
    frame = [c for c in comments if c["type"] == "frame"][0]
    # "my_note" is comment 0, integer 1 stays as 1
    assert 0 in frame["child_comments"]
    assert 1 in frame["child_comments"]
    # "cat" step is step index 1
    assert 1 in frame["child_steps"]


# -- round-trip tests --


def test_comments_round_trip_list():
    fmt2 = round_trip(WORKFLOW_WITH_COMMENTS_LIST)
    assert "comments" in fmt2
    comments = fmt2["comments"]
    assert isinstance(comments, list)
    assert len(comments) == 3
    text_c = comments[0]
    assert text_c["text"] == "Check adapters"
    assert text_c["text_size"] == 2


def test_comments_round_trip_dict():
    fmt2 = round_trip(WORKFLOW_WITH_COMMENTS_DICT)
    assert "comments" in fmt2
    comments = fmt2["comments"]
    assert isinstance(comments, dict)
    assert "adapter_warning" in comments
    assert "preprocessing_docs" in comments
    assert "preprocessing" in comments
    frame = comments["preprocessing"]
    assert frame["contains_steps"] == ["cat"]
    assert "adapter_warning" in frame["contains_comments"]
    assert "preprocessing_docs" in frame["contains_comments"]


def test_comments_round_trip_mixed_refs():
    fmt2 = round_trip(WORKFLOW_WITH_FRAME_MIXED_REFS)
    comments = fmt2["comments"]
    assert isinstance(comments, list)
    frame = [c for c in comments if c["type"] == "frame"][0]
    assert "cat" in frame["contains_steps"]
    # my_note should resolve to label, index 1 stays as index (unlabeled)
    assert "my_note" in frame["contains_comments"]
    assert 1 in frame["contains_comments"]


def test_native_to_format2_compact_strips_position():
    """Compact mode strips position and size from comments."""
    native = _make_native_workflow_with_comments(
        [
            {
                "id": 0,
                "type": "text",
                "position": [100, 200],
                "size": [200, 50],
                "color": "blue",
                "data": {"text": "Note", "size": 1},
            },
        ]
    )
    fmt2 = from_galaxy_native(native, compact=True)
    assert "comments" in fmt2
    c = fmt2["comments"][0]
    assert "position" not in c
    assert "size" not in c
    assert c["text"] == "Note"


def test_format2_to_native_bad_comment_label():
    """Bad label reference in contains_comments raises clear error."""
    bad_wf = """
class: GalaxyWorkflow
inputs:
  the_input: data
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  my_frame:
    type: frame
    position: [50, 50]
    size: [600, 400]
    color: none
    title: Frame
    contains_comments:
      - nonexistent_label
"""
    with pytest.raises(Exception, match="unknown comment label"):
        to_native(bad_wf)


def test_round_trip_text_all_optional_fields():
    """Text comment with all optional fields (bold, italic) round-trips."""
    fmt2 = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input: data
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  - type: text
    position: [100, 200]
    size: [200, 50]
    color: blue
    text: "Styled note"
    text_size: 3
    bold: true
    italic: true
""")
    c = fmt2["comments"][0]
    assert c["text"] == "Styled note"
    assert c["text_size"] == 3
    assert c["bold"] is True
    assert c["italic"] is True


def test_round_trip_text_minimal_fields():
    """Text comment with only required fields (no bold/italic)."""
    fmt2 = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input: data
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  - type: text
    position: [10, 20]
    size: [100, 30]
    color: none
    text: "Plain"
    text_size: 1
""")
    c = fmt2["comments"][0]
    assert c["text"] == "Plain"
    assert c["text_size"] == 1
    assert "bold" not in c
    assert "italic" not in c


def test_round_trip_markdown():
    """Markdown comment round-trips with multiline text."""
    fmt2 = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input: data
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  - type: markdown
    position: [300, 50]
    size: [400, 300]
    color: none
    text: |
      # Heading
      Some **bold** text and a list:
      - item 1
      - item 2
""")
    c = fmt2["comments"][0]
    assert c["type"] == "markdown"
    assert "# Heading" in c["text"]
    assert "**bold**" in c["text"]
    assert c["position"] == [300, 50]
    assert c["size"] == [400, 300]


def test_round_trip_freehand():
    """Freehand comment round-trips with line coordinates."""
    fmt2 = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input: data
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  - type: freehand
    position: [200, 300]
    size: [100, 80]
    color: red
    thickness: 5
    line: [[210, 310], [220, 330], [250, 360], [270, 350]]
""")
    c = fmt2["comments"][0]
    assert c["type"] == "freehand"
    assert c["thickness"] == 5
    assert c["line"] == [[210, 310], [220, 330], [250, 360], [270, 350]]
    assert c["color"] == "red"
    assert c["position"] == [200, 300]
    assert c["size"] == [100, 80]


def test_round_trip_frame_no_children():
    """Frame with no contained steps or comments round-trips."""
    fmt2 = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input: data
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  - type: frame
    position: [10, 10]
    size: [500, 500]
    color: yellow
    title: Empty Frame
""")
    c = fmt2["comments"][0]
    assert c["type"] == "frame"
    assert c["title"] == "Empty Frame"
    assert c["color"] == "yellow"
    assert "contains_steps" not in c
    assert "contains_comments" not in c


def test_round_trip_all_types_together():
    """All 4 comment types in a single workflow round-trip with full fields."""
    fmt2 = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input: data
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  note:
    type: text
    position: [100, 200]
    size: [200, 50]
    color: blue
    text: "Important"
    text_size: 2
    bold: true
    italic: false

  docs:
    type: markdown
    position: [300, 50]
    size: [400, 300]
    color: none
    text: "# Docs"

  group:
    type: frame
    position: [50, 50]
    size: [700, 500]
    color: green
    title: All Steps
    contains_steps:
      - cat
    contains_comments:
      - note
      - docs

  sketch:
    type: freehand
    position: [600, 100]
    size: [50, 50]
    color: red
    thickness: 2
    line: [[610, 110], [620, 120]]
""")
    comments = fmt2["comments"]
    assert isinstance(comments, dict)
    assert len(comments) == 4

    assert comments["note"]["bold"] is True
    assert comments["note"]["italic"] is False
    assert comments["docs"]["text"] == "# Docs"
    assert comments["group"]["contains_steps"] == ["cat"]
    assert set(comments["group"]["contains_comments"]) == {"note", "docs"}
    assert comments["sketch"]["thickness"] == 2
    assert comments["sketch"]["line"] == [[610, 110], [620, 120]]
