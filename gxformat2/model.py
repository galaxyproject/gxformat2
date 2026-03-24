"""Abstractions for dealing with Format2 data."""

import logging
import os
from typing import (
    Any,
    cast,
    Optional,
    Union,
)

from typing_extensions import Literal

from gxformat2.normalized import resolve_source_reference as _resolve_source_reference

log = logging.getLogger(__name__)



_NativeGalaxyStepType = Literal[
    "subworkflow",
    "data_input",
    "data_collection_input",
    "tool",
    "pause",
    "pick_value",
    "parameter_input",
]
_GxFormat2StepTypeAlias = Literal[
    "input",
    "input_collection",
    "parameter",
]
_StepTypes = Union[_NativeGalaxyStepType, _GxFormat2StepTypeAlias]


_STEP_TYPES = [
    "subworkflow",
    "data_input",
    "data_collection_input",
    "tool",
    "pause",
    "pick_value",
    "parameter_input",
]
_STEP_TYPE_ALIASES: dict[_GxFormat2StepTypeAlias, _NativeGalaxyStepType] = {
    "input": "data_input",
    "input_collection": "data_collection_input",
    "parameter": "parameter_input",
}


def get_native_step_type(gxformat2_step_dict: dict) -> _NativeGalaxyStepType:
    """Infer native galaxy step type from the gxformat2 step as a dict."""
    specifies_subworkflow_run = bool(gxformat2_step_dict.get("run"))
    step_type_default = "tool" if not specifies_subworkflow_run else "subworkflow"
    raw_step_type = gxformat2_step_dict.get("type", step_type_default)
    if raw_step_type not in _STEP_TYPES and raw_step_type not in _STEP_TYPE_ALIASES:
        raise Exception(f"Unknown step type encountered {raw_step_type}")
    step_type: _NativeGalaxyStepType
    if raw_step_type in _STEP_TYPE_ALIASES:
        step_type = _STEP_TYPE_ALIASES[cast(_GxFormat2StepTypeAlias, raw_step_type)]
    else:
        step_type = cast(_NativeGalaxyStepType, raw_step_type)
    return step_type


# source: step#output and $link: step#output instead of outputSource: step/output and $link: step/output
SUPPORT_LEGACY_CONNECTIONS = os.environ.get("GXFORMAT2_SUPPORT_LEGACY_CONNECTIONS") == "1"


def pop_connect_from_step_dict(step: dict) -> dict:
    """Merge 'in' and 'connect' keys into a unified connection dict separated from state.

    Meant to be used an initial processing step in reasoning about connections defined by the
    format2 step description.
    """
    if "connect" not in step:
        step["connect"] = {}

    connect = step["connect"]
    del step["connect"]

    # handle CWL-style in dict connections.
    if "in" in step:
        step_in = step["in"]
        assert isinstance(step_in, dict)
        connection_keys = set()
        for key, value in step_in.items():
            # TODO: this can be a list right?
            if isinstance(value, dict) and "source" in value:
                value = value["source"]
            elif isinstance(value, dict) and "default" in value:
                continue
            elif isinstance(value, dict):
                raise KeyError(f"step input must define either source or default {value}")
            connect[key] = [value]
            connection_keys.add(key)

        for key in connection_keys:
            del step_in[key]

        if len(step_in) == 0:
            del step["in"]

    return connect


def setup_connected_values(value, key: str = "", append_to: Optional[dict[str, list]] = None) -> Any:
    """Replace links with connected value."""

    def append_link(key: str, value: dict):
        if append_to is None:
            return

        if key not in append_to:
            append_to[key] = []

        assert "$link" in value
        link_value = value["$link"]
        append_to[key].append(clean_connection(link_value))

    def recurse(sub_value, sub_key) -> Any:
        return setup_connected_values(sub_value, sub_key, append_to=append_to)

    if _is_link(value):
        append_link(key, value)
        # Filled in by the connection, so to force late
        # validation of the field just mark as ConnectedValue,
        # which should be further validated by Galaxy
        return _connected_value()
    if isinstance(value, dict):
        new_dict_values: dict[str, Any] = {}
        for dict_k, dict_v in value.items():
            new_key = _join_prefix(key, dict_k)
            new_dict_values[dict_k] = recurse(dict_v, new_key)
        return new_dict_values
    elif isinstance(value, list):
        new_list_values: list[Any] = []
        for i, list_v in enumerate(value):
            # If we are a repeat we need to modify the key
            # but not if values are actually $links.
            if _is_link(list_v):
                assert isinstance(list_v, dict)
                append_link(key, list_v)
                new_list_values.append(None)
            else:
                new_key = "%s_%d" % (key, i)
                new_list_values.append(recurse(list_v, new_key))
        return new_list_values
    else:
        return value


def resolve_source_reference(value: str, known_labels: Union[set, dict]) -> tuple:
    """Parse a source reference into (step_label_or_id, output_name).

    Deprecated: use ``gxformat2.normalized.resolve_source_reference`` directly.
    """
    return _resolve_source_reference(value, known_labels)


def clean_connection(value: str) -> str:
    """Convert legacy style connection targets with modern CWL-style ones."""
    if value and "#" in value and SUPPORT_LEGACY_CONNECTIONS:
        # Hope these are just used by Galaxy testing workflows and such, and not in production workflows.
        log.warn(f"Legacy workflow syntax for connections [{value}] will not be supported in the future")
        value = value.replace("#", "/", 1)

    return value


def _connected_value():
    return {"__class__": "ConnectedValue"}


def _is_link(value: Any) -> bool:
    return isinstance(value, dict) and "$link" in value


def _join_prefix(prefix: Optional[str], key: str):
    if prefix:
        new_key = f"{prefix}|{key}"
    else:
        new_key = key
    return new_key


def _convert_dict_to_id_list_if_needed(
    dict_or_list: Union[dict, list],
    add_label: bool = False,
    mutate: bool = False,
) -> list:
    """Convert a list or dict to a list with keys embedded.

    If `add_label` is True, embed dict keys as 'label' attribute
    else 'id'.
    """
    if isinstance(dict_or_list, dict):
        rval = []
        for key, value in dict_or_list.items():
            if not isinstance(value, dict):
                value = {"type": value}
            if not mutate:
                value = value.copy()
            if add_label:
                if value.get("label") is None:
                    value["label"] = key
            else:
                value["id"] = key
            rval.append(value)
    else:
        rval = cast(list, dict_or_list)
    return rval


def _with_step_ids(steps: list, inputs_offset: int = 0):
    """Walk over a list of steps and ensure the steps have a numeric id if otherwise missing."""
    assert isinstance(steps, list)
    new_steps = []
    for i, step in enumerate(steps):
        if "id" not in step:
            step = step.copy()
            step["id"] = i + inputs_offset
        assert step["id"] is not None
        new_steps.append(step)
    return new_steps


def ensure_step_position(step: dict, order_index: int):
    """Ensure step contains a position definition.

    Modifies the input step dictionary.
    """
    if "position" not in step:
        step["position"] = {"left": 10 * order_index, "top": 10 * order_index}


def native_input_to_format2_type(step: dict, tool_state: dict) -> Union[str, list[str]]:
    """Return a Format2 input type ('type') from a native input step dictionary."""
    module_type = step.get("type")
    if module_type == "data_collection_input":
        format2_type = "collection"
    elif module_type == "data_input":
        format2_type = "data"
    elif module_type == "parameter_input":
        native_type = cast(str, tool_state.get("parameter_type"))
        format2_type = native_type
        if native_type == "integer":
            format2_type = "int"
        elif native_type == "text":
            format2_type = "string"
        if tool_state.get("multiple", False):
            return [format2_type]
    return format2_type


def steps_as_list(
    format2_workflow: dict, add_ids: bool = False, inputs_offset: int = 0, mutate: bool = False
) -> list[dict[str, Any]]:
    """Return steps as a list, converting ID map to list representation if needed.

    This method does mutate the supplied steps, try to make progress toward not doing this.

    Add keys as labels instead of IDs. Why am I doing this?
    """
    if "steps" not in format2_workflow:
        raise Exception(f"No 'steps' key in dict, keys are {format2_workflow.keys()}")
    steps = format2_workflow["steps"]
    steps = _convert_dict_to_id_list_if_needed(steps, add_label=True, mutate=mutate)
    if add_ids:
        if mutate:
            _append_step_id_to_step_list_elements(steps, inputs_offset=inputs_offset)
        else:
            steps = _with_step_ids(steps, inputs_offset=inputs_offset)
    return steps


# Mapping from native comment data.* field names to Format2 top-level field names.
# Key = native data field name, Value = format2 field name.
_COMMENT_DATA_FIELDS: dict[str, dict[str, str]] = {
    "text": {"text": "text", "bold": "bold", "italic": "italic", "size": "text_size"},
    "markdown": {"text": "text"},
    "frame": {"title": "title"},
    "freehand": {"thickness": "thickness", "line": "line"},
}

# Fields common to all comment types (preserved as-is, minus 'id' and 'data').
_COMMENT_COMMON_FIELDS = ("type", "position", "size", "color")


def _tuples_to_lists(value):
    """Recursively convert tuples to lists for YAML serialization.

    Galaxy's Pydantic models use tuples for position/size/line coordinates,
    but YAML's OrderedDumper can't serialize tuples.
    """
    if isinstance(value, tuple):
        return [_tuples_to_lists(v) for v in value]
    if isinstance(value, list):
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

    # Copy common fields
    for field in _COMMENT_COMMON_FIELDS:
        if field in native_comment:
            result[field] = _tuples_to_lists(native_comment[field])

    # Preserve label if present
    if "label" in native_comment:
        result["label"] = native_comment["label"]

    # Flatten data fields (convert tuples to lists for YAML serialization)
    data = native_comment.get("data", {})
    field_map = _COMMENT_DATA_FIELDS.get(comment_type, {})
    for native_name, format2_name in field_map.items():
        if native_name in data:
            result[format2_name] = _tuples_to_lists(data[native_name])

    # Rename frame containment fields
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

    # Copy common fields
    for field in _COMMENT_COMMON_FIELDS:
        if field in format2_comment:
            result[field] = format2_comment[field]

    # Preserve label if present
    if "label" in format2_comment:
        result["label"] = format2_comment["label"]

    # Build data dict from flattened fields
    data: dict = {}
    field_map = _COMMENT_DATA_FIELDS.get(comment_type, {})
    # Invert: format2_name -> native_name
    for native_name, format2_name in field_map.items():
        if format2_name in format2_comment:
            data[native_name] = format2_comment[format2_name]
    result["data"] = data

    # Rename frame containment fields back
    if "contains_steps" in format2_comment:
        result["child_steps"] = format2_comment["contains_steps"]
    if "contains_comments" in format2_comment:
        result["child_comments"] = format2_comment["contains_comments"]

    return result


def _append_step_id_to_step_list_elements(steps: list[dict[str, Any]], inputs_offset: int = 0) -> None:
    """Ensure a list of steps each contains an 'id' element."""
    assert isinstance(steps, list)
    for i, step in enumerate(steps):
        if "id" not in step:
            step["id"] = i + inputs_offset
        assert step["id"] is not None
