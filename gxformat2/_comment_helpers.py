"""Helpers for converting comments between native and Format2 representations."""

from __future__ import annotations

# Mapping from native comment data.* field names to Format2 top-level field names.
_COMMENT_DATA_FIELDS: dict[str, dict[str, str]] = {
    "text": {"text": "text", "bold": "bold", "italic": "italic", "size": "text_size"},
    "markdown": {"text": "text"},
    "frame": {"title": "title"},
    "freehand": {"thickness": "thickness", "line": "line"},
}

# Fields common to all comment types (preserved as-is, minus 'id' and 'data').
_COMMENT_COMMON_FIELDS = ("type", "position", "size", "color")


def _tuples_to_lists(value):
    """Recursively convert tuples to lists for YAML serialization."""
    if isinstance(value, (tuple, list)):
        return [_tuples_to_lists(v) for v in value]
    return value


def flatten_comment_data(native_comment: dict) -> dict:
    """Convert a native comment dict to Format2 representation.

    Hoists type-specific fields from nested ``data`` dict to top level.
    Renames ``child_steps`` -> ``contains_steps`` and ``child_comments`` -> ``contains_comments``.
    Drops the ``id`` field (order_index).
    """
    comment_type = native_comment["type"]
    result: dict = {}

    for field in _COMMENT_COMMON_FIELDS:
        if field in native_comment:
            result[field] = _tuples_to_lists(native_comment[field])

    if "label" in native_comment:
        result["label"] = native_comment["label"]

    data = native_comment.get("data", {})
    field_map = _COMMENT_DATA_FIELDS.get(comment_type, {})
    for native_name, format2_name in field_map.items():
        if native_name in data:
            result[format2_name] = _tuples_to_lists(data[native_name])

    if "child_steps" in native_comment:
        result["contains_steps"] = native_comment["child_steps"]
    if "child_comments" in native_comment:
        result["contains_comments"] = native_comment["child_comments"]

    return result


def unflatten_comment_data(format2_comment: dict) -> dict:
    """Convert a Format2 comment dict to native representation.

    Collects type-specific top-level fields back into a nested ``data`` dict.
    Renames ``contains_steps`` -> ``child_steps`` and ``contains_comments`` -> ``child_comments``.
    """
    comment_type = format2_comment["type"]
    result: dict = {}

    for field in _COMMENT_COMMON_FIELDS:
        if field in format2_comment:
            result[field] = format2_comment[field]

    if "label" in format2_comment:
        result["label"] = format2_comment["label"]

    data: dict = {}
    field_map = _COMMENT_DATA_FIELDS.get(comment_type, {})
    for native_name, format2_name in field_map.items():
        if format2_name in format2_comment:
            data[native_name] = format2_comment[format2_name]
    result["data"] = data

    if "contains_steps" in format2_comment:
        result["child_steps"] = format2_comment["contains_steps"]
    if "contains_comments" in format2_comment:
        result["child_comments"] = format2_comment["contains_comments"]

    return result
