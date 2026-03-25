"""Functionality for converting a Format 2 workflow into a standard Galaxy workflow.

This module provides backward-compatible wrapper functions that delegate
to :mod:`gxformat2.to_native` and return plain dicts.  The new typed API
is :func:`gxformat2.to_native.to_native`.
"""

import argparse
import json
import os
import sys
from typing import Any, Callable, Dict, Optional

from .model import steps_as_list  # noqa: F401 (re-exported for abstract.py, normalize.py)
from .to_native import POST_JOB_ACTIONS  # noqa: F401 (re-exported for tests)
from .yaml import ordered_load

log = __import__("logging").getLogger(__name__)

NativeStateEncoderFn = Optional[Callable[[dict, Dict[str, Any]], Optional[Dict[str, Any]]]]
"""Callback to encode format2 state back to native tool_state.

Accepts (step, state) where step is the partially-built native step dict
and state is the format2 state dict after setup_connected_values processing.
Returns {param_name: encoded_value} for native tool_state, or None to fall
back to default json.dumps encoding.
"""

SCRIPT_DESCRIPTION = """
Convert a Format 2 Galaxy workflow description into a native format.
"""


class ImportOptions:

    def __init__(self):
        self.deduplicate_subworkflows = False
        self.encode_tool_state_json = True
        self.state_encode_to_native: NativeStateEncoderFn = None


def yaml_to_workflow(has_yaml, galaxy_interface=None, workflow_directory=None, import_options=None):
    """Convert a Format 2 workflow into standard Galaxy format from supplied stream."""
    as_python = ordered_load(has_yaml)
    return python_to_workflow(
        as_python,
        galaxy_interface=galaxy_interface,
        workflow_directory=workflow_directory,
        import_options=import_options,
    )


def python_to_workflow(as_python, galaxy_interface=None, workflow_directory=None, import_options=None):
    """Convert a Format 2 workflow into standard Galaxy format from supplied dictionary."""
    from .options import ConversionOptions
    from .to_native import to_native

    if "yaml_content" in as_python:
        as_python = ordered_load(as_python["yaml_content"])

    if workflow_directory is None:
        workflow_directory = os.path.abspath(".")

    import_options = import_options or ImportOptions()

    options = ConversionOptions(
        workflow_directory=workflow_directory,
        deduplicate_subworkflows=import_options.deduplicate_subworkflows,
        state_encode_to_native=import_options.state_encode_to_native,
    )
    result = to_native(as_python, options)
    data = result.model_dump(by_alias=True, exclude_none=True, mode="json")
    _compat_fixup_native(data, import_options)
    return data


def _compat_fixup_native(data: dict, import_options: ImportOptions) -> None:
    """Post-process native dict for backward compat with old converter output."""
    for step in data.get("steps", {}).values():
        # JSON-encode tool_state if requested
        if import_options.encode_tool_state_json and isinstance(step.get("tool_state"), dict):
            step["tool_state"] = json.dumps(step["tool_state"])
        # Ensure label key exists (old converter always set it)
        if "label" not in step:
            step["label"] = None
        # Wrap single input_connections in lists (old converter always used lists)
        ic = step.get("input_connections", {})
        for key, value in ic.items():
            if isinstance(value, dict):
                ic[key] = [value]
        # Recurse into subworkflows
        if isinstance(step.get("subworkflow"), dict):
            _compat_fixup_native(step["subworkflow"], import_options)


def main(argv=None):
    """Entry point for script to conversion from Format 2 interface."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)

    format2_path = args.input_path
    output_path = args.output_path or (format2_path + ".gxwf.yml")

    workflow_directory = os.path.abspath(format2_path)

    with open(format2_path) as f:
        has_workflow = ordered_load(f)

    output = python_to_workflow(has_workflow, workflow_directory=workflow_directory)
    with open(output_path, "w") as f:
        json.dump(output, f, indent=4)


def _parser():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("input_path", metavar="INPUT", type=str, help="input workflow path (.gxwf.yml)")
    parser.add_argument("output_path", metavar="OUTPUT", type=str, nargs="?", help="output workflow path (.ga)")
    return parser


if __name__ == "__main__":
    main(sys.argv)


__all__ = (
    "main",
    "python_to_workflow",
    "yaml_to_workflow",
)
