"""Normalized native Galaxy workflow models.

These models narrow the loose types from the auto-generated
``gxformat2.schema.native`` models into a form where every optional
container is guaranteed non-None, tool_state is always a parsed dict,
and subworkflows are recursively normalized.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Annotated, Any, Union

from pydantic import BaseModel, ConfigDict, Discriminator, Field, field_validator, Tag
from typing_extensions import TypeAlias

from gxformat2.schema.native import (
    _discriminate_comments,
    _discriminate_creator,
    CreatorOrganization,
    CreatorPerson,
    NativeFrameComment,
    NativeFreehandComment,
    NativeGalaxyWorkflow,
    NativeInputConnection,
    NativeMarkdownComment,
    NativePostJobAction,
    NativeReport,
    NativeSourceMetadata,
    NativeStep,
    NativeStepInput,
    NativeStepOutput,
    NativeStepType,
    NativeTextComment,
    NativeWorkflowOutput,
    StepPosition,
    ToolShedRepository,
)

from ._types import ToolReference

NativeComment: TypeAlias = Annotated[
    Union[
        Annotated[NativeTextComment, Tag("NativeTextComment")],
        Annotated[NativeMarkdownComment, Tag("NativeMarkdownComment")],
        Annotated[NativeFrameComment, Tag("NativeFrameComment")],
        Annotated[NativeFreehandComment, Tag("NativeFreehandComment")],
    ],
    Discriminator(_discriminate_comments),
]

NativeCreator: TypeAlias = Annotated[
    Union[
        Annotated[CreatorPerson, Tag("CreatorPerson")],
        Annotated[CreatorOrganization, Tag("CreatorOrganization")],
    ],
    Discriminator(_discriminate_creator),
]


class _DictMixin:
    """Shared serialization for normalized models.

    Mixed into BaseModel subclasses — model_dump is provided by Pydantic.
    """

    def to_dict(self: Any) -> dict[str, Any]:
        """Serialize to a JSON/YAML-compatible dict."""
        return self.model_dump(by_alias=True, exclude_none=True, mode="json")


class NormalizedNativeStep(_DictMixin, BaseModel):
    """A native workflow step with optional containers resolved to empty defaults.

    tool_state is guaranteed to be a parsed dict.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: int = Field(description="Step ID.")
    name: str | None = Field(default=None)
    type_: NativeStepType = Field(default=NativeStepType.tool, alias="type")
    label: str | None = Field(default=None)
    annotation: str | None = Field(default=None)
    when: str | None = Field(default=None)
    content_id: str | None = Field(default=None)
    content_source: str | None = Field(default=None)
    tool_state: dict[str, Any] = Field(default_factory=dict, description="Always a parsed dict, never a JSON string.")
    tool_id: str | None = Field(default=None)
    tool_version: str | None = Field(default=None)
    tool_shed_repository: ToolShedRepository | None = Field(default=None)
    tool_uuid: str | None = Field(default=None)
    uuid: str | None = Field(default=None)
    errors: str | None = Field(default=None)
    position: StepPosition | None = Field(default=None)
    input_connections: dict[str, list[NativeInputConnection]] = Field(default_factory=dict)

    @field_validator("input_connections", mode="before")
    @classmethod
    def _normalize_connections(cls, v):
        if isinstance(v, dict):
            return {k: val if isinstance(val, list) else [val] for k, val in v.items()}
        return v

    inputs: list[NativeStepInput] = Field(default_factory=list)
    outputs: list[NativeStepOutput] = Field(default_factory=list)
    workflow_outputs: list[NativeWorkflowOutput] = Field(default_factory=list)
    post_job_actions: dict[str, NativePostJobAction] = Field(default_factory=dict)
    subworkflow: NormalizedNativeWorkflow | None = Field(default=None)
    tool_representation: dict[str, Any] | None = Field(default=None)
    in_: dict[str, Any] | None = Field(default=None, alias="in")

    @property
    def is_tool_step(self) -> bool:
        return self.type_ == NativeStepType.tool

    @property
    def is_subworkflow_step(self) -> bool:
        return self.type_ == NativeStepType.subworkflow

    @property
    def is_input_step(self) -> bool:
        return self.type_ in (
            NativeStepType.data_input,
            NativeStepType.data_collection_input,
            NativeStepType.parameter_input,
        )

    @property
    def is_pause_step(self) -> bool:
        return self.type_ == NativeStepType.pause

    @property
    def is_pick_value_step(self) -> bool:
        return self.type_ == NativeStepType.pick_value

    @property
    def connected_paths(self) -> frozenset[str]:
        """State paths that have incoming connections."""
        return frozenset(self.input_connections.keys())


class NormalizedNativeWorkflow(_DictMixin, BaseModel):
    """A native Galaxy workflow with optional containers resolved to empty defaults.

    Steps contain NormalizedNativeStep instances.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    name: str | None = Field(default=None)
    a_galaxy_workflow: str = Field(default="true")
    format_version: str = Field(default="0.1", alias="format-version")
    annotation: str | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    version: int | None = Field(default=None)
    license: str | None = Field(default=None)
    release: str | None = Field(default=None)
    uuid: str | None = Field(default=None)
    creator: list[NativeCreator] | None = Field(default=None)
    report: NativeReport | None = Field(default=None)
    readme: str | None = Field(default=None)
    help: str | None = Field(default=None)
    logo_url: str | None = Field(default=None)
    doi: list[str] | None = Field(default=None)
    source_metadata: NativeSourceMetadata | None = Field(default=None)
    comments: list[NativeComment] = Field(default_factory=list)
    steps: dict[str, NormalizedNativeStep] = Field(default_factory=dict)
    subworkflows: dict[str, NormalizedNativeWorkflow] | None = Field(default=None)

    @property
    def unique_tools(self) -> frozenset[ToolReference]:
        """All unique (tool_id, tool_version) pairs in this workflow and its inline subworkflows."""
        tools: set[ToolReference] = set()
        self._collect_tools(tools)
        return frozenset(tools)

    def _collect_tools(self, into: set[ToolReference]) -> None:
        for step in self.steps.values():
            if step.tool_id is not None:
                into.add(ToolReference(step.tool_id, step.tool_version))
            if step.subworkflow is not None:
                step.subworkflow._collect_tools(into)


NormalizedNativeStep.model_rebuild()
NormalizedNativeWorkflow.model_rebuild()


def load_native(data: dict[str, Any], *, strict: bool = True) -> NativeGalaxyWorkflow:
    """Load a native Galaxy workflow dict into a :class:`NativeGalaxyWorkflow`.

    Parameters
    ----------
    data:
        Raw workflow dict (e.g. parsed from a ``.ga`` JSON file).
    strict:
        When *True* (default) the dict is validated as-is. When *False*,
        known Galaxy serialization quirks are normalized before validation
        (e.g. ``tags: ""`` -> ``tags: []``).
    """
    if not strict:
        data = _normalize_native_for_validation(data)
    return NativeGalaxyWorkflow.model_validate(data)


def _normalize_native_for_validation(data: dict[str, Any]) -> dict[str, Any]:
    """Fix known Galaxy serialization quirks in a native workflow dict."""
    data = data.copy()
    _normalize_tags(data)
    if "steps" in data and isinstance(data["steps"], dict):
        steps: dict[str, Any] = {}
        for key, step in data["steps"].items():
            if isinstance(step, dict):
                step = _normalize_step_for_validation(step)
            steps[key] = step
        data["steps"] = steps
    return data


def _normalize_step_for_validation(step: dict[str, Any]) -> dict[str, Any]:
    """Normalize a single step dict."""
    step = step.copy()
    if step.get("subworkflow") and isinstance(step["subworkflow"], dict):
        step["subworkflow"] = _normalize_native_for_validation(step["subworkflow"])
    _normalize_post_job_actions(step)
    return step


def _normalize_post_job_actions(step: dict[str, Any]) -> None:
    """Fix post_job_actions where action_arguments is a scalar instead of dict."""
    pjas = step.get("post_job_actions")
    if not isinstance(pjas, dict):
        return
    normalized = {}
    for key, pja in pjas.items():
        if isinstance(pja, dict):
            args = pja.get("action_arguments")
            if args is not None and not isinstance(args, dict):
                pja = pja.copy()
                pja["action_arguments"] = None
            normalized[key] = pja
        else:
            normalized[key] = pja
    step["post_job_actions"] = normalized


def _normalize_tags(data: dict[str, Any]) -> None:
    """Normalize ``tags`` field in-place on *data*.

    Galaxy sometimes serializes tags as an empty string ``""`` or as a
    comma-separated string instead of a list.
    """
    tags = data.get("tags")
    if isinstance(tags, str):
        data["tags"] = [t.strip() for t in tags.split(",") if t.strip()] if tags else []


def normalized_native(
    workflow: dict[str, Any] | str | Path | os.PathLike[str] | NativeGalaxyWorkflow,
) -> NormalizedNativeWorkflow:
    """Normalize a native Galaxy workflow into a fully typed model.

    Accepts a raw dict, a file path, or an already-parsed
    ``NativeGalaxyWorkflow``.  Returns a ``NormalizedNativeWorkflow``
    where tool_state is always a dict, and all optional containers are
    resolved to empty defaults.
    """
    if isinstance(workflow, (str, Path)):
        with open(workflow) as f:
            workflow = json.load(f)
    if isinstance(workflow, dict):
        workflow = load_native(workflow, strict=False)
    assert isinstance(workflow, NativeGalaxyWorkflow)
    return _normalize_workflow(workflow)


def _normalize_workflow(wf: NativeGalaxyWorkflow) -> NormalizedNativeWorkflow:
    steps: dict[str, NormalizedNativeStep] = {}
    for key, step in (wf.steps or {}).items():
        steps[key] = _normalize_step(step)

    subworkflows: dict[str, NormalizedNativeWorkflow] | None = None
    if wf.subworkflows:
        subworkflows = {k: _normalize_workflow(v) for k, v in wf.subworkflows.items()}

    return NormalizedNativeWorkflow(
        name=wf.name,
        a_galaxy_workflow=wf.a_galaxy_workflow,
        format_version=wf.format_version,
        annotation=wf.annotation,
        tags=wf.tags or [],
        version=wf.version,
        license=wf.license,
        release=wf.release,
        uuid=wf.uuid,
        creator=wf.creator,
        report=wf.report,
        readme=wf.readme,
        help=wf.help,
        logo_url=wf.logo_url,
        doi=wf.doi,
        source_metadata=wf.source_metadata,
        comments=list(wf.comments) if wf.comments else [],
        steps=steps,
        subworkflows=subworkflows,
    )


def _normalize_position(position: StepPosition | None) -> StepPosition | None:
    """Strip legacy extra fields (bottom, height, right, width, x, y) from step positions."""
    if position is None:
        return None
    return StepPosition(top=position.top, left=position.left)


def _normalize_step(step: NativeStep) -> NormalizedNativeStep:
    tool_state: dict[str, Any]
    if isinstance(step.tool_state, str):
        tool_state = json.loads(step.tool_state)
    elif step.tool_state is not None:
        tool_state = step.tool_state
    else:
        tool_state = {}

    subworkflow: NormalizedNativeWorkflow | None = None
    if step.subworkflow is not None:
        subworkflow = _normalize_workflow(step.subworkflow)

    return NormalizedNativeStep(
        id=step.id or 0,
        name=step.name,
        type_=step.type_ or NativeStepType.tool,
        in_=step.in_,
        label=step.label,
        annotation=step.annotation,
        when=step.when,
        content_id=step.content_id,
        content_source=getattr(step, "content_source", None),
        tool_state=tool_state,
        tool_id=step.tool_id,
        tool_version=step.tool_version,
        tool_shed_repository=step.tool_shed_repository,
        tool_uuid=step.tool_uuid,
        uuid=step.uuid,
        errors=step.errors,
        position=_normalize_position(step.position),
        input_connections={k: v if isinstance(v, list) else [v] for k, v in (step.input_connections or {}).items()},
        inputs=step.inputs or [],
        outputs=step.outputs or [],
        workflow_outputs=step.workflow_outputs or [],
        post_job_actions=step.post_job_actions or {},
        subworkflow=subworkflow,
        tool_representation=step.tool_representation,
    )
