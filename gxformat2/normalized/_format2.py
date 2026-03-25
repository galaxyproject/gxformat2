"""Normalized Format 2 Galaxy workflow models.

These models narrow the flexible union types from the auto-generated
``gxformat2.schema.gxformat2`` models.  Steps, inputs, outputs, and
comments are always lists (never dicts).  String shorthands are expanded.
All step/input ids are populated.
"""

from __future__ import annotations

import copy
from functools import cached_property
from pathlib import Path
from typing import Any, Literal, NamedTuple, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing_extensions import TypeAlias

from gxformat2.schema.gxformat2 import (
    CreatorOrganization,
    CreatorPerson,
    FrameComment,
    FreehandComment,
    GalaxyWorkflow,
    MarkdownComment,
    Report,
    StepPosition,
    TextComment,
    ToolShedRepository,
    WorkflowInputParameter,
    WorkflowOutputParameter,
    WorkflowStep,
    WorkflowStepInput,
    WorkflowStepOutput,
    WorkflowStepType,
)


class GalaxyUserToolStub(BaseModel):
    """Stub marker for a user-defined Galaxy tool in the normalized tree.

    Carries enough to discriminate (class: GalaxyUserTool) and preserves
    all other fields as extras. The full tool definition is opaque at this level.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    class_: Literal["GalaxyUserTool"] = Field(alias="class")
    name: str | None = Field(default=None)


class ImportReference(BaseModel):
    """Stub marker for an unresolved @import in the normalized tree.

    Present only before expansion — resolved into inline
    ExpandedFormat2 subworkflows during expansion.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    import_path: str = Field(alias="@import")


class SourceReference(NamedTuple):
    """A parsed Format2 source reference (e.g. ``step_label/output_name``)."""

    step_label: str
    output_name: str


def resolve_source_reference(value: str, known_labels: set | dict) -> SourceReference:
    """Parse a source reference into (step_label_or_id, output_name).

    Tries matching known labels first to handle labels containing '/'.
    Falls back to split on '/' for numeric step IDs or unknown labels.
    """
    for label in sorted(known_labels, key=len, reverse=True):
        if value == label:
            return SourceReference(label, "output")
        if value.startswith(label + "/"):
            return SourceReference(label, value[len(label) + 1 :])
    if "/" in value:
        parts = value.split("/", 1)
        return SourceReference(parts[0], parts[1])
    return SourceReference(value, "output")


class NormalizedWorkflowStep(BaseModel):
    """A Format 2 workflow step with all union types resolved to canonical list form.

    Ids are guaranteed populated.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str = Field(description="Step identifier — always populated.")
    label: str | None = Field(default=None)
    doc: str | None = Field(default=None, description="Annotation, joined if originally a list.")
    type_: WorkflowStepType = Field(default=WorkflowStepType.tool, alias="type")
    tool_id: str | None = Field(default=None)
    tool_version: str | None = Field(default=None)
    tool_shed_repository: ToolShedRepository | None = Field(default=None)
    position: StepPosition | None = Field(default=None)
    when: str | None = Field(default=None)
    state: dict[str, Any] | None = Field(default=None)
    tool_state: str | dict[str, Any] | None = Field(default=None)
    runtime_inputs: list[str] | None = Field(default=None)
    errors: str | None = Field(default=None)
    uuid: str | None = Field(default=None)
    in_: list[WorkflowStepInput] = Field(
        default_factory=list, alias="in", description="Always a list, shorthands expanded."
    )
    out: list[WorkflowStepOutput] = Field(default_factory=list, description="Always a list, shorthands expanded.")
    run: NormalizedFormat2 | GalaxyUserToolStub | ImportReference | str | None = Field(default=None)

    @field_validator("run", mode="before")
    @classmethod
    def _preserve_run_type(cls, v: Any) -> Any:
        """Prevent pydantic from auto-coercing dicts into NormalizedFormat2."""
        if isinstance(v, dict):
            if "@import" in v:
                return ImportReference.model_validate(v)
            if v.get("class") == "GalaxyUserTool":
                return GalaxyUserToolStub.model_validate(v)
        return v

    @property
    def is_tool_step(self) -> bool:
        return self.type_ == WorkflowStepType.tool

    @property
    def is_subworkflow_step(self) -> bool:
        return self.type_ == WorkflowStepType.subworkflow

    @property
    def is_pause_step(self) -> bool:
        return self.type_ == WorkflowStepType.pause

    @property
    def is_pick_value_step(self) -> bool:
        return self.type_ == WorkflowStepType.pick_value


class NormalizedFormat2(BaseModel):
    """A Format 2 Galaxy workflow with all union types resolved.

    Steps, inputs, outputs, and comments are always lists.
    Input shorthands are expanded to full WorkflowInputParameter instances.
    Step ids are always populated.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    class_: Literal["GalaxyWorkflow"] = Field(default="GalaxyWorkflow", alias="class")
    label: str | None = Field(default=None)
    doc: str | None = Field(default=None, description="Annotation, joined if originally a list.")
    inputs: list[WorkflowInputParameter] = Field(
        default_factory=list, description="Always a list, shorthands expanded."
    )
    outputs: list[WorkflowOutputParameter] = Field(default_factory=list, description="Always a list.")
    steps: list[NormalizedWorkflowStep] = Field(default_factory=list, description="Always a list, ids populated.")
    comments: list[TextComment | MarkdownComment | FrameComment | FreehandComment] = Field(
        default_factory=list, description="Always a list of typed comments."
    )
    report: Report | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    creator: list[CreatorPerson | CreatorOrganization] | None = Field(default=None)
    license: str | None = Field(default=None)
    release: str | None = Field(default=None)
    uuid: str | None = Field(default=None)

    @cached_property
    def known_labels(self) -> set[str]:
        """All step and input labels/ids in this workflow."""
        labels = {s.label or s.id for s in self.steps}
        labels |= {i.id for i in self.inputs if i.id}
        return labels

    def resolve_source(self, source: str) -> SourceReference:
        """Parse a source reference string (e.g. ``step/output``) against this workflow's labels."""
        return resolve_source_reference(source, self.known_labels)


NormalizedWorkflowStep.model_rebuild()
NormalizedFormat2.model_rebuild()


def normalized_format2(
    workflow: dict[str, Any] | str | Path | GalaxyWorkflow,
) -> NormalizedFormat2:
    """Normalize a Format 2 Galaxy workflow into a fully typed model.

    Accepts a raw dict, a YAML/JSON file path, a ``GalaxyWorkflow``
    model, or a native workflow dict (auto-detected by
    ``a_galaxy_workflow`` key and converted via ``from_galaxy_native``).

    Handles ``$graph`` multi-workflow documents by extracting the
    ``main`` workflow and inlining ``#ref`` subworkflow references.

    Returns a ``NormalizedFormat2`` where steps/inputs/outputs are always
    lists, shorthands are expanded, and ids are populated.
    """
    if isinstance(workflow, (str, Path)):
        from gxformat2.yaml import ordered_load_path

        workflow = ordered_load_path(str(workflow))
    if isinstance(workflow, dict):
        if workflow.get("a_galaxy_workflow") == "true":
            from gxformat2.export import from_galaxy_native

            workflow = from_galaxy_native(workflow)
        elif "$graph" in workflow and "class" not in workflow:
            workflow = _resolve_graph(workflow)
        assert isinstance(workflow, dict)
        # Migrate legacy 'name' to 'label'
        if "name" in workflow and "label" not in workflow:
            workflow = {**workflow, "label": workflow["name"]}
        # Ensure required fields have defaults for lenient parsing
        if "inputs" not in workflow:
            workflow = {**workflow, "inputs": {}}
        if "outputs" not in workflow:
            workflow = {**workflow, "outputs": {}}
        if "steps" not in workflow:
            workflow = {**workflow, "steps": {}}
        workflow = _pre_clean_steps(workflow)
        workflow = GalaxyWorkflow.model_validate(workflow)
    assert isinstance(workflow, GalaxyWorkflow)
    return _normalize_workflow(workflow)


def _normalize_workflow(wf: GalaxyWorkflow) -> NormalizedFormat2:
    inputs = _normalize_inputs(wf.inputs)
    outputs = _normalize_outputs(wf.outputs)
    steps = _normalize_steps(wf.steps, inputs_offset=len(inputs))
    comments = _normalize_comments(wf.comments)
    doc = _join_doc(wf.doc)

    return NormalizedFormat2(
        label=wf.label,
        doc=doc,
        inputs=inputs,
        outputs=outputs,
        steps=steps,
        comments=comments,
        report=wf.report,
        tags=wf.tags or [],
        creator=wf.creator,
        license=wf.license,
        release=wf.release,
        uuid=wf.uuid,
    )


def _join_doc(doc: str | list[str] | None) -> str | None:
    if doc is None:
        return None
    if isinstance(doc, list):
        return "\n".join(doc) if doc else None
    return doc


INPUT_TYPE_ALIASES = {
    "File": "data",
    "data_input": "data",
    "data_collection": "collection",
    "data_collection_input": "collection",
}


def _normalize_input_type(value: Any) -> Any:
    """Normalize input type aliases to canonical Format2 types."""
    if isinstance(value, str):
        return INPUT_TYPE_ALIASES.get(value, value)
    if isinstance(value, list):
        return [_normalize_input_type(v) for v in value]
    return value


def _normalize_inputs(
    inputs: list[WorkflowInputParameter] | dict[str, WorkflowInputParameter | str] | dict[str, Any],
) -> list[WorkflowInputParameter]:
    if isinstance(inputs, list):
        result = []
        for inp in inputs:
            if isinstance(inp, WorkflowInputParameter):
                result.append(inp)
            elif isinstance(inp, dict):
                if "type" in inp:
                    inp = {**inp, "type": _normalize_input_type(inp["type"])}
                result.append(WorkflowInputParameter.model_validate(inp))
            else:
                result.append(WorkflowInputParameter.model_validate(inp))
        return result

    # Dict form — keys are ids, values are WorkflowInputParameter, type string, or dict
    result = []
    for key, value in inputs.items():
        if isinstance(value, str):
            # Shorthand: input_name: "data"
            normalized_type = _normalize_input_type(value)
            result.append(WorkflowInputParameter.model_validate({"id": key, "type": normalized_type}))
        elif isinstance(value, WorkflowInputParameter):
            if value.id is None:
                value = value.model_copy(update={"id": key})
            result.append(value)
        elif isinstance(value, dict):
            if "id" not in value:
                value = {**value, "id": key}
            if "type" in value:
                value = {**value, "type": _normalize_input_type(value["type"])}
            if "format" in value and isinstance(value["format"], str):
                value = {**value, "format": [value["format"]]}
            result.append(WorkflowInputParameter.model_validate(value))
        else:
            result.append(WorkflowInputParameter(id=key))
    return result


def _normalize_outputs(
    outputs: list[WorkflowOutputParameter] | dict[str, WorkflowOutputParameter | str] | dict[str, Any],
) -> list[WorkflowOutputParameter]:
    if isinstance(outputs, list):
        result = []
        for out in outputs:
            if isinstance(out, WorkflowOutputParameter):
                result.append(out)
            else:
                result.append(WorkflowOutputParameter.model_validate(out))
        return result

    result = []
    for key, value in outputs.items():
        if isinstance(value, WorkflowOutputParameter):
            if value.id is None:
                value = value.model_copy(update={"id": key})
            result.append(value)
        elif isinstance(value, dict):
            if "id" not in value:
                value = {**value, "id": key}
            result.append(WorkflowOutputParameter.model_validate(value))
        else:
            result.append(WorkflowOutputParameter(id=key))
    return result


def _pre_clean_steps(workflow: dict[str, Any]) -> dict[str, Any]:
    """Resolve ``$link`` entries in step state dicts before model validation.

    ``$link`` in ``state`` is a Format2 shorthand for connections embedded in
    tool state.  This replaces them with ConnectedValue markers and adds the
    connection source to ``in``, so the model layer sees only schema-compliant data.
    """
    steps = workflow.get("steps", {})
    if isinstance(steps, dict):
        cleaned = {k: _pre_clean_step(v) if isinstance(v, dict) else v for k, v in steps.items()}
    elif isinstance(steps, list):
        cleaned = [_pre_clean_step(s) if isinstance(s, dict) else s for s in steps]
    else:
        return workflow
    return {**workflow, "steps": cleaned}


def _pre_clean_step(step: dict[str, Any]) -> dict[str, Any]:
    """Resolve $link in state on a single step dict."""
    state = step.get("state")
    if not isinstance(state, dict):
        # Recursively clean subworkflow runs even if no state
        run = step.get("run")
        if isinstance(run, dict) and run.get("class") == "GalaxyWorkflow":
            return {**step, "run": _pre_clean_steps(run)}
        return step

    step = dict(step)
    clean_state, link_connections = _resolve_links(state)
    step["state"] = clean_state

    if link_connections:
        in_val = step.get("in")
        if isinstance(in_val, list):
            extra = [{"id": k, "source": srcs if len(srcs) > 1 else srcs[0]} for k, srcs in link_connections.items()]
            step["in"] = in_val + extra
        else:
            in_dict = dict(in_val) if isinstance(in_val, dict) else {}
            for key, sources in link_connections.items():
                source = sources if len(sources) > 1 else sources[0]
                in_dict[key] = {"source": source} if isinstance(source, list) else source
            step["in"] = in_dict

    # Recursively clean subworkflow runs
    run = step.get("run")
    if isinstance(run, dict) and run.get("class") == "GalaxyWorkflow":
        step["run"] = _pre_clean_steps(run)

    return step


def _normalize_steps(
    steps: list[WorkflowStep] | dict[str, WorkflowStep],
    inputs_offset: int = 0,
) -> list[NormalizedWorkflowStep]:
    if isinstance(steps, dict):
        step_list = []
        for key, step in steps.items():
            if isinstance(step, WorkflowStep):
                if step.id is None:
                    step = step.model_copy(update={"id": key})
                if step.label is None:
                    step = step.model_copy(update={"label": key})
                step_list.append(step)
            elif isinstance(step, dict):
                if "id" not in step:
                    step = {**step, "id": key}
                if "label" not in step:
                    step = {**step, "label": key}
                step_list.append(WorkflowStep.model_validate(step))
            else:
                step_list.append(WorkflowStep.model_validate({"id": key, "label": key}))
    else:
        step_list = []
        for i, step in enumerate(steps):
            if isinstance(step, WorkflowStep):
                if step.id is None:
                    step = step.model_copy(update={"id": str(i + inputs_offset)})
                step_list.append(step)
            elif isinstance(step, dict):
                if "id" not in step:
                    step = {**step, "id": str(i + inputs_offset)}
                step_list.append(WorkflowStep.model_validate(step))
            else:
                step_list.append(step)

    return [_normalize_step(s) for s in step_list]


_CONNECTED_VALUE = {"__class__": "ConnectedValue"}


def _normalize_step(step: WorkflowStep) -> NormalizedWorkflowStep:
    in_list = _normalize_step_inputs(step.in_)
    out_list = _normalize_step_outputs(step.out)

    run: NormalizedFormat2 | GalaxyUserToolStub | ImportReference | str | None = None
    if isinstance(step.run, GalaxyWorkflow):
        run = _normalize_workflow(step.run)
    elif isinstance(step.run, dict):
        if "@import" in step.run:
            run = ImportReference.model_validate(step.run)
        elif step.run.get("class") == "GalaxyUserTool":
            run = GalaxyUserToolStub.model_validate(step.run)
        else:
            run = normalized_format2(step.run)
    elif isinstance(step.run, str):
        run = step.run

    # Infer type when not explicitly set
    step_type = step.type_
    if step_type is None:
        if isinstance(run, (NormalizedFormat2, ImportReference, str)):
            step_type = WorkflowStepType.subworkflow
        elif isinstance(run, GalaxyUserToolStub):
            step_type = WorkflowStepType.tool
        else:
            step_type = WorkflowStepType.tool

    return NormalizedWorkflowStep(
        id=step.id or "0",
        label=step.label,
        doc=_join_doc(step.doc),
        type_=step_type,
        in_=in_list,
        tool_id=step.tool_id,
        tool_version=step.tool_version,
        tool_shed_repository=step.tool_shed_repository,
        position=step.position,
        when=step.when,
        state=step.state,
        tool_state=step.tool_state,
        runtime_inputs=step.runtime_inputs,
        errors=step.errors,
        uuid=step.uuid,
        out=out_list,
        run=run,
    )


def _resolve_links(
    value: Any,
    key: str = "",
    connections: dict[str, list[str]] | None = None,
) -> tuple[Any, dict[str, list[str]]]:
    """Walk state dict, replacing $link with ConnectedValue and collecting connections.

    Returns (clean_value, connections) where connections maps pipe-separated
    state paths to source references.
    """
    if connections is None:
        connections = {}

    if isinstance(value, dict) and "$link" in value:
        link_value = value["$link"]
        connections.setdefault(key, []).append(link_value)
        return dict(_CONNECTED_VALUE), connections

    if isinstance(value, dict):
        new_dict: dict[str, Any] = {}
        for k, v in value.items():
            child_key = f"{key}|{k}" if key else k
            new_dict[k], connections = _resolve_links(v, child_key, connections)
        return new_dict, connections

    if isinstance(value, list):
        new_list: list[Any] = []
        for i, v in enumerate(value):
            if isinstance(v, dict) and "$link" in v:
                link_value = v["$link"]
                connections.setdefault(key, []).append(link_value)
                new_list.append(None)
            else:
                child_key = f"{key}_{i}"
                resolved, connections = _resolve_links(v, child_key, connections)
                new_list.append(resolved)
        return new_list, connections

    return value, connections


def _normalize_step_inputs(
    in_: list[WorkflowStepInput] | dict[str, WorkflowStepInput | str] | None,
) -> list[WorkflowStepInput]:
    if in_ is None:
        return []
    if isinstance(in_, list):
        return [i if isinstance(i, WorkflowStepInput) else WorkflowStepInput.model_validate(i) for i in in_]

    result = []
    for key, value in in_.items():
        if isinstance(value, str):
            # Shorthand: input_name: "source_step/output"
            result.append(WorkflowStepInput(id=key, source=value))
        elif isinstance(value, WorkflowStepInput):
            if value.id is None:
                value = value.model_copy(update={"id": key})
            result.append(value)
        elif isinstance(value, dict):
            if "id" not in value:
                value = {**value, "id": key}
            result.append(WorkflowStepInput.model_validate(value))
        else:
            result.append(WorkflowStepInput(id=key))
    return result


def _normalize_step_outputs(
    out: list[WorkflowStepOutput | str] | dict[str, WorkflowStepOutput | str] | None,
) -> list[WorkflowStepOutput]:
    if out is None:
        return []
    if isinstance(out, list):
        result = []
        for item in out:
            if isinstance(item, str):
                result.append(WorkflowStepOutput(id=item))
            elif isinstance(item, WorkflowStepOutput):
                result.append(item)
            elif isinstance(item, dict):
                result.append(WorkflowStepOutput.model_validate(item))
            else:
                result.append(item)
        return result

    result = []
    for key, value in out.items():
        if isinstance(value, str):
            result.append(WorkflowStepOutput(id=key))
        elif isinstance(value, WorkflowStepOutput):
            if value.id is None:
                value = value.model_copy(update={"id": key})
            result.append(value)
        elif isinstance(value, dict):
            if "id" not in value:
                value = {**value, "id": key}
            result.append(WorkflowStepOutput.model_validate(value))
        else:
            result.append(WorkflowStepOutput(id=key))
    return result


_COMMENT_TYPE_MAP = {
    "text": TextComment,
    "markdown": MarkdownComment,
    "frame": FrameComment,
    "freehand": FreehandComment,
}


Format2Comment: TypeAlias = Union[TextComment, MarkdownComment, FrameComment, FreehandComment]


def _normalize_comments(
    comments: list[Format2Comment] | dict[str, Format2Comment] | None,
) -> list[Format2Comment]:
    if comments is None:
        return []
    if isinstance(comments, list):
        return list(comments)

    result: list[Format2Comment] = []
    for key, comment in comments.items():
        if isinstance(comment, (TextComment, MarkdownComment, FrameComment, FreehandComment)):
            if comment.label is None:
                comment = comment.model_copy(update={"label": key})
            result.append(comment)
        elif isinstance(comment, dict):
            if "label" not in comment:
                comment = {**comment, "label": key}
            comment_type = comment.get("type", "text")
            model_class = _COMMENT_TYPE_MAP.get(comment_type, TextComment)
            result.append(model_class.model_validate(comment))
        else:
            result.append(comment)
    return result


def _resolve_graph(raw: dict[str, Any]) -> dict[str, Any]:
    """Extract main workflow from a ``$graph`` document and inline ``#ref`` subworkflows.

    A ``$graph`` document contains multiple workflows as a list under the
    ``$graph`` key.  The workflow with ``id: main`` is the primary workflow.
    Steps with ``run: '#subworkflow_id'`` are resolved by inlining the
    referenced subworkflow from the same ``$graph``.
    """
    graph = raw["$graph"]
    lookup: dict[str, dict[str, Any]] = {}
    main: dict[str, Any] | None = None
    for entry in graph:
        if not isinstance(entry, dict):
            raise Exception("Malformed workflow content in $graph")
        if "id" not in entry:
            raise Exception("No subworkflow ID found for entry in $graph.")
        graph_id = entry["id"]
        lookup[graph_id] = entry
        if graph_id == "main":
            main = entry
    if main is None:
        raise Exception("$graph has no 'main' workflow")
    main = copy.deepcopy(main)
    _inline_graph_refs(main, lookup)
    return main


def _is_graph_id_reference(run_action: Any) -> bool:
    """Check if a ``run`` value is a ``$graph`` reference (e.g. ``'#subworkflow1'``)."""
    return isinstance(run_action, str) and run_action.startswith("#")


def _inline_graph_refs(workflow: dict[str, Any], lookup: dict[str, dict[str, Any]]) -> None:
    """Recursively replace ``#ref`` run values with the referenced subworkflow."""
    steps = workflow.get("steps", {})
    step_iter = steps.values() if isinstance(steps, dict) else steps
    for step in step_iter:
        if not isinstance(step, dict):
            continue
        run = step.get("run")
        if _is_graph_id_reference(run):
            assert isinstance(run, str)
            ref_id = run[1:]
            if ref_id not in lookup:
                raise Exception(f"$graph reference '{run}' not found in graph entries")
            resolved = copy.deepcopy(lookup[ref_id])
            _inline_graph_refs(resolved, lookup)
            step["run"] = resolved
