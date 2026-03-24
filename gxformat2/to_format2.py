"""Convert native Galaxy workflows to Format2 using typed models.

This module provides :func:`to_format2` which accepts any native workflow
representation and returns a :class:`NormalizedFormat2` (or
:class:`ExpandedFormat2` when ``expand=True``).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Literal, overload

from ._labels import Labels, UNLABELED_INPUT_PREFIX, UNLABELED_STEP_PREFIX
from .model import (
    flatten_comment_data,
    native_input_to_format2_type,
)
from .normalized._expanded import (
    expanded_format2,
    ExpandedFormat2,
)
from .normalized._format2 import (
    NormalizedFormat2,
    NormalizedWorkflowStep,
)
from .normalized._native import (
    normalized_native,
    NormalizedNativeStep,
    NormalizedNativeWorkflow,
)
from .options import ConversionOptions
from .schema.gxformat2 import (
    Report,
    StepPosition as Format2StepPosition,
    ToolShedRepository as Format2ToolShedRepository,
    WorkflowComment,
    WorkflowInputParameter,
    WorkflowOutputParameter,
    WorkflowStepInput,
    WorkflowStepOutput,
    WorkflowStepType,
)
from .schema.native import NativeGalaxyWorkflow, StepPosition as NativeStepPosition

log = logging.getLogger(__name__)

INPUT_STEP_TYPES = ("data_input", "data_collection_input", "parameter_input")


def _convert_position(position: NativeStepPosition | None) -> Format2StepPosition | None:
    if position is None:
        return None
    return Format2StepPosition(left=position.left, top=position.top)


def _convert_tool_shed_repo(repo) -> Format2ToolShedRepository | None:
    if repo is None:
        return None
    return Format2ToolShedRepository(
        name=repo.name, changeset_revision=repo.changeset_revision,
        owner=repo.owner, tool_shed=repo.tool_shed,
    )


@overload
def to_format2(
    workflow: dict[str, Any] | str | Path | NativeGalaxyWorkflow | NormalizedNativeWorkflow,
    options: ConversionOptions,
    expand: Literal[True],
) -> ExpandedFormat2: ...


@overload
def to_format2(
    workflow: dict[str, Any] | str | Path | NativeGalaxyWorkflow | NormalizedNativeWorkflow,
    options: ConversionOptions | None = None,
    expand: Literal[False] = False,
) -> NormalizedFormat2: ...


def to_format2(
    workflow: dict[str, Any] | str | Path | NativeGalaxyWorkflow | NormalizedNativeWorkflow,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> NormalizedFormat2 | ExpandedFormat2:
    """Convert a native Galaxy workflow to Format2.

    Returns :class:`NormalizedFormat2` by default, or
    :class:`ExpandedFormat2` when ``expand=True``.
    """
    options = options or ConversionOptions()
    if not isinstance(workflow, NormalizedNativeWorkflow):
        workflow = normalized_native(workflow)

    result = _build_format2_workflow(workflow, options)

    if expand:
        return expanded_format2(result, options)
    return result


def _build_format2_workflow(
    wf: NormalizedNativeWorkflow,
    options: ConversionOptions,
) -> NormalizedFormat2:
    compact = options.compact

    # Build label map for source references
    label_map: dict[str, str] = {}
    for key, step in wf.steps.items():
        if step.label is not None:
            label_map[str(key)] = step.label
        elif step.type_ in INPUT_STEP_TYPES:
            label_map[str(key)] = f"{UNLABELED_INPUT_PREFIX}{step.id}"
        else:
            label_map[str(key)] = f"{UNLABELED_STEP_PREFIX}{step.id}"

    # Separate inputs from non-input steps
    input_params: list[WorkflowInputParameter] = []
    fmt2_steps: list[NormalizedWorkflowStep] = []
    labels = Labels()

    # Build workflow outputs from step workflow_outputs
    output_params: list[WorkflowOutputParameter] = []
    for step in wf.steps.values():
        for workflow_output in step.workflow_outputs:
            source = _to_source(workflow_output.output_name, label_map, step.id)
            output_id = labels.ensure_new_output_label(workflow_output.label)
            output_params.append(WorkflowOutputParameter(
                id=output_id,
                outputSource=source,
            ))

    for step in wf.steps.values():
        if step.type_ in INPUT_STEP_TYPES:
            input_params.append(_build_input_param(step))
        else:
            fmt2_steps.append(_build_format2_step(step, label_map, options))

    # Convert comments
    comments = _build_format2_comments(wf, label_map, compact)

    return NormalizedFormat2(
        label=wf.name,
        doc=wf.annotation or None,
        inputs=input_params,
        outputs=output_params,
        steps=fmt2_steps,
        comments=comments,
        report=Report(markdown=wf.report.markdown) if wf.report else None,
        tags=wf.tags,
        creator=[c.model_dump(by_alias=True, exclude_none=True) for c in wf.creator] if wf.creator else None,
        license=wf.license,
        release=wf.release,
        uuid=wf.uuid,
    )


def _build_input_param(step: NormalizedNativeStep) -> WorkflowInputParameter:
    step_id = step.label if step.label is not None else f"{UNLABELED_INPUT_PREFIX}{step.id}"
    tool_state = step.tool_state
    input_type = native_input_to_format2_type({"type": step.type_}, tool_state)

    kwargs: dict[str, Any] = {"id": step_id, "type_": input_type}

    for key in ("collection_type", "optional", "format", "default", "restrictions",
                "suggestions", "restrictOnConnections", "fields", "column_definitions"):
        if key in tool_state:
            if key == "format":
                fmt = tool_state[key]
                kwargs["format"] = [fmt] if isinstance(fmt, str) else fmt
            else:
                kwargs[key] = tool_state[key]

    if step.annotation:
        kwargs["doc"] = step.annotation
    if step.position:
        kwargs["position"] = _convert_position(step.position)

    return WorkflowInputParameter(**kwargs)


def _build_format2_step(
    step: NormalizedNativeStep,
    label_map: dict[str, str],
    options: ConversionOptions,
) -> NormalizedWorkflowStep:
    compact = options.compact
    module_type = step.type_

    if module_type == "tool":
        return _build_tool_format2_step(step, label_map, options)
    elif module_type == "subworkflow":
        return _build_subworkflow_format2_step(step, label_map, options)
    elif module_type == "pause":
        return _build_pause_format2_step(step, label_map, compact)
    elif module_type == "pick_value":
        return _build_pick_value_format2_step(step, label_map, compact, options)
    else:
        raise NotImplementedError(f"Unhandled module type {module_type}")


def _build_tool_format2_step(
    step: NormalizedNativeStep,
    label_map: dict[str, str],
    options: ConversionOptions,
) -> NormalizedWorkflowStep:
    # User-defined tool
    if step.tool_representation and step.tool_representation.get("class") == "GalaxyUserTool":
        return _build_user_tool_format2_step(step, label_map, options.compact)

    in_list = _build_step_inputs(step, label_map)
    out_list = _build_step_outputs(step)

    # Handle tool state
    state: dict[str, Any] | None = None
    tool_state: str | dict[str, Any] | None = None

    converted_state = None
    if options.convert_tool_state is not None:
        try:
            step_dict = step.model_dump(by_alias=True, exclude_none=True)
            converted_state = options.convert_tool_state(step_dict)
        except Exception:
            log.warning("convert_tool_state failed for %s, falling back", step.tool_id, exc_info=True)

    if converted_state is not None:
        state = converted_state
    else:
        ts = dict(step.tool_state)
        ts.pop("__page__", None)
        ts.pop("__rerun_remap_job_id__", None)
        tool_state = ts

    label = step.label or label_map.get(str(step.id))
    if label and Labels.is_unlabeled(label):
        label = None

    return NormalizedWorkflowStep(
        id=label or str(step.id),
        label=label,
        doc=step.annotation or None,
        tool_id=step.tool_id,
        tool_version=step.tool_version,
        tool_shed_repository=_convert_tool_shed_repo(step.tool_shed_repository),
        state=state,
        tool_state=tool_state,
        in_=in_list,
        out=out_list,
        position=_convert_position(step.position) if not options.compact else None,
        when=step.when,
        uuid=step.uuid,
        errors=step.errors,
    )


def _build_user_tool_format2_step(
    step: NormalizedNativeStep,
    label_map: dict[str, str],
    compact: bool,
) -> NormalizedWorkflowStep:
    in_list = _build_step_inputs(step, label_map)
    out_list = _build_step_outputs(step)
    label = step.label or label_map.get(str(step.id))

    return NormalizedWorkflowStep(
        id=label or str(step.id),
        label=label,
        doc=step.annotation or None,
        run=step.tool_representation,
        in_=in_list,
        out=out_list,
        position=_convert_position(step.position) if not compact else None,
    )


def _build_subworkflow_format2_step(
    step: NormalizedNativeStep,
    label_map: dict[str, str],
    options: ConversionOptions,
) -> NormalizedWorkflowStep:
    in_list = _build_step_inputs(step, label_map)
    out_list = _build_step_outputs(step)

    run: NormalizedFormat2 | str | None = None
    content_source = step.content_source
    if content_source in ("url", "trs_url") and step.content_id:
        run = step.content_id
    elif step.subworkflow is not None:
        run = _build_format2_workflow(step.subworkflow, options)
    elif step.content_id:
        run = step.content_id

    label = step.label or label_map.get(str(step.id))
    if label and Labels.is_unlabeled(label):
        label = None

    return NormalizedWorkflowStep(
        id=label or str(step.id),
        label=label,
        doc=step.annotation or None,
        run=run,
        in_=in_list,
        out=out_list,
        position=_convert_position(step.position) if not options.compact else None,
        when=step.when,
        uuid=step.uuid,
    )


def _build_pause_format2_step(
    step: NormalizedNativeStep,
    label_map: dict[str, str],
    compact: bool,
) -> NormalizedWorkflowStep:
    in_list = _build_step_inputs(step, label_map)
    label = step.label or label_map.get(str(step.id))
    if label and Labels.is_unlabeled(label):
        label = None

    return NormalizedWorkflowStep(
        id=label or str(step.id),
        label=label,
        doc=step.annotation or None,
        type_=WorkflowStepType.pause,
        in_=in_list,
        position=_convert_position(step.position) if not compact else None,
    )


def _build_pick_value_format2_step(
    step: NormalizedNativeStep,
    label_map: dict[str, str],
    compact: bool,
    options: ConversionOptions,
) -> NormalizedWorkflowStep:
    in_list = _build_step_inputs(step, label_map)
    out_list = _build_step_outputs(step)

    state: dict[str, Any] | None = None
    tool_state = step.tool_state
    if "mode" in tool_state:
        state = {"mode": tool_state["mode"]}

    label = step.label or label_map.get(str(step.id))
    if label and Labels.is_unlabeled(label):
        label = None

    return NormalizedWorkflowStep(
        id=label or str(step.id),
        label=label,
        doc=step.annotation or None,
        type_=WorkflowStepType.pick_value,
        state=state,
        in_=in_list,
        out=out_list,
        position=_convert_position(step.position) if not compact else None,
    )


# --- Shared helpers ---


def _build_step_inputs(
    step: NormalizedNativeStep,
    label_map: dict[str, str],
) -> list[WorkflowStepInput]:
    """Convert native input_connections to Format2 step inputs."""
    in_list: list[WorkflowStepInput] = []
    # Preserve existing 'in' defaults
    defaults: dict[str, Any] = {}
    if step.in_:
        for key, value in step.in_.items():
            if isinstance(value, dict) and "default" in value:
                defaults[key] = value["default"]

    for input_name, input_defs in step.input_connections.items():
        if not isinstance(input_defs, list):
            input_defs = [input_defs]
        sources: list[str] = []
        for input_def in input_defs:
            source = _to_source(input_def.output_name, label_map, input_def.id)
            sources.append(source)

        actual_name = "$step" if input_name == "__NO_INPUT_OUTPUT_NAME__" else input_name
        if actual_name == "$step" and sources:
            # Strip /__NO_INPUT_OUTPUT_NAME__ suffix
            sources = [s.rsplit("/__NO_INPUT_OUTPUT_NAME__", 1)[0] if "/__NO_INPUT_OUTPUT_NAME__" in s else s for s in sources]

        source_val: str | list[str] = sources[0] if len(sources) == 1 else sources
        default = defaults.pop(actual_name, None)
        in_list.append(WorkflowStepInput(
            id=actual_name,
            source=source_val,
            default=default,
        ))

    # Add remaining defaults without connections
    for key, default in defaults.items():
        in_list.append(WorkflowStepInput(id=key, default=default))

    return in_list


def _build_step_outputs(step: NormalizedNativeStep) -> list[WorkflowStepOutput]:
    """Convert native post_job_actions to Format2 step outputs."""
    if not step.post_job_actions:
        return []

    outputs_by_name: dict[str, dict[str, Any]] = {}
    remaining_pjas: dict[str, Any] = {}

    for pja_key, pja in step.post_job_actions.items():
        action_type = pja.action_type
        output_name = pja.output_name
        action_args = pja.action_arguments or {}

        if output_name not in outputs_by_name:
            outputs_by_name[output_name] = {}
        output_dict = outputs_by_name[output_name]

        handled = True
        if action_type == "RenameDatasetAction":
            output_dict["rename"] = action_args["newname"]
        elif action_type == "HideDatasetAction":
            output_dict["hide"] = True
        elif action_type == "DeleteIntermediatesAction":
            output_dict["delete_intermediate_datasets"] = True
        elif action_type == "ChangeDatatypeAction":
            output_dict["change_datatype"] = action_args["newtype"]
        elif action_type == "TagDatasetAction":
            output_dict["add_tags"] = action_args["tags"].split(",")
        elif action_type == "RemoveTagDatasetAction":
            output_dict["remove_tags"] = action_args["tags"].split(",")
        elif action_type == "ColumnSetAction":
            output_dict["set_columns"] = action_args
        else:
            handled = False

        if not handled:
            remaining_pjas[pja_key] = pja.model_dump(by_alias=True, exclude_none=True)

    result: list[WorkflowStepOutput] = []
    for name, props in outputs_by_name.items():
        result.append(WorkflowStepOutput(id=name, **props))

    return result


def _to_source(output_name: str, label_map: dict[str, str], step_id: int) -> str:
    output_label = label_map.get(str(step_id)) or str(step_id)
    if output_name == "output":
        return output_label
    return f"{output_label}/{output_name}"


def _build_format2_comments(
    wf: NormalizedNativeWorkflow,
    label_map: dict[str, str],
    compact: bool,
) -> list[WorkflowComment]:
    if not wf.comments:
        return []

    native_comments = [c.model_dump(by_alias=True, exclude_none=True) for c in wf.comments]

    comment_label_map: dict[int, str] = {}
    for i, native_comment in enumerate(native_comments):
        label = native_comment.get("label")
        if label:
            comment_label_map[i] = label

    result: list[WorkflowComment] = []
    for native_comment in native_comments:
        fmt2_dict = flatten_comment_data(native_comment)

        if compact:
            fmt2_dict.pop("position", None)
            fmt2_dict.pop("size", None)

        if fmt2_dict.get("type") == "frame":
            if "contains_steps" in fmt2_dict:
                fmt2_dict["contains_steps"] = [
                    label_map.get(str(idx)) or idx for idx in fmt2_dict["contains_steps"]
                ]
            if "contains_comments" in fmt2_dict:
                fmt2_dict["contains_comments"] = [
                    comment_label_map.get(idx, idx) for idx in fmt2_dict["contains_comments"]
                ]

        result.append(WorkflowComment.model_validate(fmt2_dict))

    return result
