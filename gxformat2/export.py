"""Functionality for converting a standard Galaxy workflow into a format 2 workflow.

This module provides backward-compatible wrapper functions that delegate
to :mod:`gxformat2.to_format2` and return plain dicts.  The new typed API
is :func:`gxformat2.to_format2.to_format2`.
"""

import argparse
import json
import sys
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional, Union

from .schema.native import NativeGalaxyWorkflow
from .yaml import ordered_dump

log = __import__("logging").getLogger(__name__)

ConvertToolStateFn = Optional[Callable[[dict], Optional[Dict[str, Any]]]]
"""Callback to convert a native tool step's tool_state to format2 state.

Accepts a native step dict (with tool_id, tool_version, tool_state).
Returns a format2 state dict, or None to fall back to default tool_state passthrough.
"""

SCRIPT_DESCRIPTION = """
Convert a native Galaxy workflow description into a Format 2 description.
"""


def from_galaxy_native(
    native_workflow_dict: Union[dict[str, Any], NativeGalaxyWorkflow],
    tool_interface=None,
    json_wrapper: bool = False,
    compact: bool = False,
    convert_tool_state: ConvertToolStateFn = None,
):
    """Convert native .ga workflow definition to a format2 workflow.

    If ``convert_tool_state`` is provided it should be a callable accepting a
    native step dict and returning an optional dict representing the format2
    ``state`` for that step.  When the callable returns a dict, the step will
    carry ``state`` instead of ``tool_state``; when it returns ``None`` the
    default ``tool_state`` passthrough is used.
    """
    from .options import ConversionOptions
    from .to_format2 import to_format2

    options = ConversionOptions(
        compact=compact,
        state_encode_to_format2=convert_tool_state,
    )
    result = to_format2(native_workflow_dict, options)
    data = result.to_dict()
    data["class"] = "GalaxyWorkflow"

    # Strip empty optional collections that the old code omitted
    for key in ("comments", "tags"):
        if key in data and data[key] == []:
            del data[key]

    # Convert lists to dicts keyed by id/label for Format2 idmap representation
    _listify_to_idmap(data, "inputs")
    _listify_to_idmap(data, "outputs")
    _steps_to_idmap(data)
    _listify_to_idmap(data, "comments", key_field="label")

    # Convert step in/out from lists to dicts, fix up subworkflow runs
    steps = data.get("steps", {})
    step_iter = steps.values() if isinstance(steps, dict) else steps
    for step in step_iter:
        if isinstance(step, dict):
            _listify_to_idmap(step, "in")
            _listify_to_idmap(step, "out")
            # Recurse into subworkflow run
            run = step.get("run")
            if isinstance(run, dict) and run.get("steps") is not None:
                _fixup_format2_dict(run)

    if json_wrapper:
        return {"yaml_content": ordered_dump(data)}

    return data


def _fixup_format2_dict(data: dict) -> None:
    """Recursively fix up a Format2 workflow dict for backward compat."""
    data["class"] = "GalaxyWorkflow"
    for key in ("comments", "tags"):
        if key in data and data[key] == []:
            del data[key]
    _listify_to_idmap(data, "inputs")
    _listify_to_idmap(data, "outputs")
    _steps_to_idmap(data)
    _listify_to_idmap(data, "comments", key_field="label")
    steps = data.get("steps", {})
    step_iter = steps.values() if isinstance(steps, dict) else steps
    for step in step_iter:
        if isinstance(step, dict):
            _listify_to_idmap(step, "in")
            _listify_to_idmap(step, "out")
            run = step.get("run")
            if isinstance(run, dict) and run.get("steps") is not None:
                _fixup_format2_dict(run)


def _listify_to_idmap(data: dict, key: str, key_field: str = "id") -> None:
    """Convert a list of dicts to a dict keyed by id/label, if all items have the key."""
    items = data.get(key)
    if not isinstance(items, list) or not items:
        return
    if not all(isinstance(item, dict) and item.get(key_field) for item in items):
        return
    result = OrderedDict()
    for item in items:
        item_key = item.pop(key_field)
        result[item_key] = item
    data[key] = result


def _steps_to_idmap(data: dict) -> None:
    """Convert steps list to dict keyed by label if all steps are labeled."""
    steps = data.get("steps")
    if not isinstance(steps, list) or not steps:
        return
    if not all(isinstance(s, dict) and s.get("label") for s in steps):
        return
    result = OrderedDict()
    for step in steps:
        label = step.pop("label")
        result[label] = step
    data["steps"] = result


def main(argv=None):
    """Entry point for script to convert native workflows to Format 2."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)

    format2_path = args.input_path
    output_path = args.output_path or (format2_path + ".gxwf.yml")
    with open(format2_path) as f:
        native_workflow_dict = json.load(f)

    as_dict = from_galaxy_native(native_workflow_dict, compact=args.compact)
    with open(output_path, "w") as f:
        ordered_dump(as_dict, f)


def _parser():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("input_path", metavar="INPUT", type=str, help="input workflow path (.ga)")
    parser.add_argument("output_path", metavar="OUTPUT", type=str, nargs="?", help="output workflow path (.gxfw.yml)")
    parser.add_argument("--compact", action="store_true", help="Generate compact workflow without position information")
    return parser


__all__ = (
    "from_galaxy_native",
    "main",
)
