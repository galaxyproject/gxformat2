"""Unified conversion module: native<->Format2, expansion, and ensure_ entry points.

This module deliberately consolidates three concerns that were previously
split across ``to_format2``, ``to_native``, and ``normalized/_expanded``:

1. **Conversion** — native Galaxy (.ga) <-> Format2 (YAML) transforms.
2. **Expansion** — resolving external ``@import``, URL, and TRS references
   in step ``run`` / ``subworkflow`` fields.
3. **ensure_ entry points** — polymorphic helpers that accept *any*
   workflow representation and return the desired typed model.

These three concerns are tightly coupled: expansion needs conversion for
cross-format subworkflows (e.g. a Format2 workflow that ``run:`` references
a native .ga URL must convert it before inlining).  Conversion needs
expansion for the ``expand=True`` path.  When they lived in separate
modules, this created circular imports between ``to_format2 -> _expanded
-> to_format2`` and ``to_native -> _expanded -> to_native``, which required
ugly lazy imports.  Merging into one module eliminates the cycle entirely
and makes the call graph explicit.
"""

from __future__ import annotations

import json
import logging
import os
import uuid as uuid_mod
from pathlib import Path
from typing import Any, Callable, Literal, overload, TypedDict

from pydantic import Field

from .._comment_helpers import flatten_comment_data, unflatten_comment_data
from .._labels import Labels, UNLABELED_INPUT_PREFIX, UNLABELED_STEP_PREFIX
from ..options import (
    ConversionOptions,
    default_url_resolver,
    MAX_EXPANSION_DEPTH,
)
from ..schema.gxformat2 import (
    CreatorOrganization,
    CreatorPerson,
    FrameComment,
    FreehandComment,
    GalaxyWorkflow,
    MarkdownComment,
    Report,
)
from ..schema.gxformat2 import StepPosition as Format2StepPosition
from ..schema.gxformat2 import (
    TextComment,
)
from ..schema.gxformat2 import ToolShedRepository as Format2ToolShedRepository
from ..schema.gxformat2 import (
    WorkflowInputParameter,
    WorkflowOutputParameter,
    WorkflowStepInput,
    WorkflowStepOutput,
    WorkflowStepType,
)
from ..schema.native import (
    NativeCreatorOrganization,
    NativeCreatorPerson,
    NativeGalaxyWorkflow,
    NativeInputConnection,
    NativePostJobAction,
    NativeReport,
    NativeStepInput,
    NativeStepType,
    NativeWorkflowOutput,
)
from ..schema.native import StepPosition as NativeStepPosition
from ..schema.native import (
    ToolShedRepository,
)
from ..yaml import ordered_load_path
from ._format2 import (
    GalaxyUserToolStub,
    ImportReference,
    normalized_format2,
    NormalizedFormat2,
    NormalizedWorkflowStep,
    resolve_source_reference,
)
from ._native import (
    normalized_native,
    NormalizedNativeStep,
    NormalizedNativeWorkflow,
)

log = logging.getLogger(__name__)


# --- Expanded model definitions ---


class ExpandedWorkflowStep(NormalizedWorkflowStep):
    """Format2 step with run fully resolved."""

    run: ExpandedFormat2 | None = Field(default=None, description="Always resolved or absent.")


class ExpandedFormat2(NormalizedFormat2):
    """Format2 workflow with all references expanded."""

    steps: list[ExpandedWorkflowStep] = Field(default_factory=list)


class ExpandedNativeStep(NormalizedNativeStep):
    """Native step with subworkflow references resolved."""

    subworkflow: ExpandedNativeWorkflow | None = Field(default=None)


class ExpandedNativeWorkflow(NormalizedNativeWorkflow):
    """Native workflow with all subworkflow references resolved."""

    steps: dict[str, ExpandedNativeStep] = Field(default_factory=dict)


ExpandedWorkflowStep.model_rebuild()
ExpandedFormat2.model_rebuild()
ExpandedNativeStep.model_rebuild()
ExpandedNativeWorkflow.model_rebuild()


# --- Expansion context and helpers ---


class _ExpansionContext:
    """Internal context for tracking cycle detection during expansion."""

    def __init__(self, options: ConversionOptions, resolving_urls: frozenset[str] = frozenset()):
        self.options = options
        self._resolving_urls = resolving_urls
        self._resolver = options.url_resolver or default_url_resolver

    def resolve_url(self, url: str) -> dict[str, Any]:
        if url in self._resolving_urls:
            raise ValueError(f"Circular subworkflow reference: {url}")
        if len(self._resolving_urls) >= MAX_EXPANSION_DEPTH:
            raise ValueError(f"Max expansion depth ({MAX_EXPANSION_DEPTH}) exceeded")
        return self._resolver(url)

    def resolve_import(self, path: str) -> dict[str, Any]:
        if self.options.workflow_directory is None:
            raise ValueError(f"Cannot resolve @import '{path}' without workflow_directory")
        full_path = os.path.join(self.options.workflow_directory, path)
        return ordered_load_path(full_path)

    def child(self, url: str) -> _ExpansionContext:
        return _ExpansionContext(self.options, self._resolving_urls | {url})


def _resolve_run_reference(ref: str, ctx: _ExpansionContext) -> dict[str, Any]:
    """Resolve a run reference (URL or file path) to a workflow dict."""
    if "://" in ref:
        return ctx.resolve_url(ref)
    return ctx.resolve_import(ref)


def _is_resolvable_url(content_id: str) -> bool:
    """Check if a content_id is a URL that can be fetched."""
    return content_id.startswith(("http://", "https://", "base64://"))


def _ensure_format2(resolved: dict[str, Any], options: ConversionOptions) -> NormalizedFormat2:
    """Convert a fetched workflow dict to NormalizedFormat2, handling cross-format."""
    if resolved.get("a_galaxy_workflow") == "true":
        return to_format2(resolved, options=options, expand=False)
    return normalized_format2(resolved)


def _ensure_native(resolved: dict[str, Any], options: ConversionOptions) -> NormalizedNativeWorkflow:
    """Convert a fetched workflow dict to NormalizedNativeWorkflow, handling cross-format."""
    if resolved.get("a_galaxy_workflow") == "true":
        return normalized_native(resolved)
    return to_native(resolved, options=options, expand=False)


# --- ensure_ entry points ---


@overload
def ensure_format2(
    workflow: dict[str, Any] | str | Path | NativeGalaxyWorkflow | NormalizedNativeWorkflow,
    options: ConversionOptions,
    expand: Literal[True],
) -> ExpandedFormat2: ...


@overload
def ensure_format2(
    workflow: dict[str, Any] | str | Path | NativeGalaxyWorkflow | NormalizedNativeWorkflow,
    options: ConversionOptions | None = None,
    expand: Literal[False] = False,
) -> NormalizedFormat2: ...


@overload
def ensure_format2(
    workflow: GalaxyWorkflow | NormalizedFormat2,
    options: ConversionOptions,
    expand: Literal[True],
) -> ExpandedFormat2: ...


@overload
def ensure_format2(
    workflow: GalaxyWorkflow | NormalizedFormat2,
    options: ConversionOptions | None = None,
    expand: Literal[False] = False,
) -> NormalizedFormat2: ...


def ensure_format2(
    workflow: (
        dict[str, Any]
        | str
        | Path
        | NativeGalaxyWorkflow
        | NormalizedNativeWorkflow
        | GalaxyWorkflow
        | NormalizedFormat2
    ),
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> NormalizedFormat2 | ExpandedFormat2:
    """Ensure a workflow is returned as Format2 typed models.

    Accepts native or Format2 inputs (raw dict/path or typed models),
    normalizing/converting as needed, and optionally expanding refs.
    """
    options = options or ConversionOptions()

    if isinstance(workflow, NormalizedFormat2):
        result = workflow
    elif isinstance(workflow, GalaxyWorkflow):
        result = normalized_format2(workflow)
    elif isinstance(workflow, (NativeGalaxyWorkflow, NormalizedNativeWorkflow)):
        result = to_format2(workflow, options=options, expand=False)
    else:
        result = normalized_format2(workflow)

    if expand:
        return expanded_format2(result, options)
    return result


@overload
def ensure_native(
    workflow: dict[str, Any] | str | Path | NormalizedFormat2 | GalaxyWorkflow,
    options: ConversionOptions,
    expand: Literal[True],
) -> ExpandedNativeWorkflow: ...


@overload
def ensure_native(
    workflow: dict[str, Any] | str | Path | NormalizedFormat2 | GalaxyWorkflow,
    options: ConversionOptions | None = None,
    expand: Literal[False] = False,
) -> NormalizedNativeWorkflow: ...


@overload
def ensure_native(
    workflow: NativeGalaxyWorkflow | NormalizedNativeWorkflow,
    options: ConversionOptions,
    expand: Literal[True],
) -> ExpandedNativeWorkflow: ...


@overload
def ensure_native(
    workflow: NativeGalaxyWorkflow | NormalizedNativeWorkflow,
    options: ConversionOptions | None = None,
    expand: Literal[False] = False,
) -> NormalizedNativeWorkflow: ...


def ensure_native(
    workflow: (
        dict[str, Any]
        | str
        | Path
        | NormalizedFormat2
        | GalaxyWorkflow
        | NativeGalaxyWorkflow
        | NormalizedNativeWorkflow
    ),
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> NormalizedNativeWorkflow | ExpandedNativeWorkflow:
    """Ensure a workflow is returned as native typed models.

    Accepts native or Format2 inputs (raw dict/path or typed models),
    normalizing/converting as needed, and optionally expanding refs.
    """
    options = options or ConversionOptions()

    if isinstance(workflow, NormalizedNativeWorkflow):
        result = workflow
    elif isinstance(workflow, NativeGalaxyWorkflow):
        result = normalized_native(workflow)
    elif isinstance(workflow, (NormalizedFormat2, GalaxyWorkflow)):
        result = to_native(workflow, options=options, expand=False)
    elif isinstance(workflow, dict) and workflow.get("a_galaxy_workflow") == "true":
        result = normalized_native(workflow)
    elif isinstance(workflow, dict) and workflow.get("class") == "GalaxyWorkflow":
        result = to_native(workflow, options=options, expand=False)
    else:
        # str or Path — could be either format, try native first
        loaded = ordered_load_path(str(workflow)) if isinstance(workflow, (str, Path)) else workflow
        if isinstance(loaded, dict) and loaded.get("a_galaxy_workflow") == "true":
            result = normalized_native(loaded)
        else:
            result = to_native(loaded, options=options, expand=False)

    if expand:
        return expanded_native(result, options)
    return result


# --- Format2 conversion (native -> format2) ---


INPUT_STEP_TYPES = ("data_input", "data_collection_input", "parameter_input")


def native_input_to_format2_type(step: dict, tool_state: dict) -> str | list[str]:
    """Return a Format2 input type ('type') from a native input step dictionary."""
    module_type = step.get("type")
    if module_type == "data_collection_input":
        format2_type = "collection"
    elif module_type == "data_input":
        format2_type = "data"
    elif module_type == "parameter_input":
        native_type = tool_state.get("parameter_type", "")
        format2_type = native_type
        if native_type == "integer":
            format2_type = "int"
        elif native_type == "text":
            format2_type = "string"
        if tool_state.get("multiple", False):
            return [format2_type]
    return format2_type


def _convert_position(position: NativeStepPosition | None) -> Format2StepPosition | None:
    if position is None:
        return None
    return Format2StepPosition(left=position.left, top=position.top)


def _convert_tool_shed_repo_to_format2(repo) -> Format2ToolShedRepository | None:
    if repo is None:
        return None
    return Format2ToolShedRepository(
        name=repo.name,
        changeset_revision=repo.changeset_revision,
        owner=repo.owner,
        tool_shed=repo.tool_shed,
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
            output_params.append(
                WorkflowOutputParameter(
                    id=output_id,
                    outputSource=source,
                )
            )

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
        creator=_convert_creators(wf.creator),
        license=wf.license,
        release=wf.release,
        uuid=wf.uuid,
    )


def _build_input_param(step: NormalizedNativeStep) -> WorkflowInputParameter:
    step_id = step.label if step.label is not None else f"{UNLABELED_INPUT_PREFIX}{step.id}"
    tool_state = step.tool_state
    input_type = native_input_to_format2_type({"type": step.type_}, tool_state)

    kwargs: dict[str, Any] = {"id": step_id, "type_": input_type}

    for key in (
        "collection_type",
        "optional",
        "format",
        "default",
        "restrictions",
        "suggestions",
        "restrictOnConnections",
        "fields",
        "column_definitions",
    ):
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

    in_list = _build_format2_step_inputs(step, label_map)
    out_list = _build_format2_step_outputs(step)

    # Handle tool state
    state: dict[str, Any] | None = None
    tool_state: str | dict[str, Any] | None = None

    converted_state = None
    if options.state_encode_to_format2 is not None:
        try:
            step_dict = step.model_dump(by_alias=True, exclude_none=True)
            converted_state = options.state_encode_to_format2(step_dict)
        except Exception:
            log.warning("state_encode_to_format2 failed for %s, falling back", step.tool_id, exc_info=True)

    if converted_state is not None:
        state = converted_state
    else:
        ts = dict(step.tool_state)
        ts.pop("__page__", None)
        ts.pop("__rerun_remap_job_id__", None)
        tool_state = ts

    raw_label = step.label or label_map.get(str(step.id))
    step_id = raw_label or str(step.id)
    display_label = None if (raw_label and Labels.is_unlabeled(raw_label)) else raw_label

    return NormalizedWorkflowStep(
        id=step_id,
        label=display_label,
        doc=step.annotation or None,
        tool_id=step.tool_id,
        tool_version=step.tool_version,
        tool_shed_repository=_convert_tool_shed_repo_to_format2(step.tool_shed_repository),
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
    in_list = _build_format2_step_inputs(step, label_map)
    out_list = _build_format2_step_outputs(step)
    raw_label = step.label or label_map.get(str(step.id))
    step_id = raw_label or str(step.id)

    return NormalizedWorkflowStep(
        id=step_id,
        label=raw_label,
        doc=step.annotation or None,
        run=GalaxyUserToolStub.model_validate(step.tool_representation) if step.tool_representation else None,
        in_=in_list,
        out=out_list,
        position=_convert_position(step.position) if not compact else None,
    )


def _build_subworkflow_format2_step(
    step: NormalizedNativeStep,
    label_map: dict[str, str],
    options: ConversionOptions,
) -> NormalizedWorkflowStep:
    in_list = _build_format2_step_inputs(step, label_map)
    out_list = _build_format2_step_outputs(step)

    run: NormalizedFormat2 | str | None = None
    content_source = step.content_source
    if content_source in ("url", "trs_url") and step.content_id:
        run = step.content_id
    elif step.subworkflow is not None:
        run = _build_format2_workflow(step.subworkflow, options)
    elif step.content_id:
        run = step.content_id

    raw_label = step.label or label_map.get(str(step.id))
    step_id = raw_label or str(step.id)
    display_label = None if (raw_label and Labels.is_unlabeled(raw_label)) else raw_label

    return NormalizedWorkflowStep(
        id=step_id,
        label=display_label,
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
    in_list = _build_format2_step_inputs(step, label_map)
    raw_label = step.label or label_map.get(str(step.id))
    step_id = raw_label or str(step.id)
    display_label = None if (raw_label and Labels.is_unlabeled(raw_label)) else raw_label

    return NormalizedWorkflowStep(
        id=step_id,
        label=display_label,
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
    in_list = _build_format2_step_inputs(step, label_map)
    out_list = _build_format2_step_outputs(step)

    state: dict[str, Any] | None = None
    tool_state = step.tool_state
    if "mode" in tool_state:
        state = {"mode": tool_state["mode"]}

    raw_label = step.label or label_map.get(str(step.id))
    step_id = raw_label or str(step.id)
    display_label = None if (raw_label and Labels.is_unlabeled(raw_label)) else raw_label

    return NormalizedWorkflowStep(
        id=step_id,
        label=display_label,
        doc=step.annotation or None,
        type_=WorkflowStepType.pick_value,
        state=state,
        in_=in_list,
        out=out_list,
        position=_convert_position(step.position) if not compact else None,
    )


def _build_format2_step_inputs(
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
            sources = [
                s.rsplit("/__NO_INPUT_OUTPUT_NAME__", 1)[0] if "/__NO_INPUT_OUTPUT_NAME__" in s else s for s in sources
            ]

        source_val: str | list[str] = sources[0] if len(sources) == 1 else sources
        default = defaults.pop(actual_name, None)
        in_list.append(
            WorkflowStepInput(
                id=actual_name,
                source=source_val,
                default=default,
            )
        )

    # Add remaining defaults without connections
    for key, default in defaults.items():
        in_list.append(WorkflowStepInput(id=key, default=default))

    return in_list


def _build_format2_step_outputs(step: NormalizedNativeStep) -> list[WorkflowStepOutput]:
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
            if action_args:
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


_CREATOR_CLASS_MAP: dict[str, type[CreatorPerson] | type[CreatorOrganization]] = {
    "Person": CreatorPerson,
    "Organization": CreatorOrganization,
}


def _convert_creators(
    native_creators: list | None,
) -> list[CreatorPerson | CreatorOrganization] | None:
    if not native_creators:
        return None
    result: list[CreatorPerson | CreatorOrganization] = []
    for c in native_creators:
        d = c.model_dump(by_alias=True, exclude_none=True) if hasattr(c, "model_dump") else c
        cls = _CREATOR_CLASS_MAP.get(d.get("class", ""), CreatorPerson)
        result.append(cls.model_validate(d))
    return result


_COMMENT_TYPE_MAP: dict[str, type[TextComment] | type[MarkdownComment] | type[FrameComment] | type[FreehandComment]] = {
    "text": TextComment,
    "markdown": MarkdownComment,
    "frame": FrameComment,
    "freehand": FreehandComment,
}


def _build_format2_comments(
    wf: NormalizedNativeWorkflow,
    label_map: dict[str, str],
    compact: bool,
) -> list[TextComment | MarkdownComment | FrameComment | FreehandComment]:
    if not wf.comments:
        return []

    native_comments = [c.model_dump(by_alias=True, exclude_none=True) for c in wf.comments]

    comment_label_map: dict[int, str] = {}
    for i, native_comment in enumerate(native_comments):
        label = native_comment.get("label")
        if label:
            comment_label_map[i] = label

    result: list[TextComment | MarkdownComment | FrameComment | FreehandComment] = []
    for native_comment in native_comments:
        fmt2_dict = flatten_comment_data(native_comment)

        if compact:
            fmt2_dict.pop("position", None)
            fmt2_dict.pop("size", None)

        if fmt2_dict.get("type") == "frame":
            if "contains_steps" in fmt2_dict:
                fmt2_dict["contains_steps"] = [label_map.get(str(idx)) or idx for idx in fmt2_dict["contains_steps"]]
            if "contains_comments" in fmt2_dict:
                fmt2_dict["contains_comments"] = [
                    comment_label_map.get(idx, idx) for idx in fmt2_dict["contains_comments"]
                ]

        comment_type = fmt2_dict.get("type", "text")
        model_class = _COMMENT_TYPE_MAP.get(comment_type, TextComment)
        result.append(model_class.model_validate(fmt2_dict))

    return result


# --- Native conversion (format2 -> native) ---


class _PJADef(TypedDict):
    action_class: str
    default: Any
    arguments: Callable[..., dict[str, Any]]


POST_JOB_ACTIONS: dict[str, _PJADef] = {
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

    # Handle $graph + deduplicate_subworkflows before normalization
    deduplicated_subworkflows: dict[str, NormalizedNativeWorkflow] | None = None
    if isinstance(workflow, dict) and "$graph" in workflow and "class" not in workflow:
        if options.deduplicate_subworkflows:
            deduplicated_subworkflows = {}
            graph = workflow["$graph"]
            main_dict = None
            for entry in graph:
                graph_id = entry.get("id")
                if graph_id == "main":
                    main_dict = entry
                elif graph_id:
                    sub_wf = normalized_format2(entry)
                    sub_ctx = _ConversionContext(options)
                    _register_labels(sub_wf, sub_ctx)
                    deduplicated_subworkflows[graph_id] = _build_native_workflow(sub_wf, sub_ctx)
            if main_dict is None:
                raise Exception("$graph has no 'main' workflow")
            workflow = main_dict

    if not isinstance(workflow, NormalizedFormat2):
        workflow = normalized_format2(workflow)

    ctx = _ConversionContext(options)
    _register_labels(workflow, ctx)

    result = _build_native_workflow(workflow, ctx)
    if deduplicated_subworkflows is not None:
        result = result.model_copy(update={"subworkflows": deduplicated_subworkflows})

    if expand:
        return expanded_native(result, options)
    return result


def _register_labels(wf: NormalizedFormat2, ctx: _ConversionContext) -> None:
    """Register input and step labels in the conversion context."""
    for i, inp in enumerate(wf.inputs):
        if inp.id:
            ctx.labels[inp.id] = i
    for j, step in enumerate(wf.steps):
        idx = len(wf.inputs) + j
        label = step.label or step.id
        if label:
            ctx.labels[label] = idx


class _ConversionContext:
    """Internal conversion state -- not part of public API."""

    def __init__(self, options: ConversionOptions):
        self.options = options
        self.labels: dict[str, int] = {}
        self.subworkflow_contexts: dict[str, _ConversionContext] = {}

    def step_id(self, label_or_id: str | int) -> int:
        if label_or_id in self.labels:
            return self.labels[label_or_id]  # type: ignore[index]
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
        creator=_convert_creators_to_native(wf.creator) if wf.creator else None,
        report=NativeReport(markdown=wf.report.markdown) if wf.report else None,
        steps=native_steps,
        comments=comments,
    )


def _build_input_step(
    inp: WorkflowInputParameter,
    order_index: int,
    ctx: _ConversionContext,
) -> NormalizedNativeStep:
    raw_label = inp.id or f"Input {order_index}"
    label = None if Labels.is_unlabeled(raw_label) else raw_label
    input_type = inp.type_
    if isinstance(input_type, list):
        if len(input_type) != 1:
            raise Exception("Only simple arrays of workflow inputs are currently supported")
        input_type = input_type[0]
        multiple = True
    else:
        multiple = False

    type_str = (
        input_type.value
        if input_type is not None and hasattr(input_type, "value")
        else str(input_type) if input_type else "data"
    )
    if type_str in ("File", "data", "data_input"):
        step_type = NativeStepType.data_input
    elif type_str in ("collection", "data_collection", "data_collection_input"):
        step_type = NativeStepType.data_collection_input
    elif type_str in ("text", "string", "integer", "int", "float", "color", "boolean"):
        step_type = NativeStepType.parameter_input
    else:
        raise Exception(f"Unknown input type [{type_str}] encountered.")

    tool_state: dict[str, Any] = {"name": raw_label}
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
        name=raw_label,
        annotation=_join_doc(inp.doc) or "",
        tool_state=tool_state,
        position=position,
        inputs=[NativeStepInput(name=raw_label, description="")],
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
            # URL reference -- treat as subworkflow
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
    if isinstance(step.run, GalaxyUserToolStub):
        tool_representation = step.run.model_dump(by_alias=True, exclude_none=True)
    elif isinstance(step.run, dict) and step.run.get("class") == "GalaxyUserTool":
        tool_representation = step.run
    elif isinstance(step.run, NormalizedFormat2):
        # Shouldn't reach here for tools, but defensive
        pass

    tool_id = step.tool_id
    if tool_id is None and tool_representation is None:
        raise Exception("Tool steps must define a tool_id.")

    # Build tool state -- step.state already has $link resolved to ConnectedValue
    # and step.in_ has all connections (from in, connect, and $link sources)
    tool_state: dict[str, Any] = {"__page__": 0}
    connect = _extract_connections(step)

    runtime_inputs = step.runtime_inputs or []
    if step.state is not None or runtime_inputs:
        step_state = dict(step.state) if step.state else {}

        encoder = ctx.options.state_encode_to_native
        encoded = None
        if encoder is not None:
            try:
                step_as_dict = {"tool_id": tool_id, "tool_version": step.tool_version}
                encoded = encoder(step_as_dict, step_state)
            except Exception:
                log.warning("state_encode_to_native failed for %s, falling back to default", tool_id, exc_info=True)

        if encoded is not None:
            tool_state.update(encoded)
        else:
            tool_state.update(step_state)
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
        label=_step_label(step),
        name=tool_id or (tool_representation or {}).get("name", "User Defined Tool"),
        annotation=step.doc or "",
        tool_id=tool_id,
        tool_version=step.tool_version,
        tool_shed_repository=_convert_tool_shed_repo_to_native(step.tool_shed_repository),
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
        # URL reference -- pass through as content_id
        content_id = step.run
    elif isinstance(step.run, dict):
        # Dict subworkflow -- normalize and convert
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
        label=_step_label(step),
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
        label=_step_label(step),
        name=name,
        annotation=step.doc or "",
        tool_state={"name": name},
        input_connections=input_connections,
        inputs=[NativeStepInput(name=name, description="")],
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
        label=_step_label(step),
        name=name,
        annotation=step.doc or "",
        tool_state=tool_state,
        input_connections=input_connections,
        post_job_actions=post_job_actions,
        inputs=[NativeStepInput(name=name, description="")],
        position=position,
        uuid=step.uuid,
    )


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

        source = output_source
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
    comments: list[TextComment | MarkdownComment | FrameComment | FreehandComment],
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


def _step_label(step: NormalizedWorkflowStep) -> str | None:
    """Extract the user label from a Format2 step.

    For dict-keyed steps, the key is stored in ``id`` and ``label`` is None.
    Non-numeric ids are user labels; numeric ids are auto-assigned indices.
    Sentinel labels (``_unlabeled_*``) are cleared to None.
    """
    if step.label is not None:
        if Labels.is_unlabeled(step.label):
            return None
        return step.label
    if step.id and not step.id.isdigit():
        if Labels.is_unlabeled(step.id):
            return None
        return step.id
    return None


def _convert_tool_shed_repo_to_native(repo) -> ToolShedRepository | None:
    if repo is None:
        return None
    if isinstance(repo, ToolShedRepository):
        return repo
    return ToolShedRepository(
        name=repo.name,
        changeset_revision=repo.changeset_revision,
        owner=repo.owner,
        tool_shed=repo.tool_shed,
    )


def _default_position(position: Any, order_index: int) -> NativeStepPosition:
    if position is not None:
        if isinstance(position, NativeStepPosition):
            return position
        return NativeStepPosition(left=position.left, top=position.top)
    return NativeStepPosition(left=10 * order_index, top=10 * order_index)


_NATIVE_CREATOR_MAP: dict[str, type[NativeCreatorPerson] | type[NativeCreatorOrganization]] = {
    "Person": NativeCreatorPerson,
    "Organization": NativeCreatorOrganization,
}


def _convert_creators_to_native(
    creators: list,
) -> list[NativeCreatorPerson | NativeCreatorOrganization]:
    result: list[NativeCreatorPerson | NativeCreatorOrganization] = []
    for c in creators:
        d = c.model_dump(by_alias=True, exclude_none=True) if hasattr(c, "model_dump") else c
        cls = _NATIVE_CREATOR_MAP.get(d.get("class", ""), NativeCreatorPerson)
        result.append(cls.model_validate(d))
    return result


def _join_doc(doc: str | list[str] | None) -> str | None:
    if doc is None:
        return None
    if isinstance(doc, list):
        return "\n".join(doc) if doc else None
    return doc


# --- Expansion ---


def expanded_format2(
    workflow: dict[str, Any] | str | Path | NormalizedFormat2,
    options: ConversionOptions | None = None,
) -> ExpandedFormat2:
    """Normalize and expand a Format2 workflow, resolving all references.

    Resolves ``@import``, URL, and TRS URL references in step ``run``
    fields.  Uses ``options.url_resolver`` (or the built-in default) for
    HTTP fetches.
    """
    options = options or ConversionOptions()
    if not isinstance(workflow, NormalizedFormat2):
        workflow = normalized_format2(workflow)
    ctx = _ExpansionContext(options)
    return _expand_format2(workflow, ctx)


def expanded_native(
    workflow: dict[str, Any] | str | Path | NormalizedNativeWorkflow,
    options: ConversionOptions | None = None,
) -> ExpandedNativeWorkflow:
    """Normalize and expand a native workflow, resolving all subworkflow references.

    Resolves ``content_id`` URL references by fetching and converting
    them.  Uses ``options.url_resolver`` (or the built-in default) for
    HTTP fetches.
    """
    options = options or ConversionOptions()
    if not isinstance(workflow, NormalizedNativeWorkflow):
        workflow = normalized_native(workflow)
    ctx = _ExpansionContext(options)
    return _expand_native(workflow, ctx)


def _expand_format2(wf: NormalizedFormat2, ctx: _ExpansionContext) -> ExpandedFormat2:
    expanded_steps: list[ExpandedWorkflowStep] = []
    for step in wf.steps:
        expanded_run: ExpandedFormat2 | None = None
        if isinstance(step.run, NormalizedFormat2):
            expanded_run = _expand_format2(step.run, ctx)
        elif isinstance(step.run, str):
            resolved = _resolve_run_reference(step.run, ctx)
            child_ctx = ctx.child(step.run)
            normalized = _ensure_format2(resolved, ctx.options)
            expanded_run = _expand_format2(normalized, child_ctx)
        elif isinstance(step.run, ImportReference):
            resolved = ctx.resolve_import(step.run.import_path)
            child_ctx = ctx.child(step.run.import_path)
            normalized = _ensure_format2(resolved, ctx.options)
            expanded_run = _expand_format2(normalized, child_ctx)
        elif isinstance(step.run, dict):
            if "@import" in step.run:
                resolved = ctx.resolve_import(step.run["@import"])
            else:
                resolved = step.run
            child_ctx = ctx.child(str(step.run.get("@import", id(step.run))))
            normalized = _ensure_format2(resolved, ctx.options)
            expanded_run = _expand_format2(normalized, child_ctx)

        step_data = step.model_dump(by_alias=True, exclude={"run"})
        expanded_steps.append(ExpandedWorkflowStep(**step_data, run=expanded_run))

    wf_data = wf.model_dump(by_alias=True, exclude={"steps"})
    return ExpandedFormat2(**wf_data, steps=expanded_steps)


def _expand_native(wf: NormalizedNativeWorkflow, ctx: _ExpansionContext) -> ExpandedNativeWorkflow:
    expanded_steps: dict[str, ExpandedNativeStep] = {}
    for key, step in wf.steps.items():
        expanded_sub: ExpandedNativeWorkflow | None = None
        if step.subworkflow is not None:
            expanded_sub = _expand_native(step.subworkflow, ctx)
        elif step.content_id and _is_resolvable_url(step.content_id):
            resolved = ctx.resolve_url(step.content_id)
            child_ctx = ctx.child(step.content_id)
            normalized = _ensure_native(resolved, ctx.options)
            expanded_sub = _expand_native(normalized, child_ctx)

        step_data = step.model_dump(by_alias=True, exclude={"subworkflow"})
        if expanded_sub is not None:
            step_data.pop("content_id", None)
        expanded_steps[key] = ExpandedNativeStep(**step_data, subworkflow=expanded_sub)

    # Expand subworkflows dict too
    expanded_subworkflows: dict[str, ExpandedNativeWorkflow] | None = None
    if wf.subworkflows:
        expanded_subworkflows = {k: _expand_native(v, ctx) for k, v in wf.subworkflows.items()}

    wf_data = wf.model_dump(by_alias=True, exclude={"steps", "subworkflows"})
    return ExpandedNativeWorkflow(**wf_data, steps=expanded_steps, subworkflows=expanded_subworkflows)
