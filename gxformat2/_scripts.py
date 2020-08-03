"""Utilities for scripts in gxformat2."""
from gxformat2.export import from_galaxy_native


def ensure_format2(workflow_dict: dict):
    """Consume a dictionary and ensure the result is format2.

    So convert from ga if needed.
    """
    if workflow_dict.get("a_galaxy_workflow") == "true":
        workflow_dict = from_galaxy_native(workflow_dict)
    return workflow_dict
