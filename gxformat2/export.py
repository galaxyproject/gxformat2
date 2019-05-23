"""Functionality for converting a standard Galaxy workflow into a format 2 workflow."""

from collections import OrderedDict
import json

from ._yaml import ordered_dump


def _copy_common_properties(from_native_step, to_format2_step):
    annotation = from_native_step.get("annotation", "")
    if annotation:
        to_format2_step["doc"] = annotation
    position = from_native_step.get("position", None)
    if position:
        to_format2_step["position"] = position


def from_galaxy_native(native_workflow_dict, tool_interface=None, json_wrapper=False):
    """Convert native .ga workflow definition to a format2 workflow.

    This is highly experimental and currently broken.
    """
    data = OrderedDict()
    data['class'] = 'GalaxyWorkflow'
    _copy_common_properties(native_workflow_dict, data)
    for top_level_key in ['tags', 'uuid']:
        value = native_workflow_dict.get(top_level_key)
        if value:
            data[top_level_key] = value

    native_steps = native_workflow_dict.get("steps")

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

    # For each step, rebuild the form and encode the state
    for step in native_steps.values():
        for workflow_output in step.get("workflow_outputs", []):
            source = _to_source(workflow_output, label_map, output_id=step["id"])
            output_id = workflow_output["label"]
            outputs[output_id] = {"outputSource": source}

        module_type = step.get("type")
        if module_type in ['data_input', 'data_collection_input', 'parameter_input']:
            step_id = step["label"]  # TODO: auto-label
            input_dict = {}
            if module_type == 'data_collection_input':
                input_dict['type'] = 'collection'
            elif module_type == 'data_input':
                input_dict['type'] = 'data'
            elif module_type == "parameter_input":
                tool_state = _tool_state(step)
                input_dict['type'] = tool_state.get("parameter_type")
            # TODO: handle parameter_input types
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
        if "outputs" not in to_format2_step:
            to_format2_step["outputs"] = {}
        outputs_dict = to_format2_step["outputs"]
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
    output_id = output_id or has_output_name['id']
    output_id = str(output_id)
    output_name = has_output_name['output_name']
    output_label = label_map.get(output_id) or output_id
    if output_name == "output":
        source = output_label
    else:
        source = "%s/%s" % (output_label, output_name)
    return source


__all__ = (
    'from_galaxy_native',
)
