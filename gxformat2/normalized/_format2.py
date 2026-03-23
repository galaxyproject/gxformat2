"""Normalized Format 2 Galaxy workflow models.

These models narrow the flexible union types from the auto-generated
``gxformat2.schema.gxformat2`` models.  Steps, inputs, outputs, and
comments are always lists (never dicts).  String shorthands are expanded.
All step/input ids are populated.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gxformat2.schema.gxformat2 import (
    GalaxyType,
    GalaxyWorkflow,
    Report,
    StepPosition,
    ToolShedRepository,
    WorkflowComment,
    WorkflowInputParameter,
    WorkflowOutputParameter,
    WorkflowStep,
    WorkflowStepInput,
    WorkflowStepOutput,
    WorkflowStepType,
)


class NormalizedWorkflowStep(BaseModel):
    """A Format 2 workflow step with all union types resolved to their
    canonical list form and ids guaranteed populated."""

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    id: str = Field(description="Step identifier — always populated.")
    label: str | None = Field(default=None)
    doc: str | None = Field(default=None, description="Annotation, joined if originally a list.")
    type_: WorkflowStepType | None = Field(default=None, alias="type")
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
    run: Any = Field(
        default=None,
        description="Inline subworkflow (NormalizedFormat2), unresolved reference (str/dict), or absent.",
    )


class NormalizedFormat2(BaseModel):
    """A Format 2 Galaxy workflow with all union types resolved.

    Steps, inputs, outputs, and comments are always lists.
    Input shorthands are expanded to full WorkflowInputParameter instances.
    Step ids are always populated.
    """

    model_config = ConfigDict(populate_by_name=True, extra="allow")

    label: str | None = Field(default=None)
    doc: str | None = Field(default=None, description="Annotation, joined if originally a list.")
    inputs: list[WorkflowInputParameter] = Field(
        default_factory=list, description="Always a list, shorthands expanded."
    )
    outputs: list[WorkflowOutputParameter] = Field(default_factory=list, description="Always a list.")
    steps: list[NormalizedWorkflowStep] = Field(default_factory=list, description="Always a list, ids populated.")
    comments: list[WorkflowComment] = Field(default_factory=list, description="Always a list.")
    report: Report | None = Field(default=None)
    tags: list[str] = Field(default_factory=list)
    creator: list[dict[str, Any]] | None = Field(default=None)
    license: str | None = Field(default=None)
    release: str | None = Field(default=None)
    uuid: str | None = Field(default=None)


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
        # Ensure required fields have defaults for lenient parsing
        if "inputs" not in workflow:
            workflow = {**workflow, "inputs": {}}
        if "outputs" not in workflow:
            workflow = {**workflow, "outputs": {}}
        if "steps" not in workflow:
            workflow = {**workflow, "steps": {}}
        workflow = GalaxyWorkflow.model_validate(workflow)
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


def _normalize_inputs(
    inputs: list[WorkflowInputParameter] | dict[str, WorkflowInputParameter | str] | dict[str, Any],
) -> list[WorkflowInputParameter]:
    if isinstance(inputs, list):
        result = []
        for inp in inputs:
            if isinstance(inp, WorkflowInputParameter):
                result.append(inp)
            else:
                result.append(WorkflowInputParameter.model_validate(inp))
        return result

    # Dict form — keys are ids, values are WorkflowInputParameter, type string, or dict
    result = []
    for key, value in inputs.items():
        if isinstance(value, str):
            # Shorthand: input_name: "data"
            result.append(
                WorkflowInputParameter(id=key, type_=GalaxyType(value) if value in GalaxyType.__members__ else None)
            )
        elif isinstance(value, WorkflowInputParameter):
            if value.id is None:
                value = value.model_copy(update={"id": key})
            result.append(value)
        elif isinstance(value, dict):
            if "id" not in value:
                value = {**value, "id": key}
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
                step_list.append(step)
            elif isinstance(step, dict):
                if "id" not in step:
                    step = {**step, "id": key}
                step_list.append(WorkflowStep.model_validate(step))
            else:
                step_list.append(WorkflowStep.model_validate({"id": key}))
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


def _normalize_step(step: WorkflowStep) -> NormalizedWorkflowStep:
    in_list = _normalize_step_inputs(step.in_)
    out_list = _normalize_step_outputs(step.out)

    run: NormalizedFormat2 | str | dict[str, Any] | None = None
    if isinstance(step.run, GalaxyWorkflow):
        run = _normalize_workflow(step.run)
    elif step.run is not None:
        # Unresolved reference (URL string, @import dict) — pass through
        run = step.run

    return NormalizedWorkflowStep(
        id=step.id or "0",
        label=step.label,
        doc=_join_doc(step.doc),
        type_=step.type_,
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
        in_=in_list,
        out=out_list,
        run=run,
    )


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


def _normalize_comments(
    comments: list[WorkflowComment] | dict[str, WorkflowComment] | None,
) -> list[WorkflowComment]:
    if comments is None:
        return []
    if isinstance(comments, list):
        return comments

    result = []
    for key, comment in comments.items():
        if isinstance(comment, WorkflowComment):
            if comment.label is None:
                comment = comment.model_copy(update={"label": key})
            result.append(comment)
        elif isinstance(comment, dict):
            if "label" not in comment:
                comment = {**comment, "label": key}
            result.append(WorkflowComment.model_validate(comment))
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
            ref_id = run[1:]
            if ref_id not in lookup:
                raise Exception(f"$graph reference '{run}' not found in graph entries")
            resolved = copy.deepcopy(lookup[ref_id])
            _inline_graph_refs(resolved, lookup)
            step["run"] = resolved
