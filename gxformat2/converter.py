"""Functionality for converting a Format 2 workflow into a standard Galaxy workflow."""
from __future__ import print_function

import argparse
import copy
import json
import logging
import os
import sys
import uuid
from collections import OrderedDict
from typing import Dict, Optional

from ._labels import Labels
from .model import (
    convert_dict_to_id_list_if_needed,
    ensure_step_position,
    inputs_as_native_steps,
    with_step_ids,
)
from .yaml import ordered_load

SCRIPT_DESCRIPTION = """
Convert a Format 2 Galaxy workflow description into a native format.
"""

# source: step#output and $link: step#output instead of outputSource: step/output and $link: step/output
SUPPORT_LEGACY_CONNECTIONS = os.environ.get("GXFORMAT2_SUPPORT_LEGACY_CONNECTIONS") == "1"
STEP_TYPES = [
    "subworkflow",
    "data_input",
    "data_collection_input",
    "tool",
    "pause",
    "parameter_input",
]

STEP_TYPE_ALIASES = {
    'input': 'data_input',
    'input_collection': 'data_collection_input',
    'parameter': 'parameter_input',
}

RUN_ACTIONS_TO_STEPS = {
    'GalaxyWorkflow': 'run_workflow_to_step',
    'GalaxyTool': 'run_tool_to_step',
}

POST_JOB_ACTIONS = {
    'hide': {
        'action_class': "HideDatasetAction",
        'default': False,
        'arguments': lambda x: x,
    },
    'rename': {
        'action_class': 'RenameDatasetAction',
        'default': {},
        'arguments': lambda x: {'newname': x},
    },
    'delete_intermediate_datasets': {
        'action_class': 'DeleteIntermediatesAction',
        'default': False,
        'arguments': lambda x: x,
    },
    'change_datatype': {
        'action_class': 'ChangeDatatypeAction',
        'default': {},
        'arguments': lambda x: {'newtype': x},
    },
    'set_columns': {
        'action_class': 'ColumnSetAction',
        'default': {},
        'arguments': lambda x: x,
    },
    'add_tags': {
        'action_class': 'TagDatasetAction',
        'default': [],
        'arguments': lambda x: {'tags': ",".join(x)},
    },
    'remove_tags': {
        'action_class': 'RemoveTagDatasetAction',
        'default': [],
        'arguments': lambda x: {'tags': ",".join(x)},
    },
}

log = logging.getLogger(__name__)


def rename_arg(argument):
    return argument


def clean_connection(value):
    if value and "#" in value and SUPPORT_LEGACY_CONNECTIONS:
        # Hope these are just used by Galaxy testing workflows and such, and not in production workflows.
        log.warn("Legacy workflow syntax for connections [%s] will not be supported in the future" % value)
        value = value.replace("#", "/", 1)
    else:
        return value


class ImportOptions(object):

    def __init__(self):
        self.deduplicate_subworkflows = False


def yaml_to_workflow(has_yaml, galaxy_interface, workflow_directory, import_options=None):
    """Convert a Format 2 workflow into standard Galaxy format from supplied stream."""
    as_python = ordered_load(has_yaml)
    return python_to_workflow(as_python, galaxy_interface, workflow_directory, import_options=import_options)


def python_to_workflow(as_python, galaxy_interface, workflow_directory=None, import_options=None):
    """Convert a Format 2 workflow into standard Galaxy format from supplied dictionary."""
    if "yaml_content" in as_python:
        as_python = ordered_load(as_python["yaml_content"])

    if workflow_directory is None:
        workflow_directory = os.path.abspath(".")

    conversion_context = ConversionContext(
        galaxy_interface,
        workflow_directory,
        import_options,
    )
    as_python = _preprocess_graphs(as_python, conversion_context)
    subworkflows = None
    if conversion_context.import_options.deduplicate_subworkflows:
        # TODO: import only required workflows...
        # TODO: dag sort these...
        subworkflows = OrderedDict()
        for graph_id, subworkflow_content in conversion_context.graph_ids.items():
            if graph_id == "main":
                continue
            subworkflow_conversion_context = conversion_context.get_subworkflow_conversion_context_graph("#" + graph_id)
            subworkflows[graph_id] = _python_to_workflow(copy.deepcopy(subworkflow_content), subworkflow_conversion_context)
    converted = _python_to_workflow(as_python, conversion_context)
    if subworkflows is not None:
        converted["subworkflows"] = subworkflows
    return converted


# move to a utils file?
def steps_as_list(format2_workflow: dict, add_ids: bool = False, inputs_offset: int = 0, mutate: bool = False):
    """Return steps as a list, converting ID map to list representation if needed.

    This method does mutate the supplied steps, try to make progress toward not doing this.

    Add keys as labels instead of IDs. Why am I doing this?
    """
    if "steps" not in format2_workflow:
        raise Exception("No 'steps' key in dict, keys are %s" % format2_workflow.keys())
    steps = format2_workflow["steps"]
    steps = convert_dict_to_id_list_if_needed(steps, add_label=True, mutate=mutate)
    if add_ids:
        if mutate:
            _append_step_id_to_step_list_elements(steps, inputs_offset=inputs_offset)
        else:
            steps = with_step_ids(steps, inputs_offset=inputs_offset)
    return steps


def _append_step_id_to_step_list_elements(steps: list, inputs_offset: int = 0):
    assert isinstance(steps, list)
    for i, step in enumerate(steps):
        if "id" not in step:
            step["id"] = i + inputs_offset
        assert step["id"] is not None


def _python_to_workflow(as_python, conversion_context):

    if "class" not in as_python:
        raise Exception("This is not a not a valid Galaxy workflow definition, must define a class.")

    if as_python["class"] != "GalaxyWorkflow":
        raise Exception("This is not a not a valid Galaxy workflow definition, 'class' must be 'GalaxyWorkflow'.")

    # .ga files don't have this, drop it so it isn't interpreted as a format 2 workflow.
    as_python.pop("class")

    _ensure_defaults(as_python, {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "Workflow",
        "uuid": str(uuid.uuid4()),
    })
    _populate_annotation(as_python)

    steps = steps_as_list(as_python, mutate=True)

    convert_inputs_to_steps(as_python, steps)

    if isinstance(steps, list):
        _append_step_id_to_step_list_elements(steps)
        steps_as_dict = OrderedDict()
        for i, step in enumerate(steps):
            steps_as_dict[str(i)] = step
            if "label" in step:
                label = step["label"]
                conversion_context.labels[label] = i

            # TODO: this really should be optional in Galaxy API.
            ensure_step_position(step, i)

        as_python["steps"] = steps_as_dict
        steps = steps_as_dict

    for step in steps.values():
        step_type = step.get("type", None)
        if "run" in step:
            if step_type is not None:
                raise Exception("Steps specified as run actions cannot specify a type.")
            run_action = step.get("run")
            run_action = conversion_context.get_runnable_description(run_action)
            if isinstance(run_action, dict):
                run_class = run_action["class"]
                run_to_step_function = eval(RUN_ACTIONS_TO_STEPS[run_class])

                run_to_step_function(conversion_context, step, run_action)
            else:
                step["content_id"] = run_action
                step["type"] = "subworkflow"
            del step["run"]

    for step in steps.values():
        step_type = step.get("type", "tool")
        step_type = STEP_TYPE_ALIASES.get(step_type, step_type)
        if step_type not in STEP_TYPES:
            raise Exception("Unknown step type encountered %s" % step_type)
        step["type"] = step_type
        eval("transform_%s" % step_type)(conversion_context, step)

    outputs = as_python.pop("outputs", [])
    outputs = convert_dict_to_id_list_if_needed(outputs)

    for output in outputs:
        assert isinstance(output, dict), "Output definition must be dictionary"
        assert "source" in output or "outputSource" in output, "Output definition must specify source"

        if "label" in output and "id" in output:
            raise Exception("label and id are aliases for outputs, may only define one")
        if "label" not in output and "id" not in output:
            label = ""

        raw_label = output.pop("label", None)
        raw_id = output.pop("id", None)
        label = raw_label or raw_id
        if Labels.is_anonymous_output_label(label):
            label = None
        source = clean_connection(output.get("outputSource"))
        if source is None and SUPPORT_LEGACY_CONNECTIONS:
            source = output.get("source").replace("#", "/", 1)
        id, output_name = conversion_context.step_output(source)
        step = steps[str(id)]
        workflow_output = {
            "output_name": output_name,
            "label": label,
            "uuid": output.get("uuid", None)
        }
        if "workflow_outputs" not in step:
            step["workflow_outputs"] = []
        step["workflow_outputs"].append(workflow_output)

    return as_python


def _preprocess_graphs(as_python, conversion_context):
    if not isinstance(as_python, dict):
        raise Exception("This is not a not a valid Galaxy workflow definition.")

    format_version = as_python.get("format-version", "v2.0")
    assert format_version == "v2.0"

    if "class" not in as_python and "$graph" in as_python:
        for subworkflow in as_python["$graph"]:
            if not isinstance(subworkflow, dict):
                raise Exception("Malformed workflow content in $graph")
            if "id" not in subworkflow:
                raise Exception("No subworkflow ID found for entry in $graph.")
            subworkflow_id = subworkflow["id"]
            if subworkflow_id == "main":
                as_python = subworkflow

            conversion_context.register_runnable(subworkflow)

    return as_python


def convert_inputs_to_steps(workflow_dict: dict, steps: list):
    """Convert workflow inputs to a steps in array - like in native Galaxy.

    workflow_dict is a Format 2 representation of a workflow and steps is a
    list of steps. This method will prepend all the inputs as as steps to the
    steps list. This method modifies both workflow_dict and steps.
    """
    if "inputs" not in workflow_dict:
        return

    input_steps = inputs_as_native_steps(workflow_dict)
    workflow_dict.pop("inputs")
    for i, new_step in enumerate(input_steps):
        steps.insert(i, new_step)


def run_workflow_to_step(conversion_context, step, run_action):
    step["type"] = "subworkflow"
    if conversion_context.import_options.deduplicate_subworkflows and _is_graph_id_reference(run_action):
        step["content_id"] = run_action
    else:
        subworkflow_conversion_context = conversion_context.get_subworkflow_conversion_context(step)
        step["subworkflow"] = _python_to_workflow(
            copy.deepcopy(run_action),
            subworkflow_conversion_context,
        )


def _is_graph_id_reference(run_action):
    return run_action and not isinstance(run_action, dict)


def transform_data_input(context, step):
    transform_input(context, step, default_name="Input dataset")


def transform_data_collection_input(context, step):
    transform_input(context, step, default_name="Input dataset collection")


def transform_parameter_input(context, step):
    transform_input(context, step, default_name="input_parameter")


def transform_input(context, step, default_name):
    default_name = step.get("label", default_name)
    _populate_annotation(step)
    _ensure_inputs_connections(step)

    if "inputs" not in step:
        step["inputs"] = [{}]

    step_inputs = step["inputs"][0]
    if "name" in step_inputs:
        name = step_inputs["name"]
    else:
        name = default_name

    _ensure_defaults(step_inputs, {
        "name": name,
        "description": "",
    })
    tool_state = {
        "name": name
    }
    for attrib in ["collection_type", "parameter_type", "optional", "default", "format", "restrictions", "restrictOnConnections", "suggestions"]:
        if attrib in step:
            tool_state[attrib] = step[attrib]

    _populate_tool_state(step, tool_state)


def transform_pause(context, step, default_name="Pause for dataset review"):
    default_name = step.get("label", default_name)
    _populate_annotation(step)

    _ensure_inputs_connections(step)

    if "inputs" not in step:
        step["inputs"] = [{}]

    step_inputs = step["inputs"][0]
    if "name" in step_inputs:
        name = step_inputs["name"]
    else:
        name = default_name

    _ensure_defaults(step_inputs, {
        "name": name,
    })
    tool_state = {
        "name": name
    }

    connect = _init_connect_dict(step)
    _populate_input_connections(context, step, connect)
    _populate_tool_state(step, tool_state)


def transform_subworkflow(context, step):
    _populate_annotation(step)

    _ensure_inputs_connections(step)

    tool_state = {
    }

    connect = _init_connect_dict(step)
    _populate_input_connections(context, step, connect)
    _populate_tool_state(step, tool_state)


def _runtime_value():
    return {"__class__": "RuntimeValue"}


def transform_tool(context, step):
    if "tool_id" not in step:
        raise Exception("Tool steps must define a tool_id.")

    _ensure_defaults(step, {
        "name": step['tool_id'],
        "post_job_actions": {},
        "tool_version": None,
    })
    post_job_actions = step["post_job_actions"]
    _populate_annotation(step)

    tool_state = {
        # TODO: Galaxy should not require tool state actually specify a __page__.
        "__page__": 0,
    }

    connect = _init_connect_dict(step)

    def append_link(key, value):
        if key not in connect:
            connect[key] = []
        assert "$link" in value
        link_value = value["$link"]
        connect[key].append(clean_connection(link_value))

    def replace_links(value, key=""):
        if _is_link(value):
            append_link(key, value)
            # Filled in by the connection, so to force late
            # validation of the field just mark as RuntimeValue.
            # It would be better I guess if this were some other
            # value dedicated to this purpose (e.g. a ficitious
            # {"__class__": "ConnectedValue"}) that could be further
            # validated by Galaxy.
            return _runtime_value()
        if isinstance(value, dict):
            new_values = {}
            for k, v in value.items():
                new_key = _join_prefix(key, k)
                new_values[k] = replace_links(v, new_key)
            return new_values
        elif isinstance(value, list):
            new_values = []
            for i, v in enumerate(value):
                # If we are a repeat we need to modify the key
                # but not if values are actually $links.
                if _is_link(v):
                    append_link(key, v)
                    new_values.append(None)
                else:
                    new_key = "%s_%d" % (key, i)
                    new_values.append(replace_links(v, new_key))
            return new_values
        else:
            return value

    # TODO: handle runtime inputs and state together.
    runtime_inputs = step.get("runtime_inputs", [])
    if "state" in step or runtime_inputs:
        step_state = step.pop("state", {})
        step_state = replace_links(step_state)

        for key, value in step_state.items():
            tool_state[key] = json.dumps(value)
        for runtime_input in runtime_inputs:
            tool_state[runtime_input] = json.dumps(_runtime_value())
    elif "tool_state" in step:
        tool_state.update(step.get("tool_state"))

    # Fill in input connections
    _populate_input_connections(context, step, connect)

    _populate_tool_state(step, tool_state)

    # Handle outputs.
    out = step.pop("out", None)
    if out is None:
        # Handle LEGACY 19.XX outputs key.
        out = step.pop("outputs", [])
    out = convert_dict_to_id_list_if_needed(out)
    for output in out:
        name = output["id"]
        for action_key, action_dict in POST_JOB_ACTIONS.items():
            action_argument = output.get(action_key, action_dict['default'])
            if action_argument:
                action_class = action_dict['action_class']
                action_name = action_class + name
                action = _action(
                    action_class,
                    name,
                    arguments=action_dict['arguments'](action_argument)
                )
                post_job_actions[action_name] = action


def run_tool_to_step(conversion_context, step, run_action):
    tool_description = conversion_context.galaxy_interface.import_tool(
        run_action
    )
    step["type"] = "tool"
    step["tool_id"] = tool_description["tool_id"]
    step["tool_version"] = tool_description["tool_version"]
    step["tool_hash"] = tool_description.get("tool_hash")
    step["tool_uuid"] = tool_description.get("uuid")


class BaseConversionContext(object):

    def __init__(self):
        self.labels = {}
        self.subworkflow_conversion_contexts = {}

    def step_id(self, label_or_id):
        if label_or_id in self.labels:
            id = self.labels[label_or_id]
        else:
            id = label_or_id
        return int(id)

    def step_output(self, value):
        value_parts = str(value).split("/")
        if len(value_parts) == 1:
            value_parts.append("output")
        id = self.step_id(value_parts[0])
        return id, value_parts[1]

    def get_subworkflow_conversion_context(self, step):
        # TODO: sometimes this method takes format2 steps and some times converted native ones
        # (for input connections) - redo this so the type signature is stronger.
        step_id = step.get("id")
        run_action = step.get("run")
        if self.import_options.deduplicate_subworkflows and _is_graph_id_reference(run_action):
            subworkflow_conversion_context = self.get_subworkflow_conversion_context_graph(run_action)
            return subworkflow_conversion_context
        if "content_id" in step:
            subworkflow_conversion_context = self.get_subworkflow_conversion_context_graph(step["content_id"])
            return subworkflow_conversion_context

        if step_id not in self.subworkflow_conversion_contexts:

            subworkflow_conversion_context = SubworkflowConversionContext(
                self
            )
            self.subworkflow_conversion_contexts[step_id] = subworkflow_conversion_context
        return self.subworkflow_conversion_contexts[step_id]

    def get_runnable_description(self, run_action):
        if "@import" in run_action:
            if len(run_action) > 1:
                raise Exception("@import must be only key if present.")

            run_action_path = run_action["@import"]
            runnable_path = os.path.join(self.workflow_directory, run_action_path)
            with open(runnable_path, "r") as f:
                runnable_description = ordered_load(f)
                run_action = runnable_description

        if not self.import_options.deduplicate_subworkflows and _is_graph_id_reference(run_action):
            run_action = self.graph_ids[run_action[1:]]

        return run_action


class ConversionContext(BaseConversionContext):

    def __init__(self, galaxy_interface, workflow_directory, import_options: Optional[ImportOptions] = None):
        super(ConversionContext, self).__init__()
        self.import_options = import_options or ImportOptions()
        self.graph_ids = OrderedDict()  # type: Dict
        self.graph_id_subworkflow_conversion_contexts = {}  # type: Dict
        self.workflow_directory = workflow_directory
        self.galaxy_interface = galaxy_interface

    def register_runnable(self, run_action):
        assert "id" in run_action
        self.graph_ids[run_action["id"]] = run_action

    def get_subworkflow_conversion_context_graph(self, graph_id):
        if graph_id not in self.graph_id_subworkflow_conversion_contexts:
            subworkflow_conversion_context = SubworkflowConversionContext(
                self
            )
            self.graph_id_subworkflow_conversion_contexts[graph_id] = subworkflow_conversion_context
        return self.graph_id_subworkflow_conversion_contexts[graph_id]


class SubworkflowConversionContext(BaseConversionContext):

    def __init__(self, parent_context):
        super(SubworkflowConversionContext, self).__init__()
        self.parent_context = parent_context

    @property
    def graph_ids(self):
        return self.parent_context.graph_ids

    @property
    def workflow_directory(self):
        return self.parent_context.workflow_directory

    @property
    def import_options(self):
        return self.parent_context.import_options

    @property
    def galaxy_interface(self):
        return self.parent_context.galaxy_interface

    def get_subworkflow_conversion_context_graph(self, graph_id):
        return self.parent_context.get_subworkflow_conversion_context_graph(graph_id)


def _action(type, name, arguments={}):
    return {
        "action_arguments": arguments,
        "action_type": type,
        "output_name": name,
    }


def _is_link(value):
    return isinstance(value, dict) and "$link" in value


def _join_prefix(prefix, key):
    if prefix:
        new_key = "%s|%s" % (prefix, key)
    else:
        new_key = key
    return new_key


def _init_connect_dict(step):
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
            if isinstance(value, dict) and 'source' in value:
                value = value["source"]
            elif isinstance(value, dict) and 'default' in value:
                continue
            elif isinstance(value, dict):
                raise KeyError('step input must define either source or default %s' % value)
            connect[key] = [value]
            connection_keys.add(key)

        for key in connection_keys:
            del step_in[key]

        if len(step_in) == 0:
            del step['in']

    return connect


def _populate_input_connections(context, step, connect):
    _ensure_inputs_connections(step)
    input_connections = step["input_connections"]
    is_subworkflow_step = step.get("type") == "subworkflow"

    for key, values in connect.items():
        input_connection_value = []
        if not isinstance(values, list):
            values = [values]
        for value in values:
            if not isinstance(value, dict):
                if key == "$step":
                    value += "/__NO_INPUT_OUTPUT_NAME__"
                id, output_name = context.step_output(value)
                value = {"id": id, "output_name": output_name}
                if is_subworkflow_step:
                    subworkflow_conversion_context = context.get_subworkflow_conversion_context(step)
                    input_subworkflow_step_id = subworkflow_conversion_context.step_id(key)
                    value["input_subworkflow_step_id"] = input_subworkflow_step_id
            input_connection_value.append(value)
        if key == "$step":
            key = "__NO_INPUT_OUTPUT_NAME__"
        input_connections[key] = input_connection_value


def _populate_annotation(step):
    if "annotation" not in step and "doc" in step:
        annotation = step.pop("doc")
        step["annotation"] = annotation
    elif "annotation" not in step:
        step["annotation"] = ""


def _ensure_inputs_connections(step):
    if "input_connections" not in step:
        step["input_connections"] = {}


def _ensure_defaults(in_dict, defaults):
    for key, value in defaults.items():
        if key not in in_dict:
            in_dict[key] = value


def _populate_tool_state(step, tool_state):
    step["tool_state"] = json.dumps(tool_state)


def main(argv=None):
    """Entry point for script to conversion from Format 2 interface."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)

    format2_path = args.input_path
    output_path = args.output_path or (format2_path + ".gxwf.yml")

    workflow_directory = os.path.abspath(format2_path)
    galaxy_interface = None

    with open(format2_path, "r") as f:
        has_workflow = ordered_load(f)

    output = python_to_workflow(has_workflow, galaxy_interface=galaxy_interface, workflow_directory=workflow_directory)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)


def _parser():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument('input_path', metavar='INPUT', type=str,
                        help='input workflow path (.ga)')
    parser.add_argument('output_path', metavar='OUTPUT', type=str, nargs="?",
                        help='output workflow path (.gxfw.yml)')
    return parser


if __name__ == "__main__":
    main(sys.argv)


__all__ = (
    'main',
    'python_to_workflow',
    'yaml_to_workflow',
)
