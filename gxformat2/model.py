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


def ensure_step_position(step: dict, order_index: int):
    """Ensure step contains a position definition.

    Modifies the input step dictionary.
    """
    if "position" not in step:
        step["position"] = {
            "left": 10 * order_index,
            "top": 10 * order_index
        }


def inputs_as_steps(workflow_dict: dict):
    """Return workflow inputs to a steps in array - like in native Galaxy.

    workflow_dict is a Format 2 representation of a workflow. This method
    does not modify workflow_dict.
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
        elif input_type in ["text", "integer", "float", "color", "boolean"]:
            step_type = "parameter_input"
            input_def["parameter_type"] = input_type
        else:
            raise Exception("Input type must be a data file or collection.")

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
