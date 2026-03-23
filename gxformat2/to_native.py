"""Convert Format2 workflows to native Galaxy format using typed models.

This module provides :func:`to_native` which accepts any workflow
representation and returns a :class:`NormalizedNativeWorkflow` (or
:class:`ExpandedNativeWorkflow` when ``expand=True``).
"""

from __future__ import annotations

import json
import logging
import uuid as uuid_mod
from pathlib import Path
from typing import Any, Literal, overload

from ._labels import Labels
from .model import (
    clean_connection,
    resolve_source_reference,
    setup_connected_values,
    SUPPORT_LEGACY_CONNECTIONS,
    unflatten_comment_data,
)
from .normalized._expanded import (
    expanded_native,
    ExpandedNativeWorkflow,
)
from .normalized._format2 import (
    normalized_format2,
    NormalizedFormat2,
    NormalizedWorkflowStep,
)
from .normalized._native import (
    NormalizedNativeStep,
    NormalizedNativeWorkflow,
)
from .options import ConversionOptions
from .schema.gxformat2 import (
    GalaxyWorkflow,
    WorkflowComment,
    WorkflowInputParameter,
    WorkflowOutputParameter,
    WorkflowStepOutput,
)
from .schema.native import (
    NativeInputConnection,
    NativePostJobAction,
    NativeStepType,
    NativeWorkflowOutput,
    StepPosition,
)

log = logging.getLogger(__name__)

POST_JOB_ACTIONS = {
    "hide": {
        "action_class": "HideDatasetAction",
        "default": False,
        "arguments": lambda x: {},
    },
    "rename": {
        "action_class": "RenameDatasetAction",
        "default": {},
        "arguments": lambda x: {"newname": x},
    },
    "delete_intermediate_datasets": {
        "action_class": "DeleteIntermediatesAction",
        "default": False,
        "arguments": lambda x: {},
    },
    "change_datatype": {
        "action_class": "ChangeDatatypeAction",
        "default": {},
        "arguments": lambda x: {"newtype": x},
    },
    "set_columns": {
        "action_class": "ColumnSetAction",
        "default": {},
        "arguments": lambda x: x,
    },
    "add_tags": {
        "action_class": "TagDatasetAction",
        "default": [],
        "arguments": lambda x: {"tags": ",".join(x)},
    },
    "remove_tags": {
        "action_class": "RemoveTagDatasetAction",
        "default": [],
        "arguments": lambda x: {"tags": ",".join(x)},
    },
}


@overload
def to_native(
    workflow: dict[str, Any] | str | Path | NormalizedFormat2 | GalaxyWorkflow,
    options: ConversionOptions,
    expand: Literal[True],
) -> ExpandedNativeWorkflow: ...


@overload
def to_native(
    workflow: dict[str, Any] | str | Path | NormalizedFormat2 | GalaxyWorkflow,
    options: ConversionOptions | None = None,
    expand: Literal[False] = False,
) -> NormalizedNativeWorkflow: ...


def to_native(
    workflow: dict[str, Any] | str | Path | NormalizedFormat2 | GalaxyWorkflow,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> NormalizedNativeWorkflow | ExpandedNativeWorkflow:
    """Convert a Format2 workflow to native Galaxy format.

    Returns :class:`NormalizedNativeWorkflow` by default, or
    :class:`ExpandedNativeWorkflow` when ``expand=True`` (resolving
    all URL/TRS/@import subworkflow references).
    """
    options = options or ConversionOptions()
    if not isinstance(workflow, NormalizedFormat2):
        workflow = normalized_format2(workflow)

    ctx = _ConversionContext(options)
    # Register labels: inputs first, then steps
    for i, inp in enumerate(workflow.inputs):
        label = inp.id
        if label:
            ctx.labels[label] = i
    for j, step in enumerate(workflow.steps):
        idx = len(workflow.inputs) + j
        label = step.label or step.id
        if label:
            ctx.labels[label] = idx

    result = _build_native_workflow(workflow, ctx)

    if expand:
        return expanded_native(result, options)
    return result


class _ConversionContext:
    """Internal conversion state — not part of public API."""

    def __init__(self, options: ConversionOptions):
        self.options = options
        self.labels: dict[str, int] = {}
        self.subworkflow_contexts: dict[str, _ConversionContext] = {}

    def step_id(self, label_or_id: str | int) -> int:
        if label_or_id in self.labels:
            return self.labels[label_or_id]
        return int(label_or_id)

    def step_output(self, value: str) -> tuple[int, str]:
        label_or_id, output_name = resolve_source_reference(str(value), self.labels)
        return self.step_id(label_or_id), output_name

    def child_context(self) -> _ConversionContext:
        return _ConversionContext(self.options)


def _build_native_workflow(
    wf: NormalizedFormat2,
    ctx: _ConversionContext,
) -> NormalizedNativeWorkflow:
    # Build input steps
    native_steps: dict[str, NormalizedNativeStep] = {}
    for i, inp in enumerate(wf.inputs):
        native_steps[str(i)] = _build_input_step(inp, i, ctx)

    # Build non-input steps
    inputs_offset = len(wf.inputs)
    for j, step in enumerate(wf.steps):
        order_index = inputs_offset + j
        native_steps[str(order_index)] = _build_step(step, order_index, ctx)

    # Wire workflow outputs to steps
    _wire_workflow_outputs(wf.outputs, native_steps, ctx)

    # Convert comments
    comments = _build_native_comments(wf.comments, ctx)

    return NormalizedNativeWorkflow(
        a_galaxy_workflow="true",
        format_version="0.1",
        name=wf.label or "Workflow",
        uuid=wf.uuid or str(uuid_mod.uuid4()),
        annotation=wf.doc or "",
        tags=wf.tags,
        license=wf.license,
        release=wf.release,
        creator=wf.creator,
        report=wf.report,
        steps=native_steps,
        comments=comments,
    )


def _build_input_step(
    inp: WorkflowInputParameter,
    order_index: int,
    ctx: _ConversionContext,
) -> NormalizedNativeStep:
    label = inp.id or f"Input {order_index}"
    input_type = inp.type_
    if isinstance(input_type, list):
        if len(input_type) != 1:
            raise Exception("Only simple arrays of workflow inputs are currently supported")
        input_type = input_type[0]
        multiple = True
    else:
        multiple = False

    type_str = input_type.value if hasattr(input_type, "value") else str(input_type) if input_type else "data"
    if type_str in ("File", "data", "data_input"):
        step_type = NativeStepType.data_input
    elif type_str in ("collection", "data_collection", "data_collection_input"):
        step_type = NativeStepType.data_collection_input
    elif type_str in ("text", "string", "integer", "int", "float", "color", "boolean"):
        step_type = NativeStepType.parameter_input
    else:
        raise Exception(f"Unknown input type [{type_str}] encountered.")

    tool_state: dict[str, Any] = {"name": label}
    if step_type == NativeStepType.parameter_input:
        native_type = type_str
        if native_type == "int":
            native_type = "integer"
        elif native_type == "string":
            native_type = "text"
        tool_state["parameter_type"] = native_type
    if multiple:
        tool_state["multiple"] = True
    if inp.optional is not None:
        tool_state["optional"] = inp.optional
    if inp.format:
        tool_state["format"] = inp.format
    if inp.collection_type:
        tool_state["collection_type"] = inp.collection_type
    if inp.default is not None:
        tool_state["default"] = inp.default

    # Copy extra fields from input (restrictions, suggestions, etc.)
    if inp.model_extra:
        for key in ("restrictions", "suggestions", "restrictOnConnections", "fields", "column_definitions"):
            if key in inp.model_extra:
                tool_state[key] = inp.model_extra[key]

    position = _default_position(inp.position, order_index)

    in_ = None
    default = inp.default
    if isinstance(default, dict) and default.get("class") == "File":
        in_ = {"default": {"default": default}}
        tool_state.pop("default", None)

    return NormalizedNativeStep(
        id=order_index,
        type_=step_type,
        label=label,
        name=label,
        annotation=_join_doc(inp.doc) or "",
        tool_state=tool_state,
        position=position,
        inputs=[{"name": label, "description": ""}],
        in_=in_,
    )


def _build_step(
    step: NormalizedWorkflowStep,
    order_index: int,
    ctx: _ConversionContext,
) -> NormalizedNativeStep:
    step_type = _resolve_step_type(step)

    if step_type == NativeStepType.tool:
        return _build_tool_step(step, order_index, ctx)
    elif step_type == NativeStepType.subworkflow:
        return _build_subworkflow_step(step, order_index, ctx)
    elif step_type == NativeStepType.pause:
        return _build_pause_step(step, order_index, ctx)
    elif step_type == NativeStepType.pick_value:
        return _build_pick_value_step(step, order_index, ctx)
    else:
        raise NotImplementedError(f"Unhandled step type: {step_type}")


def _resolve_step_type(step: NormalizedWorkflowStep) -> NativeStepType:
    if step.run is not None:
        if isinstance(step.run, (NormalizedFormat2, GalaxyWorkflow, dict)):
            run_dict = step.run if isinstance(step.run, dict) else None
            if run_dict and run_dict.get("class") == "GalaxyUserTool":
                return NativeStepType.tool
            return NativeStepType.subworkflow
        elif isinstance(step.run, str):
            # URL reference — treat as subworkflow
            return NativeStepType.subworkflow
    step_type_str = step.type_.value if step.type_ else "tool"
    # Handle aliases
    alias_map = {
        "input": "data_input",
        "input_collection": "data_collection_input",
        "parameter": "parameter_input",
    }
    step_type_str = alias_map.get(step_type_str, step_type_str)
    return NativeStepType(step_type_str)


def _build_tool_step(
    step: NormalizedWorkflowStep,
    order_index: int,
    ctx: _ConversionContext,
) -> NormalizedNativeStep:
    # Handle user-defined tools
    tool_representation: dict[str, Any] | None = None
    if isinstance(step.run, dict) and step.run.get("class") == "GalaxyUserTool":
        tool_representation = step.run
    elif isinstance(step.run, NormalizedFormat2):
        # Shouldn't reach here for tools, but defensive
        pass

    tool_id = step.tool_id
    if tool_id is None and tool_representation is None:
        raise Exception("Tool steps must define a tool_id.")

    # Build tool state
    tool_state: dict[str, Any] = {"__page__": 0}
    connect = _extract_connections(step)

    runtime_inputs = step.runtime_inputs or []
    if step.state is not None or runtime_inputs:
        step_state = dict(step.state) if step.state else {}
        step_state = setup_connected_values(step_state, append_to=connect)

        encoder = ctx.options.native_state_encoder
        encoded = None
        if encoder is not None:
            try:
                step_as_dict = {"tool_id": tool_id, "tool_version": step.tool_version}
                encoded = encoder(step_as_dict, step_state)
            except Exception:
                log.warning("native_state_encoder failed for %s, falling back to default", tool_id, exc_info=True)

        if encoded is not None:
            tool_state.update(encoded)
        else:
            for key, value in step_state.items():
                tool_state[key] = value
        for runtime_input in runtime_inputs:
            tool_state[runtime_input] = {"__class__": "RuntimeValue"}
    elif step.tool_state is not None:
        if isinstance(step.tool_state, str):
            tool_state.update(json.loads(step.tool_state))
        elif isinstance(step.tool_state, dict):
            tool_state.update(step.tool_state)

    # Build input connections
    input_connections = _build_input_connections(connect, ctx, is_subworkflow=False)

    # Build post job actions
    post_job_actions = _build_post_job_actions(step.out)

    position = _default_position(step.position, order_index)

    return NormalizedNativeStep(
        id=order_index,
        type_=NativeStepType.tool,
        label=step.label,
        name=tool_id or (tool_representation or {}).get("name", "User Defined Tool"),
        annotation=step.doc or "",
        tool_id=tool_id,
        tool_version=step.tool_version,
        tool_shed_repository=step.tool_shed_repository,
        tool_state=tool_state,
        tool_representation=tool_representation,
        input_connections=input_connections,
        post_job_actions=post_job_actions,
        position=position,
        when=step.when,
        uuid=step.uuid,
        errors=step.errors,
    )


def _build_subworkflow_step(
    step: NormalizedWorkflowStep,
    order_index: int,
    ctx: _ConversionContext,
) -> NormalizedNativeStep:
    # Resolve subworkflow
    subworkflow: NormalizedNativeWorkflow | None = None
    content_id: str | None = None

    subworkflow_child_ctx: _ConversionContext | None = None
    if isinstance(step.run, NormalizedFormat2):
        subworkflow_child_ctx = ctx.child_context()
        _register_subworkflow_labels(step.run, subworkflow_child_ctx)
        subworkflow = _build_native_workflow(step.run, subworkflow_child_ctx)
    elif isinstance(step.run, str):
        # URL reference — pass through as content_id
        content_id = step.run
    elif isinstance(step.run, dict):
        # Dict subworkflow — normalize and convert
        subworkflow_child_ctx = ctx.child_context()
        sub_fmt2 = normalized_format2(step.run)
        _register_subworkflow_labels(sub_fmt2, subworkflow_child_ctx)
        subworkflow = _build_native_workflow(sub_fmt2, subworkflow_child_ctx)

    connect = _extract_connections(step)
    is_subworkflow = subworkflow is not None
    input_connections = _build_input_connections(
        connect, ctx, is_subworkflow=is_subworkflow, subworkflow_ctx=subworkflow_child_ctx
    )
    post_job_actions = _build_post_job_actions(step.out)
    position = _default_position(step.position, order_index)

    return NormalizedNativeStep(
        id=order_index,
        type_=NativeStepType.subworkflow,
        label=step.label,
        annotation=step.doc or "",
        tool_state={},
        subworkflow=subworkflow,
        content_id=content_id,
        input_connections=input_connections,
        post_job_actions=post_job_actions,
        position=position,
        when=step.when,
        uuid=step.uuid,
    )


def _build_pause_step(
    step: NormalizedWorkflowStep,
    order_index: int,
    ctx: _ConversionContext,
) -> NormalizedNativeStep:
    name = step.label or "Pause for dataset review"
    connect = _extract_connections(step)
    input_connections = _build_input_connections(connect, ctx)
    position = _default_position(step.position, order_index)

    return NormalizedNativeStep(
        id=order_index,
        type_=NativeStepType.pause,
        label=step.label,
        name=name,
        annotation=step.doc or "",
        tool_state={"name": name},
        input_connections=input_connections,
        inputs=[{"name": name, "description": ""}],
        position=position,
        uuid=step.uuid,
    )


def _build_pick_value_step(
    step: NormalizedWorkflowStep,
    order_index: int,
    ctx: _ConversionContext,
) -> NormalizedNativeStep:
    name = step.label or "Pick Value"
    tool_state: dict[str, Any] = dict(step.state) if step.state else {}
    tool_state["name"] = name

    connect = _extract_connections(step)
    input_connections = _build_input_connections(connect, ctx)

    num_inputs = len(input_connections)
    if num_inputs > 0:
        tool_state["num_inputs"] = max(2, num_inputs)

    post_job_actions = _build_post_job_actions(step.out)
    position = _default_position(step.position, order_index)

    return NormalizedNativeStep(
        id=order_index,
        type_=NativeStepType.pick_value,
        label=step.label,
        name=name,
        annotation=step.doc or "",
        tool_state=tool_state,
        input_connections=input_connections,
        post_job_actions=post_job_actions,
        inputs=[{"name": name, "description": ""}],
        position=position,
        uuid=step.uuid,
    )


# --- Shared helpers ---


def _extract_connections(step: NormalizedWorkflowStep) -> dict[str, list]:
    """Extract connection info from step inputs.

    Converts NormalizedWorkflowStep.in_ (list of WorkflowStepInput with
    source fields) into a connect dict compatible with connection building.
    """
    connect: dict[str, list] = {}
    for step_input in step.in_:
        input_id = step_input.id
        if input_id is None:
            continue
        source = step_input.source
        if source is not None:
            if isinstance(source, list):
                connect[input_id] = source
            else:
                connect[input_id] = [source]
    return connect


def _build_input_connections(
    connect: dict[str, list],
    ctx: _ConversionContext,
    is_subworkflow: bool = False,
    subworkflow_ctx: _ConversionContext | None = None,
) -> dict[str, NativeInputConnection | list[NativeInputConnection]]:
    input_connections: dict[str, NativeInputConnection | list[NativeInputConnection]] = {}

    for key, values in connect.items():
        connection_list: list[NativeInputConnection] = []
        for value in values:
            if isinstance(value, str):
                if key == "$step":
                    value += "/__NO_INPUT_OUTPUT_NAME__"
                step_id, output_name = ctx.step_output(value)
                conn = NativeInputConnection(id=step_id, output_name=output_name)
                if is_subworkflow and subworkflow_ctx and key in subworkflow_ctx.labels:
                    conn = NativeInputConnection(
                        id=step_id,
                        output_name=output_name,
                        input_subworkflow_step_id=subworkflow_ctx.step_id(key),
                    )
                connection_list.append(conn)

        actual_key = "__NO_INPUT_OUTPUT_NAME__" if key == "$step" else key
        if connection_list:
            input_connections[actual_key] = connection_list if len(connection_list) > 1 else connection_list[0]

    return input_connections


def _build_post_job_actions(
    outputs: list[WorkflowStepOutput],
) -> dict[str, NativePostJobAction]:
    post_job_actions: dict[str, NativePostJobAction] = {}
    for output in outputs:
        output_name = output.id
        if output_name is None:
            continue
        for action_key, action_dict in POST_JOB_ACTIONS.items():
            action_value = getattr(output, action_key, None)
            if action_value is None:
                action_value = action_dict["default"]
            if action_value:
                action_class = action_dict["action_class"]
                action_name = action_class + output_name
                post_job_actions[action_name] = NativePostJobAction(
                    action_type=action_class,
                    output_name=output_name,
                    action_arguments=action_dict["arguments"](action_value),
                )
    return post_job_actions


def _wire_workflow_outputs(
    outputs: list[WorkflowOutputParameter],
    native_steps: dict[str, NormalizedNativeStep],
    ctx: _ConversionContext,
) -> None:
    """Attach workflow outputs to the appropriate native steps."""
    for output in outputs:
        output_source = output.outputSource
        if output_source is None:
            continue

        source = clean_connection(output_source)
        if source is None and SUPPORT_LEGACY_CONNECTIONS and hasattr(output, "source"):
            source = getattr(output, "source", "").replace("#", "/", 1)
        if source is None:
            continue

        step_id_int, output_name = ctx.step_output(source)
        step_key = str(step_id_int)
        if step_key not in native_steps:
            continue

        raw_label = output.label or output.id
        label = raw_label
        if label and Labels.is_anonymous_output_label(label):
            label = None

        workflow_output = NativeWorkflowOutput(
            output_name=output_name,
            label=label,
            uuid=output.uuid if hasattr(output, "uuid") else None,
        )
        step = native_steps[step_key]
        step.workflow_outputs.append(workflow_output)


def _build_native_comments(
    comments: list[WorkflowComment],
    ctx: _ConversionContext,
) -> list:
    """Convert Format2 comments to native format."""
    if not comments:
        return []

    comment_dicts = [c.model_dump(by_alias=True, exclude_none=True) for c in comments]

    comment_label_map: dict[str, int] = {}
    for i, comment in enumerate(comment_dicts):
        label = comment.get("label")
        if label:
            comment_label_map[label] = i

    native_comments = []
    for i, comment in enumerate(comment_dicts):
        native_comment = unflatten_comment_data(comment)
        native_comment["id"] = i

        if "child_steps" in native_comment:
            native_comment["child_steps"] = [
                ctx.step_id(ref) if isinstance(ref, str) else ref for ref in native_comment["child_steps"]
            ]

        if "child_comments" in native_comment:
            resolved = []
            for ref in native_comment["child_comments"]:
                if isinstance(ref, str):
                    if ref not in comment_label_map:
                        raise Exception(f"contains_comments references unknown comment label '{ref}'")
                    resolved.append(comment_label_map[ref])
                else:
                    resolved.append(ref)
            native_comment["child_comments"] = resolved

        native_comments.append(native_comment)

    return native_comments


def _register_subworkflow_labels(sub_wf: NormalizedFormat2, child_ctx: _ConversionContext) -> None:
    """Register input and step labels from a subworkflow into a child context."""
    for i, inp in enumerate(sub_wf.inputs):
        if inp.id:
            child_ctx.labels[inp.id] = i
    for j, sub_step in enumerate(sub_wf.steps):
        sub_label = sub_step.label or sub_step.id
        if sub_label:
            child_ctx.labels[sub_label] = len(sub_wf.inputs) + j


def _default_position(position: StepPosition | None, order_index: int) -> StepPosition:
    if position is not None:
        return position
    return StepPosition(left=10 * order_index, top=10 * order_index)


def _join_doc(doc: str | list[str] | None) -> str | None:
    if doc is None:
        return None
    if isinstance(doc, list):
        return "\n".join(doc) if doc else None
    return doc
