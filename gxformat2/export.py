"""Functionality for converting a standard Galaxy workflow into a format 2 workflow."""
import argparse
import json
import sys
from collections import OrderedDict

from ._labels import Labels
from .model import native_input_to_format2_type
from .yaml import ordered_dump

SCRIPT_DESCRIPTION = """
Convert a native Galaxy workflow description into a Format 2 description.
"""


def _copy_common_properties(from_native_step, to_format2_step):
    annotation = from_native_step.get("annotation", "")
    if annotation:
        to_format2_step["doc"] = annotation
    position = from_native_step.get("position", None)
    if position:
        to_format2_step["position"] = position
    when_exp = from_native_step.get("when", None)
    if when_exp is not None:
        to_format2_step["when"] = when_exp


def from_galaxy_native(format2_dict, tool_interface=None, json_wrapper=False):
    """Convert native .ga workflow definition to a format2 workflow.

    This is highly experimental and currently broken.
    """
    data = OrderedDict()
    data['class'] = 'GalaxyWorkflow'
    _copy_common_properties(format2_dict, data)
    if "name" in format2_dict:
        data["label"] = format2_dict.pop("name")
    for top_level_key in ['tags', 'uuid', 'report']:
        value = format2_dict.get(top_level_key)
        if value:
            data[top_level_key] = value

    native_steps = format2_dict.get("steps")

    label_map = {}
    all_labeled = True
    for key, step in native_steps.items():
        label = step.get("label")
        if not label:
            all_labeled = False
        label_map[str(key)] = label

    inputs = OrderedDict()
    outputs = OrderedDict()
    steps = []

    labels = Labels()

    # For each step, rebuild the form and encode the state
    for step in native_steps.values():
        for workflow_output in step.get("workflow_outputs", []):
            source = _to_source(workflow_output, label_map, output_id=step["id"])
            output_id = labels.ensure_new_output_label(workflow_output.get("label"))
            outputs[output_id] = {"outputSource": source}

        module_type = step.get("type")
        if module_type in ['data_input', 'data_collection_input', 'parameter_input']:
            step_id = step["label"]  # TODO: auto-label
            input_dict = {}
            tool_state = _tool_state(step)
            input_dict['type'] = native_input_to_format2_type(step, tool_state)
            for tool_state_key in ['optional', 'format', 'default', 'restrictions', 'suggestions', 'restrictOnConnections']:
                if tool_state_key in tool_state:
                    input_dict[tool_state_key] = tool_state[tool_state_key]

            _copy_common_properties(step, input_dict)
            # If we are only copying property - use the CWL-style short-hand
            if len(input_dict) == 1:
                inputs[step_id] = input_dict["type"]
            else:
                inputs[step_id] = input_dict
            continue

        if module_type == "pause":
            step_dict = OrderedDict()
            optional_props = ['label']
            _copy_common_properties(step, step_dict)
            _copy_properties(step, step_dict, optional_props=optional_props)
            _convert_input_connections(step, step_dict, label_map)
            step_dict["type"] = "pause"
            steps.append(step_dict)
            continue

        if module_type == 'subworkflow':
            step_dict = OrderedDict()
            optional_props = ['label']
            _copy_common_properties(step, step_dict)
            _copy_properties(step, step_dict, optional_props=optional_props)
            _convert_input_connections(step, step_dict, label_map)
            _convert_post_job_actions(step, step_dict)
            subworkflow_native_dict = step["subworkflow"]
            subworkflow = from_galaxy_native(subworkflow_native_dict, tool_interface=tool_interface, json_wrapper=False)
            step_dict["run"] = subworkflow
            steps.append(step_dict)
            continue

        if module_type != 'tool':
            raise NotImplementedError("Unhandled module type %s" % module_type)

        step_dict = OrderedDict()
        optional_props = ['label', 'tool_shed_repository']
        required_props = ['tool_id', 'tool_version']
        _copy_properties(step, step_dict, optional_props, required_props)
        _copy_common_properties(step, step_dict)

        tool_state = _tool_state(step)
        tool_state.pop("__page__", None)
        tool_state.pop("__rerun_remap_job_id__", None)
        step_dict['tool_state'] = tool_state

        _convert_input_connections(step, step_dict, label_map)
        _convert_post_job_actions(step, step_dict)
        steps.append(step_dict)

    data['inputs'] = inputs
    data['outputs'] = outputs

    if all_labeled:
        steps_dict = OrderedDict()
        for step in steps:
            label = step.pop("label")
            steps_dict[label] = step
        data['steps'] = steps_dict
    else:
        data['steps'] = steps

    if json_wrapper:
        return {
            "yaml_content": ordered_dump(data)
        }

    return data


def _tool_state(step):
    tool_state = json.loads(step['tool_state'])
    return tool_state


def _copy_properties(from_native_step, to_format2_step, optional_props=[], required_props=[]):
    for prop in optional_props:
        value = from_native_step.get(prop)
        if value:
            to_format2_step[prop] = value
    for prop in required_props:
        value = from_native_step.get(prop)
        to_format2_step[prop] = value


def _convert_input_connections(from_native_step, to_format2_step, label_map):
    in_dict = from_native_step.get("in", {}).copy()
    input_connections = from_native_step['input_connections']
    for input_name, input_defs in input_connections.items():
        if not isinstance(input_defs, list):
            input_defs = [input_defs]
        for input_def in input_defs:
            source = _to_source(input_def, label_map)
            if input_name == "__NO_INPUT_OUTPUT_NAME__":
                input_name = "$step"
                assert source.endswith("/__NO_INPUT_OUTPUT_NAME__")
                source = source[:-len("/__NO_INPUT_OUTPUT_NAME__")]
            in_dict[input_name] = {
                "source": source
            }
    to_format2_step["in"] = in_dict


def _convert_post_job_actions(from_native_step, to_format2_step):

    def _ensure_output_def(key):
        if "outputs" in to_format2_step:
            to_format2_step["out"] = to_format2_step.pop("outputs")
        elif "out" not in to_format2_step:
            to_format2_step["out"] = {}

        outputs_dict = to_format2_step["out"]
        if key not in outputs_dict:
            outputs_dict[key] = {}
        return outputs_dict[key]

    if "post_job_actions" in from_native_step:
        post_job_actions = from_native_step["post_job_actions"].copy()
        to_remove_keys = []

        for post_job_action_key, post_job_action_value in post_job_actions.items():
            action_type = post_job_action_value["action_type"]
            output_name = post_job_action_value.get("output_name")
            action_args = post_job_action_value.get("action_arguments", {})

            handled = True
            if action_type == "RenameDatasetAction":
                output_dict = _ensure_output_def(output_name)
                output_dict["rename"] = action_args["newname"]
                handled = True
            elif action_type == "HideDatasetAction":
                output_dict = _ensure_output_def(output_name)
                output_dict["hide"] = True
                handled = True
            elif action_type == "DeleteIntermediatesAction":
                output_dict = _ensure_output_def(output_name)
                output_dict["delete_intermediate_datasets"] = True
            elif action_type == "ChangeDatatypeAction":
                output_dict = _ensure_output_def(output_name)
                output_dict['change_datatype'] = action_args
                handled = True
            elif action_type == "TagDatasetAction":
                output_dict = _ensure_output_def(output_name)
                output_dict["add_tags"] = action_args["tags"].split(",")
            elif action_type == "RemoveTagDatasetAction":
                output_dict = _ensure_output_def(output_name)
                output_dict["remove_tags"] = action_args["tags"].split(",")
            elif action_type == "ColumnSetAction":
                output_dict = _ensure_output_def(output_name)
                output_dict["set_columns"] = action_args
            else:
                handled = False

            if handled:
                to_remove_keys.append(post_job_action_key)

        for to_remove in to_remove_keys:
            del post_job_actions[to_remove]

        if post_job_actions:
            to_format2_step["post_job_actions"] = post_job_actions


def _to_source(has_output_name, label_map, output_id=None):
    output_id = output_id if output_id is not None else has_output_name['id']
    output_id = str(output_id)
    output_name = has_output_name['output_name']
    output_label = label_map.get(output_id) or output_id
    if output_name == "output":
        source = output_label
    else:
        source = "%s/%s" % (output_label, output_name)
    return source


def main(argv=None):
    """Entry point for script to convert native workflows to Format 2."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)

    format2_path = args.input_path
    output_path = args.output_path or (format2_path + ".gxwf.yml")
    with open(format2_path, "r") as f:
        native_workflow_dict = json.load(f)

    as_dict = from_galaxy_native(native_workflow_dict)
    with open(output_path, "w") as f:
        ordered_dump(as_dict, f)


def _parser():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument('input_path', metavar='INPUT', type=str,
                        help='input workflow path (.ga)')
    parser.add_argument('output_path', metavar='OUTPUT', type=str, nargs="?",
                        help='output workflow path (.gxfw.yml)')
    return parser


__all__ = (
    'from_galaxy_native',
    'main',
)
