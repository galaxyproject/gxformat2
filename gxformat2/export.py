"""Functionality for converting a standard Galaxy workflow into a format 2 workflow."""

from collections import OrderedDict
import json

import yaml

try:
    from galaxy.model.custom_types import MutationDict
except ImportError:
    MutationDict = None


# copy-paste from configmanage.py
def _ordered_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds):
    class OrderedDumper(Dumper):
        pass

    def _dict_representer(dumper, data):
        return dumper.represent_mapping(
            yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
            list(data.items()))
    OrderedDumper.add_representer(OrderedDict, _dict_representer)
    if MutationDict is not None:
        OrderedDumper.add_representer(MutationDict, _dict_representer)
    return yaml.dump(data, stream, OrderedDumper, **kwds)


def from_galaxy_native(native_workflow_dict, tool_interface=None, json_wrapper=False):
    """Convert native .ga workflow definition to a format2 workflow.

    This is highly experimental and currently broken.
    """
    data = OrderedDict()
    data['class'] = 'GalaxyWorkflow'
    for top_level_key in ['annotation', 'tags', 'uuid']:
        value = native_workflow_dict.get(top_level_key)
        if value:
            data[top_level_key] = value

    native_steps = native_workflow_dict.get("steps")

    label_map = {}
    for key, step in native_steps.items():
        label = step.get("label")
        label_map[str(key)] = label

    inputs = []
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
            input_dict = {
                'id': step['label']
            }
            if module_type == 'data_collection_input':
                input_dict['type'] = 'collection'
            # TODO: handle parameter_input types
            inputs.append(input_dict)
            continue

        if module_type == 'subworkflow':
            step_dict = OrderedDict()
            optional_props = ['label', 'annotation']
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
        optional_props = ['label', 'annotation', 'tool_shed_repository']
        required_props = ['tool_id', 'tool_version']
        _copy_properties(step, step_dict, optional_props, required_props)

        tool_state = json.loads(step['tool_state'])
        tool_state.pop("__page__")
        tool_state.pop("__rerun_remap_job_id__")
        step_dict['tool_state'] = tool_state

        _convert_input_connections(step, step_dict, label_map)
        _convert_post_job_actions(step, step_dict)
        steps.append(step_dict)

    data['inputs'] = inputs
    data['outputs'] = outputs
    data['steps'] = steps

    if json_wrapper:
        return {
            "yaml_content": _ordered_dump(data)
        }

    return data


def _copy_properties(from_native_step, to_format2_step, optional_props=[], required_props=[]):
    for prop in optional_props:
        value = from_native_step.get(prop)
        if value:
            to_format2_step[prop] = value
    for prop in required_props:
        value = from_native_step.get(prop)
        to_format2_step[prop] = value


def _convert_input_connections(from_native_step, to_format2_step, label_map):
    in_dict = {}
    input_connections = from_native_step['input_connections']
    for input_name, input_def in input_connections.items():
        source = _to_source(input_def, label_map)
        in_dict[input_name] = {
            "source": source
        }
    to_format2_step["in"] = in_dict


def _convert_post_job_actions(from_native_step, to_format2_step):
    if "post_job_actions" in from_native_step:
        post_job_actions = from_native_step["post_job_actions"].copy()
        for key, value in post_job_actions.items():
            if isinstance(value, dict) and "action_arguments" in value:
                action_arguments = value["action_arguments"]
                print(action_arguments)
                print(type(action_arguments))
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
