"""Utilities for scripts in gxformat2."""

from gxformat2.to_format2 import ensure_format2 as _ensure_format2
from gxformat2.yaml import ordered_load_path


def ensure_format2_from_path(path: str):
    """Load a file from the specified path and ensure it is in format2."""
    return ensure_format2(ordered_load_path(path))


def ensure_format2(workflow_dict: dict, ensure_labels: bool = False):
    """Consume a dictionary and ensure the result is format2.

    So convert from ga if needed.
    """
    # keep return shape as raw dict for script compatibility
    return _ensure_format2(workflow_dict).to_dict()
