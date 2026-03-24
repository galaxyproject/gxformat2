"""Functionality for converting a standard Galaxy workflow into a format 2 workflow."""

import argparse
import json
import logging
import sys
from collections import OrderedDict
from typing import Any, Callable, Dict, Optional, Union

from pydantic import BaseModel as PydanticBaseModel

from ._labels import Labels, UNLABELED_INPUT_PREFIX, UNLABELED_STEP_PREFIX
from .model import (
    flatten_comment_data,
    native_input_to_format2_type,
)
from .native import load_native
from .schema.native import (
    NativeGalaxyWorkflow,
    NativeInputConnection,
    NativeStep,
    NativeWorkflowOutput,
)
from .yaml import ordered_dump

log = logging.getLogger(__name__)

ConvertToolStateFn = Optional[Callable[[dict], Optional[Dict[str, Any]]]]
"""Callback to convert a native tool step's tool_state to format2 state.

Accepts a native step dict (with tool_id, tool_version, tool_state).
Returns a format2 state dict, or None to fall back to default tool_state passthrough.
"""

SCRIPT_DESCRIPTION = """
Convert a native Galaxy workflow description into a Format 2 description.
"""

INPUT_STEP_TYPES = ("data_input", "data_collection_input", "parameter_input")


def _copy_common_properties(step: NativeStep, to_format2_step: dict, compact: bool = False) -> None:
    if step.annotation:
        to_format2_step["doc"] = step.annotation
    if not compact and step.position:
        to_format2_step["position"] = {"left": step.position.left, "top": step.position.top}
    if step.when:
        to_format2_step["when"] = step.when


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
        convert_tool_state=convert_tool_state,
    )
    result = to_format2(native_workflow_dict, options)
    data = result.model_dump(by_alias=True, exclude_none=True, mode="json")
    data["class"] = "GalaxyWorkflow"

    # Convert lists to dicts keyed by id/label for Format2 idmap representation
    _listify_to_idmap(data, "inputs")
    _listify_to_idmap(data, "outputs")
    _steps_to_idmap(data)
    _listify_to_idmap(data, "comments", key_field="label")

    # Convert step in/out from lists to dicts
    steps = data.get("steps", {})
    step_iter = steps.values() if isinstance(steps, dict) else steps
    for step in step_iter:
        if isinstance(step, dict):
            _listify_to_idmap(step, "in")
            _listify_to_idmap(step, "out")
            # Recurse into subworkflow run
            run = step.get("run")
            if isinstance(run, dict) and run.get("steps") is not None:
                _listify_to_idmap(run, "inputs")
                _listify_to_idmap(run, "outputs")
                _steps_to_idmap(run)
                _listify_to_idmap(run, "comments", key_field="label")

    if json_wrapper:
        return {"yaml_content": ordered_dump(data)}

    return data


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


def _convert_input_step(step: NativeStep, inputs: OrderedDict, compact: bool) -> None:
    step_id = step.label if step.label is not None else f"{UNLABELED_INPUT_PREFIX}{step.id}"
    input_dict: dict[str, Any] = {}
    tool_state = _tool_state(step)
    input_dict["type"] = native_input_to_format2_type({"type": step.type_}, tool_state)
    known_fields = [
        "collection_type",
        "optional",
        "format",
        "default",
        "restrictions",
        "suggestions",
        "restrictOnConnections",
        "fields",
        "column_definitions",
    ]
    for tool_state_key in known_fields:
        if tool_state_key in tool_state:
            input_dict[tool_state_key] = tool_state[tool_state_key]

    _copy_common_properties(step, input_dict, compact=compact)
    # If we are only copying property - use the CWL-style short-hand
    if len(input_dict) == 1:
        inputs[step_id] = input_dict["type"]
    else:
        inputs[step_id] = input_dict


def _convert_pause_step(step: NativeStep, label_map: dict, compact: bool) -> OrderedDict:
    step_dict: OrderedDict[str, Any] = OrderedDict()
    _copy_common_properties(step, step_dict, compact=compact)
    _copy_properties(step, step_dict, optional_props=["label"])
    _convert_input_connections(step, step_dict, label_map)
    step_dict["type"] = "pause"
    return step_dict


def _convert_pick_value_step(step: NativeStep, label_map: dict, compact: bool) -> OrderedDict:
    step_dict: OrderedDict[str, Any] = OrderedDict()
    _copy_common_properties(step, step_dict, compact=compact)
    _copy_properties(step, step_dict, optional_props=["label"])
    _convert_input_connections(step, step_dict, label_map)
    _convert_post_job_actions(step, step_dict)
    step_dict["type"] = "pick_value"
    tool_state = _tool_state(step)
    state: dict[str, Any] = {}
    if "mode" in tool_state:
        state["mode"] = tool_state["mode"]
    if state:
        step_dict["state"] = state
    return step_dict


def _convert_subworkflow_step(
    step: NativeStep,
    label_map: dict,
    compact: bool,
    tool_interface,
    convert_tool_state: ConvertToolStateFn,
) -> OrderedDict:
    step_dict: OrderedDict[str, Any] = OrderedDict()
    _copy_common_properties(step, step_dict, compact=compact)
    _copy_properties(step, step_dict, optional_props=["label"])
    _convert_input_connections(step, step_dict, label_map)
    _convert_post_job_actions(step, step_dict)
    content_source = getattr(step, "content_source", None)
    if content_source in ("url", "trs_url") and step.content_id:
        step_dict["run"] = step.content_id
    else:
        subworkflow = from_galaxy_native(
            step.subworkflow,
            tool_interface=tool_interface,
            json_wrapper=False,
            compact=compact,
            convert_tool_state=convert_tool_state,
        )
        step_dict["run"] = subworkflow
    return step_dict


def _convert_tool_step(
    step: NativeStep,
    label_map: dict,
    compact: bool,
    convert_tool_state: ConvertToolStateFn,
) -> OrderedDict:
    tool_representation = step.tool_representation
    if tool_representation and tool_representation.get("class") == "GalaxyUserTool":
        return _convert_user_defined_tool_step(step, tool_representation, label_map, compact)

    step_dict: OrderedDict[str, Any] = OrderedDict()
    _copy_properties(
        step, step_dict, optional_props=["label", "tool_shed_repository"], required_props=["tool_id", "tool_version"]
    )
    _copy_common_properties(step, step_dict, compact=compact)

    converted_state = None
    if convert_tool_state is not None:
        try:
            converted_state = convert_tool_state(step.model_dump(by_alias=True, exclude_none=True))
        except Exception:
            log.warning(
                "convert_tool_state callback failed for %s, falling back to default",
                step.tool_id,
                exc_info=True,
            )

    if converted_state is not None:
        step_dict["state"] = converted_state
    else:
        tool_state = _tool_state(step)
        tool_state.pop("__page__", None)
        tool_state.pop("__rerun_remap_job_id__", None)
        step_dict["tool_state"] = tool_state

    _convert_input_connections(step, step_dict, label_map)
    _convert_post_job_actions(step, step_dict)
    return step_dict


def _convert_user_defined_tool_step(
    step: NativeStep,
    tool_representation: dict[str, Any],
    label_map: dict,
    compact: bool,
) -> OrderedDict:
    step_dict: OrderedDict[str, Any] = OrderedDict()
    _copy_properties(step, step_dict, optional_props=["label"])
    _copy_common_properties(step, step_dict, compact=compact)
    step_dict["run"] = tool_representation
    _convert_input_connections(step, step_dict, label_map)
    _convert_post_job_actions(step, step_dict)
    return step_dict


def _convert_comments_to_format2(
    workflow: NativeGalaxyWorkflow,
    data: dict,
    label_map: dict,
    compact: bool,
) -> None:
    """Convert native comments to Format2 representation and add to data dict."""
    if not workflow.comments:
        return

    # Dump to dicts for flatten_comment_data which does dict manipulation
    native_comments = [c.model_dump(by_alias=True, exclude_none=True) for c in workflow.comments]

    comment_label_map: dict[int, str] = {}
    all_comments_labeled = True
    for i, native_comment in enumerate(native_comments):
        comment_label = native_comment.get("label")
        if comment_label:
            comment_label_map[i] = comment_label
        else:
            all_comments_labeled = False

    format2_comments = []
    for native_comment in native_comments:
        fmt2_comment = flatten_comment_data(native_comment)

        if compact:
            fmt2_comment.pop("position", None)
            fmt2_comment.pop("size", None)

        if fmt2_comment.get("type") == "frame":
            if "contains_steps" in fmt2_comment:
                fmt2_comment["contains_steps"] = [
                    label_map.get(str(idx)) or idx for idx in fmt2_comment["contains_steps"]
                ]
            if "contains_comments" in fmt2_comment:
                fmt2_comment["contains_comments"] = [
                    comment_label_map.get(idx, idx) for idx in fmt2_comment["contains_comments"]
                ]

        format2_comments.append(fmt2_comment)

    if all_comments_labeled:
        comments_dict = OrderedDict()
        for comment in format2_comments:
            label = comment.pop("label")
            comments_dict[label] = comment
        data["comments"] = comments_dict
    else:
        data["comments"] = format2_comments


def _tool_state(step: NativeStep) -> dict[str, Any]:
    tool_state = step.tool_state
    if isinstance(tool_state, str):
        return json.loads(tool_state)
    return tool_state if tool_state is not None else {}


def _copy_properties(
    step: NativeStep,
    to_format2_step: dict,
    optional_props: list[str] | None = None,
    required_props: list[str] | None = None,
) -> None:
    for prop in optional_props or []:
        value = getattr(step, prop, None)
        if value:
            if isinstance(value, PydanticBaseModel):
                value = value.model_dump(by_alias=True, exclude_none=True)
            to_format2_step[prop] = value
    for prop in required_props or []:
        value = getattr(step, prop, None)
        if isinstance(value, PydanticBaseModel):
            value = value.model_dump(by_alias=True, exclude_none=True)
        to_format2_step[prop] = value


def _convert_input_connections(step: NativeStep, to_format2_step: dict, label_map: dict) -> None:
    in_dict: dict[str, Any] = dict(step.in_) if step.in_ else {}
    input_connections = step.input_connections or {}
    for input_name, input_defs in input_connections.items():
        if not isinstance(input_defs, list):
            input_defs = [input_defs]
        for input_def in input_defs:
            source = _to_source(input_def, label_map)
            if input_name == "__NO_INPUT_OUTPUT_NAME__":
                input_name = "$step"
                assert source.endswith("/__NO_INPUT_OUTPUT_NAME__")
                source = source[: -len("/__NO_INPUT_OUTPUT_NAME__")]
            if input_name in in_dict:
                existing_source = in_dict[input_name]["source"]
                if not isinstance(existing_source, list):
                    existing_source = [existing_source]
                existing_source.append(source)
                in_dict[input_name]["source"] = existing_source
            else:
                in_dict[input_name] = {"source": source}
    to_format2_step["in"] = in_dict


def _convert_post_job_actions(step: NativeStep, to_format2_step: dict) -> None:

    def _ensure_output_def(key):
        if "outputs" in to_format2_step:
            to_format2_step["out"] = to_format2_step.pop("outputs")
        elif "out" not in to_format2_step:
            to_format2_step["out"] = {}

        outputs_dict = to_format2_step["out"]
        if key not in outputs_dict:
            outputs_dict[key] = {}
        return outputs_dict[key]

    if not step.post_job_actions:
        return

    remaining: dict[str, Any] = {}
    for pja_key, pja in step.post_job_actions.items():
        action_type = pja.action_type
        output_name = pja.output_name
        action_args = pja.action_arguments or {}

        handled = True
        if action_type == "RenameDatasetAction":
            output_dict = _ensure_output_def(output_name)
            output_dict["rename"] = action_args["newname"]
        elif action_type == "HideDatasetAction":
            output_dict = _ensure_output_def(output_name)
            output_dict["hide"] = True
        elif action_type == "DeleteIntermediatesAction":
            output_dict = _ensure_output_def(output_name)
            output_dict["delete_intermediate_datasets"] = True
        elif action_type == "ChangeDatatypeAction":
            output_dict = _ensure_output_def(output_name)
            output_dict["change_datatype"] = action_args["newtype"]
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

        if not handled:
            remaining[pja_key] = pja.model_dump(by_alias=True, exclude_none=True)

    if remaining:
        to_format2_step["post_job_actions"] = remaining


def _to_source(
    has_output_name: Union[NativeWorkflowOutput, NativeInputConnection],
    label_map: dict,
    output_id: int | None = None,
) -> str:
    if output_id is None:
        assert isinstance(has_output_name, NativeInputConnection)
        output_id = has_output_name.id
    output_id_str = str(output_id)
    output_name = has_output_name.output_name
    output_label = label_map.get(output_id_str) or output_id_str
    if output_name == "output":
        return output_label
    return f"{output_label}/{output_name}"


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
