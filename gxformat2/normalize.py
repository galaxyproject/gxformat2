"""Abstractions for uniform across formats."""
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


def _ensure_format2(workflow_dict=None, workflow_path=None):
    if workflow_path is not None:
        assert workflow_dict is None
        with open(workflow_path, "r") as f:
            workflow_dict = ordered_load(f)

    workflow_dict = ensure_format2(workflow_dict)
    return workflow_dict
