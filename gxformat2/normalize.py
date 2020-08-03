"""Abstractions for uniform across formats."""
from typing import Union

from gxformat2._scripts import ensure_format2
from gxformat2._yaml import ordered_load
from gxformat2.converter import _outputs_as_list, convert_inputs_to_steps, steps_as_list

NON_INPUT_TYPES = ["tool", "subworkflow", "pause"]


def steps_normalized(workflow_dict=None, workflow_path=None):
    """Walk over a normalized step rep. across workflow formats."""
    workflow_dict = _ensure_format2(workflow_dict=workflow_dict, workflow_path=workflow_path)
    steps = steps_as_list(workflow_dict)
    convert_inputs_to_steps(workflow_dict, steps)
    return steps


def inputs_normalized(**kwd):
    """Call steps_normalized and retain just the input steps normalized."""
    steps = steps_normalized(**kwd)
    input_steps = []
    for step in steps:
        step_type = step.get("type") or 'tool'
        if step_type in NON_INPUT_TYPES:
            continue

        input_steps.append(step)

    return input_steps


def outputs_normalized(**kwd):
    """Ensure Format2 and return outputs.

    Probably should go farther and normalize source -> outputSource,
    but doesn't yet do this.
    """
    workflow_dict = _ensure_format2(**kwd)
    return _outputs_as_list(workflow_dict)


def walk_id_list_or_dict(dict_or_list: Union[dict, list]):
    """Walk over idmap regardless of list or dict representation."""
    if isinstance(dict_or_list, list):
        for item in dict_or_list:
            yield item["id"], item
    else:
        for item in dict_or_list.items():
            yield item


def ensure_implicit_step_outs(workflow_dict: dict):
    """Ensure implicit 'out' dicts allowed by format2 are filled in for CWL."""
    outputs_by_label = {}

    def register_step_output(step_label, output_name):
        if step_label not in outputs_by_label:
            outputs_by_label[step_label] = set()
        outputs_by_label[step_label].add(output_name)

    def register_output_source(output_source):
        if "/" in output_source:
            step, output_name = output_source.split("/", 1)
            register_step_output(step, output_name)

    for output_name, output in walk_id_list_or_dict(workflow_dict.get("outputs", {})):
        if "outputSource" in output:
            output_source = output["outputSource"]
            if "/" in output_source:
                step, output_name = output_source.split("/", 1)
                register_step_output(step, output_name)

    for step in steps_as_list(workflow_dict):
        step_in = step.get("in", {})
        for step_in_name, step_in_def in step_in.items():
            register_output_source(step_in_def)

    for step in steps_as_list(workflow_dict):
        label = step["label"]
        if "out" not in step:
            step["out"] = []
        for out in outputs_by_label.get(label, []):
            step_out = step["out"]
            if isinstance(step_out, list):
                if out not in step_out:
                    step_out.append(out)
            else:
                step_out[out] = {}


def _ensure_format2(workflow_dict=None, workflow_path=None):
    if workflow_path is not None:
        assert workflow_dict is None
        with open(workflow_path, "r") as f:
            workflow_dict = ordered_load(f)

    workflow_dict = ensure_format2(workflow_dict)
    return workflow_dict
