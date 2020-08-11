"""Abstractions for dealing with Format2 data."""
from typing import cast, Dict, List, Union

DictOrList = Union[Dict, List]


def convert_dict_to_id_list_if_needed(
    dict_or_list: DictOrList,
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


def with_step_ids(steps: list, inputs_offset: int = 0):
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
        step["position"] = {
            "left": 10 * order_index,
            "top": 10 * order_index
        }


def native_input_to_format2_type(step: dict, tool_state: dict) -> str:
    """Return a Format2 input type ('type') from a native input step dictionary."""
    module_type = step.get("type")
    if module_type == 'data_collection_input':
        format2_type = 'collection'
    elif module_type == 'data_input':
        format2_type = 'data'
    elif module_type == "parameter_input":
        native_type = cast(str, tool_state.get("parameter_type"))
        format2_type = native_type
        if native_type == "integer":
            format2_type = "int"
        elif native_type == "text":
            format2_type = "string"
    return format2_type


def inputs_as_normalized_steps(workflow_dict):
    """Return workflow inputs to a steps in array.

    Normalize Format2 inputs. `workflow_dict` is a Format 2 representation of
    a workflow. This method does not modify `workflow_dict`.
    """
    if "inputs" not in workflow_dict:
        return []

    inputs = workflow_dict.get("inputs", [])
    new_steps = []
    inputs = convert_dict_to_id_list_if_needed(inputs)
    for input_def_raw in with_step_ids(inputs):
        input_def = input_def_raw.copy()

        if "label" in input_def and "id" in input_def:
            raise Exception("label and id are aliases for inputs, may only define one")
        if "label" not in input_def and "id" not in input_def:
            raise Exception("Input must define a label.")

        raw_label = input_def.pop("label", None)
        raw_id = input_def.pop("id", None)
        label = raw_label or raw_id

        if label is None:
            raise Exception("Input label must not be empty.")

        step_type = input_def.pop("type", "data")
        if step_type == "File":
            step_type = "data"
        elif step_type == "integer":
            step_type = "int"
        elif step_type == "text":
            step_type = "string"

        step_def = input_def
        step_def.update({
            "type": step_type,
            "id": label,
        })
        new_steps.append(step_def)

    return new_steps


def inputs_as_native_steps(workflow_dict: dict):
    """Return workflow inputs to a steps in array - like in native Galaxy.

    Convert Format2 types into native ones. `workflow_dict` is a Format 2
    representation of a workflow. This method does not modify `workflow_dict`.
    """
    if "inputs" not in workflow_dict:
        return []

    inputs = workflow_dict.get("inputs", [])
    new_steps = []
    inputs = convert_dict_to_id_list_if_needed(inputs)
    for input_def_raw in inputs:
        input_def = input_def_raw.copy()

        if "label" in input_def and "id" in input_def:
            raise Exception("label and id are aliases for inputs, may only define one")
        if "label" not in input_def and "id" not in input_def:
            raise Exception("Input must define a label.")

        raw_label = input_def.pop("label", None)
        raw_id = input_def.pop("id", None)
        label = raw_label or raw_id

        if label is None:
            raise Exception("Input label must not be empty.")

        input_type = input_def.pop("type", "data")
        if input_type in ["File", "data", "data_input"]:
            step_type = "data_input"
        elif input_type in ["collection", "data_collection", "data_collection_input"]:
            step_type = "data_collection_input"
        elif input_type in ["text", "string", "integer", "int", "float", "color", "boolean"]:
            step_type = "parameter_input"
            format2_type = input_type
            if format2_type == "int":
                native_type = "integer"
            elif format2_type == "string":
                native_type = "text"
            else:
                native_type = format2_type
            input_def["parameter_type"] = native_type
        else:
            raise Exception("Unknown input type [%s] encountered." % input_type)

        step_def = input_def
        step_def.update({
            "type": step_type,
            "label": label,
        })
        new_steps.append(step_def)

    return new_steps


def outputs_as_list(as_python: dict) -> list:
    """Extract outputs from Format2 rep as list."""
    outputs = as_python.get("outputs", [])
    outputs = convert_dict_to_id_list_if_needed(outputs)
    return outputs
