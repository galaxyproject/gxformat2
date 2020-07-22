"""Abstractions for uniform across formats."""
from gxformat2._scripts import ensure_format2
from gxformat2._yaml import ordered_load
from gxformat2.converter import convert_inputs_to_steps, steps_as_list


def steps_normalized(workflow_dict=None, workflow_path=None):
    """Walk over a normalized step rep. across workflow formats."""
    if workflow_path is not None:
        assert workflow_dict is None
        with open(workflow_path, "r") as f:
            workflow_dict = ordered_load(f)
        return steps_normalized(workflow_dict=workflow_dict)

    workflow_dict = ensure_format2(workflow_dict)
    steps = steps_as_list(workflow_dict)
    convert_inputs_to_steps(workflow_dict, steps)
    return steps
