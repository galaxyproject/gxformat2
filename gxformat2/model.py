"""Abstractions for dealing with Format2 data."""

from typing import (
    Any,
    cast,
    Optional,
    Union,
)

from typing_extensions import Literal

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


def setup_connected_values(value, key: str = "", append_to: Optional[dict[str, list]] = None) -> Any:
    """Replace links with connected value."""

    def append_link(key: str, value: dict):
        if append_to is None:
            return

        if key not in append_to:
            append_to[key] = []

        assert "$link" in value
        link_value = value["$link"]
        append_to[key].append(link_value)

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
    from gxformat2.normalized._format2 import resolve_source_reference as _impl

    return _impl(value, known_labels)


def _connected_value():
    return {"__class__": "ConnectedValue"}


def _is_link(value: Any) -> bool:
    return isinstance(value, dict) and "$link" in value


def _join_prefix(prefix: Optional[str], key: str):
    if prefix:
        return f"{prefix}|{key}"
    return key


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


def _append_step_id_to_step_list_elements(steps: list[dict[str, Any]], inputs_offset: int = 0) -> None:
    """Ensure a list of steps each contains an 'id' element."""
    assert isinstance(steps, list)
    for i, step in enumerate(steps):
        if "id" not in step:
            step["id"] = i + inputs_offset
        assert step["id"] is not None
