"""Draft workflow (``class: GalaxyWorkflowDraft``) metadata and pure checks.

The schema-salad metaschema cannot currently express a named regex-constrained
string subtype that survives the pydantic and Effect Schema code generators.
Keep the sentinel contract here so downstream tooling has one upstream-owned
definition to mirror.

The checks below back draft validation, "next step" planning, and
concrete-subset extraction. They operate on raw workflow dicts (before
normalization strips ``_plan_*``) and never mutate their input.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Iterator, Mapping
from typing import Annotated, Any, Final, Literal

from pydantic import BaseModel, Field, ValidationError

from gxformat2.normalized._format2 import resolve_source_reference
from gxformat2.schema.gxformat2_draft import GalaxyWorkflowDraft

TODO_SENTINEL_PATTERN: Final[str] = r"^TODO(_[a-zA-Z0-9_]+)?$"
TODO_SENTINEL_RE: Final[re.Pattern[str]] = re.compile(TODO_SENTINEL_PATTERN)
# TODO-shaped strings: flags malformed sentinels (TODO-foo, TODO_) the canonical
# pattern misses, without matching unrelated identifiers like TODOLIST.
TODO_LIKE_RE: Final[re.Pattern[str]] = re.compile(r"^TODO([_-]|$)")

PLAN_FIELDS: Final[tuple[str, ...]] = (
    "_plan_state",
    "_plan_context",
    "_plan_in",
    "_plan_out",
)

DRAFT_CLASS: Final[str] = "GalaxyWorkflowDraft"

StepPath = list[str]


def is_todo_sentinel(value: object) -> bool:
    """Return true if *value* is a draft TODO sentinel string."""
    return isinstance(value, str) and TODO_SENTINEL_RE.fullmatch(value) is not None


def is_draft_workflow(doc: object) -> bool:
    """Return true if *doc* is a workflow dict with ``class: GalaxyWorkflowDraft``."""
    return isinstance(doc, dict) and doc.get("class") == DRAFT_CLASS


# --- Result models ----------------------------------------------------------


class ToolIdLocation(BaseModel):
    """TODO sentinel in a step's ``tool_id``."""

    kind: Literal["tool_id"] = "tool_id"


class ToolVersionLocation(BaseModel):
    """TODO sentinel in a step's ``tool_version``."""

    kind: Literal["tool_version"] = "tool_version"


class InKeyLocation(BaseModel):
    """TODO sentinel used as a step ``in:`` key."""

    kind: Literal["in_key"] = "in_key"
    key: str


class OutIdLocation(BaseModel):
    """TODO sentinel used as a step ``out:`` id."""

    kind: Literal["out_id"] = "out_id"
    id: str


class OutputSourceLocation(BaseModel):
    """TODO sentinel port referenced by a workflow output's ``outputSource``."""

    kind: Literal["output_source"] = "output_source"
    output_label: str
    port: str


StepTodoLocation = ToolIdLocation | ToolVersionLocation | InKeyLocation | OutIdLocation
TodoLocation = Annotated[StepTodoLocation | OutputSourceLocation, Field(discriminator="kind")]


class TodoHit(BaseModel):
    """One TODO sentinel and the step path it was found at."""

    path: StepPath
    location: TodoLocation
    sentinel: str


class PlanHit(BaseModel):
    """One non-empty ``_plan_*`` field and the step path it was found at."""

    path: StepPath
    field: str
    value: str


class DraftSurvey(BaseModel):
    """Every TODO sentinel and ``_plan_*`` field of a draft, with step paths."""

    is_draft: bool
    todos: list[TodoHit] = []
    plan_fields: list[PlanHit] = []


class DraftValidationDiagnostic(BaseModel):
    """A draft validation message; ``path`` is ``[]`` for workflow-level issues."""

    path: StepPath
    message: str


class DraftValidationResult(BaseModel):
    """All draft validation diagnostics, bucketed, plus the draft survey."""

    ok: bool
    structure_errors: list[DraftValidationDiagnostic] = []
    topology_errors: list[DraftValidationDiagnostic] = []
    semantic_errors: list[DraftValidationDiagnostic] = []
    warnings: list[DraftValidationDiagnostic] = []
    survey: DraftSurvey


class NextStepResult(BaseModel):
    """``draft`` is false when no work remains; otherwise ``step`` and ``work`` are set."""

    draft: bool
    step: StepPath | None = None
    work: list[str] | None = None


class StepHasTodoReason(BaseModel):
    """Step dropped because it carries TODO sentinels."""

    kind: Literal["step_has_todo"] = "step_has_todo"
    locations: list[Annotated[StepTodoLocation, Field(discriminator="kind")]]


class StepHasPlanFieldReason(BaseModel):
    """Step dropped because it carries ``_plan_*`` fields."""

    kind: Literal["step_has_plan_field"] = "step_has_plan_field"
    fields: list[str]


class CascadeReason(BaseModel):
    """Dropped because every source it depends on was dropped."""

    kind: Literal["cascade"] = "cascade"
    depends_on: list[StepPath]


DropReason = Annotated[
    StepHasTodoReason | StepHasPlanFieldReason | CascadeReason,
    Field(discriminator="kind"),
]


class DroppedStep(BaseModel):
    """A step removed from the concrete subset."""

    path: StepPath
    reason: DropReason


class DroppedOutput(BaseModel):
    """A workflow output removed; ``path`` locates its workflow (``[]`` at top level)."""

    path: StepPath
    label: str
    reason: DropReason


class RewrittenStepInput(BaseModel):
    """A surviving step input that lost some of its source refs."""

    path: StepPath
    in_key: str
    removed_refs: list[str]
    surviving_refs: list[str]


class ExtractResult(BaseModel):
    """Concrete subset of a draft plus an account of what was dropped or rewritten."""

    workflow: Any
    dropped_steps: list[DroppedStep] = []
    dropped_outputs: list[DroppedOutput] = []
    rewritten_step_inputs: list[RewrittenStepInput] = []


# --- Shared iteration helpers -----------------------------------------------


def _list_step_label(step: dict) -> str:
    label = step.get("label")
    if isinstance(label, str):
        return label
    step_id = step.get("id")
    return step_id if isinstance(step_id, str) else ""


def _iterate_steps(steps: Any) -> Iterator[tuple[str, Any]]:
    if isinstance(steps, list):
        for step in steps:
            if isinstance(step, dict):
                yield _list_step_label(step), step
    elif isinstance(steps, dict):
        yield from steps.items()


def _iterate_labeled(value: Any) -> Iterator[tuple[str, Any]]:
    """Iterate workflow inputs/outputs in dict form or list form (keyed by ``id``)."""
    if isinstance(value, list):
        for entry in value:
            if isinstance(entry, dict):
                entry_id = entry.get("id")
                yield (entry_id if isinstance(entry_id, str) else ""), entry
    elif isinstance(value, dict):
        yield from value.items()


def _iterate_step_input_entries(step_in: Any) -> Iterator[tuple[str, Any]]:
    if isinstance(step_in, list):
        for entry in step_in:
            if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                yield entry["id"], entry
    elif isinstance(step_in, dict):
        yield from step_in.items()


def _iterate_step_out_ids(out: Any) -> Iterator[str]:
    if isinstance(out, list):
        for entry in out:
            if isinstance(entry, str):
                yield entry
            elif isinstance(entry, dict) and isinstance(entry.get("id"), str):
                yield entry["id"]
    elif isinstance(out, dict):
        yield from out.keys()


def _read_output_source(output: Any) -> str | None:
    if isinstance(output, str):
        return output
    if not isinstance(output, dict):
        return None
    src = output.get("outputSource")
    if src is None:
        src = output.get("source")
    return src if isinstance(src, str) else None


def _extract_source_refs(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [ref for item in value for ref in _extract_source_refs(item)]
    if isinstance(value, dict) and value.get("source") is not None:
        return _extract_source_refs(value["source"])
    return []


def _split_source_ref(ref: str, step_labels: Iterable[str] | Mapping[str, Any]) -> tuple[str, str | None]:
    """Parse a source ref into ``(label, port)``.

    A slash-less ref naming a step is shorthand for ``<step>/output``; any other
    slash-less ref is a workflow-input ref and is reported port-less.
    """
    if "/" in ref:
        label, port = ref.split("/", 1)
        return label, port
    if ref in step_labels:
        return ref, "output"
    return ref, None


def _step_out_ports(step: dict) -> set[str]:
    """Declared ``out:`` ids plus every output an embedded ``GalaxyUserTool`` defines."""
    ports = set(_iterate_step_out_ids(step.get("out")))
    run = step.get("run")
    if isinstance(run, dict) and run.get("class") == "GalaxyUserTool":
        outputs = run.get("outputs")
        if isinstance(outputs, list):
            ports.update(o["name"] for o in outputs if isinstance(o, dict) and isinstance(o.get("name"), str))
        elif isinstance(outputs, dict):
            ports.update(outputs.keys())
    return ports


def _present_plan_fields(doc: Mapping[str, Any]) -> list[str]:
    return [f for f in PLAN_FIELDS if isinstance(doc.get(f), str) and doc[f]]


def _step_todo_locations(step: dict) -> list[StepTodoLocation]:
    locations: list[StepTodoLocation] = []
    if is_todo_sentinel(step.get("tool_id")):
        locations.append(ToolIdLocation())
    if is_todo_sentinel(step.get("tool_version")):
        locations.append(ToolVersionLocation())
    for key, _ in _iterate_step_input_entries(step.get("in")):
        if is_todo_sentinel(key):
            locations.append(InKeyLocation(key=key))
    for out_id in _iterate_step_out_ids(step.get("out")):
        if is_todo_sentinel(out_id):
            locations.append(OutIdLocation(id=out_id))
    return locations


def _location_sentinel(step: dict, location: StepTodoLocation) -> str:
    if isinstance(location, InKeyLocation):
        return location.key
    if isinstance(location, OutIdLocation):
        return location.id
    return step[location.kind]


def format_todo_location(location: Any) -> str:
    """Render a TODO location as a short human-readable string."""
    if isinstance(location, InKeyLocation):
        return f"in.{location.key}"
    if isinstance(location, OutIdLocation):
        return f"out.{location.id}"
    if isinstance(location, OutputSourceLocation):
        return f"outputs.{location.output_label} (port {location.port})"
    return location.kind


def _path_key(path: StepPath) -> str:
    return "/".join(path)


# --- detect_draft -----------------------------------------------------------


def detect_draft(workflow: Any) -> DraftSurvey:
    """Survey every TODO sentinel and ``_plan_*`` field across a draft's steps.

    Step paths are ``[outer_label, ..., inner_label]``; subworkflows recurse only
    when the inner ``run:`` is itself a draft. Top-level ``_plan_*`` fields are
    not reported here — :func:`validate_draft` flags those.
    """
    if not is_draft_workflow(workflow):
        return DraftSurvey(is_draft=False)
    todos: list[TodoHit] = []
    plan_fields: list[PlanHit] = []
    _walk_draft_steps(workflow, [], todos, plan_fields)
    return DraftSurvey(is_draft=True, todos=todos, plan_fields=plan_fields)


def _walk_draft_steps(workflow: dict, prefix: StepPath, todos: list[TodoHit], plan_fields: list[PlanHit]) -> None:
    for label, step in _iterate_steps(workflow.get("steps")):
        if not isinstance(step, dict):
            continue
        path = [*prefix, label]
        for location in _step_todo_locations(step):
            todos.append(TodoHit(path=path, location=location, sentinel=_location_sentinel(step, location)))
        for field in _present_plan_fields(step):
            plan_fields.append(PlanHit(path=path, field=field, value=step[field]))
        if is_draft_workflow(step.get("run")):
            _walk_draft_steps(step["run"], path, todos, plan_fields)

    # Inner draft outputs collect at the outer step's path; top-level ones at [].
    step_labels = {label for label, _ in _iterate_steps(workflow.get("steps"))}
    for label, output in _iterate_labeled(workflow.get("outputs")):
        ref = _read_output_source(output)
        if ref is None:
            continue
        _, port = _split_source_ref(ref, step_labels)
        if port is not None and is_todo_sentinel(port):
            todos.append(
                TodoHit(path=prefix, location=OutputSourceLocation(output_label=label, port=port), sentinel=port)
            )


# --- validate_draft ---------------------------------------------------------


def validate_draft(workflow: Any) -> DraftValidationResult:
    """Validate a draft workflow, collecting every diagnostic rather than raising.

    - ``structure_errors``: draft schema validation failures.
    - ``topology_errors``: TODO sentinels where topology must be concrete (input,
      output and step labels, input and step types) and edge refs that don't
      resolve to a declared step + port.
    - ``semantic_errors``: malformed TODO-shaped strings, and ``_plan_*`` left on
      a tool step with no remaining TODO sentinels.
    - ``warnings``: bare ``TODO`` in port position; ``_plan_*`` on a draft root.
    """
    if not is_draft_workflow(workflow):
        return DraftValidationResult(
            ok=False,
            structure_errors=[
                DraftValidationDiagnostic(path=[], message=f'not a draft workflow (class must be "{DRAFT_CLASS}")')
            ],
            survey=DraftSurvey(is_draft=False),
        )

    structure_errors: list[DraftValidationDiagnostic] = []
    try:
        GalaxyWorkflowDraft.model_validate(workflow)
    except ValidationError as e:
        structure_errors.append(DraftValidationDiagnostic(path=[], message=str(e)))

    survey = detect_draft(workflow)
    topology_errors: list[DraftValidationDiagnostic] = []
    semantic_errors: list[DraftValidationDiagnostic] = []
    warnings: list[DraftValidationDiagnostic] = []
    _walk_draft_validation(workflow, [], topology_errors, semantic_errors, warnings)

    for todo in survey.todos:
        if todo.sentinel == "TODO" and todo.location.kind not in ("tool_id", "tool_version"):
            warnings.append(
                DraftValidationDiagnostic(
                    path=todo.path,
                    message=(
                        f"bare `TODO` in port position (location: {format_todo_location(todo.location)}); "
                        "prefer `TODO_<hint>`"
                    ),
                )
            )

    return DraftValidationResult(
        ok=not (structure_errors or topology_errors or semantic_errors),
        structure_errors=structure_errors,
        topology_errors=topology_errors,
        semantic_errors=semantic_errors,
        warnings=warnings,
        survey=survey,
    )


def _check_todo_like(value: str, path: StepPath, context: str, errors: list[DraftValidationDiagnostic]) -> None:
    if TODO_LIKE_RE.match(value) and not TODO_SENTINEL_RE.fullmatch(value):
        errors.append(
            DraftValidationDiagnostic(
                path=path, message=f"{context} is TODO-shaped but malformed (must match {TODO_SENTINEL_PATTERN})"
            )
        )


def _check_label(
    label: str,
    path: StepPath,
    what: str,
    topology_errors: list[DraftValidationDiagnostic],
    semantic_errors: list[DraftValidationDiagnostic],
) -> None:
    if is_todo_sentinel(label):
        topology_errors.append(
            DraftValidationDiagnostic(path=path, message=f'{what} label cannot be a TODO sentinel: "{label}"')
        )
    else:
        _check_todo_like(label, path, f'{what} label "{label}"', semantic_errors)


def _walk_draft_validation(
    workflow: dict,
    prefix: StepPath,
    topology_errors: list[DraftValidationDiagnostic],
    semantic_errors: list[DraftValidationDiagnostic],
    warnings: list[DraftValidationDiagnostic],
) -> None:
    for field in _present_plan_fields(workflow):
        warnings.append(
            DraftValidationDiagnostic(
                path=prefix,
                message=(
                    f"top-level `{field}` is not part of the draft contract; "
                    "planning fields belong on individual steps"
                ),
            )
        )

    input_labels: set[str] = set()
    for label, workflow_input in _iterate_labeled(workflow.get("inputs")):
        input_labels.add(label)
        _check_label(label, prefix, "workflow input", topology_errors, semantic_errors)
        if isinstance(workflow_input, dict) and is_todo_sentinel(workflow_input.get("type")):
            topology_errors.append(
                DraftValidationDiagnostic(
                    path=prefix, message=f'workflow input "{label}" type cannot be a TODO sentinel'
                )
            )

    step_out_ports = {
        label: _step_out_ports(step) for label, step in _iterate_steps(workflow.get("steps")) if isinstance(step, dict)
    }
    known_labels = input_labels | step_out_ports.keys()

    def check_edge_ref(ref: str, path: StepPath, context: str) -> None:
        _check_todo_like(ref, path, f'{context} source "{ref}"', semantic_errors)
        label, port = resolve_source_reference(ref, known_labels)
        # Steps win over inputs on a shared label, matching the conversion path.
        if label in step_out_ports:
            if port not in step_out_ports[label]:
                topology_errors.append(
                    DraftValidationDiagnostic(
                        path=path,
                        message=f'{context} source "{ref}" references unknown port "{port}" on step "{label}"',
                    )
                )
            return
        if label in input_labels:
            return
        if "/" in ref:
            message = f'{context} source "{ref}" references unknown step "{label}"'
        else:
            message = f'{context} source "{ref}" does not match any declared workflow input or step'
        topology_errors.append(DraftValidationDiagnostic(path=path, message=message))

    for label, output in _iterate_labeled(workflow.get("outputs")):
        _check_label(label, prefix, "workflow output", topology_errors, semantic_errors)
        ref = _read_output_source(output)
        if ref is not None:
            check_edge_ref(ref, prefix, f'workflow output "{label}"')

    for label, step in _iterate_steps(workflow.get("steps")):
        if not isinstance(step, dict):
            continue
        _check_label(label, prefix, "step", topology_errors, semantic_errors)
        step_path = [*prefix, label]

        if is_todo_sentinel(step.get("type")):
            topology_errors.append(
                DraftValidationDiagnostic(path=step_path, message="step type cannot be a TODO sentinel")
            )

        for key in ("tool_id", "tool_version"):
            value = step.get(key)
            if isinstance(value, str):
                _check_todo_like(value, step_path, f'{key} "{value}"', semantic_errors)
        if isinstance(step.get("in"), dict):
            for key in step["in"]:
                _check_todo_like(key, step_path, f'in: key "{key}"', semantic_errors)
        for out_id in _iterate_step_out_ids(step.get("out")):
            _check_todo_like(out_id, step_path, f'out: id "{out_id}"', semantic_errors)

        for in_key, in_value in _iterate_step_input_entries(step.get("in")):
            for ref in _extract_source_refs(in_value):
                check_edge_ref(ref, step_path, f'step input "{in_key}"')

        # Planning context must be stripped once a tool step is resolved. Non-tool
        # steps (subworkflow, pause, pick_value) may keep it for now.
        if step.get("type") in (None, "tool") and not _step_todo_locations(step):
            present = _present_plan_fields(step)
            if present:
                semantic_errors.append(
                    DraftValidationDiagnostic(
                        path=step_path,
                        message=(
                            f"tool step has no TODO sentinels but still carries planning fields "
                            f"({', '.join(present)}); strip planning state before treating the step as resolved"
                        ),
                    )
                )

        if is_draft_workflow(step.get("run")):
            _walk_draft_validation(step["run"], step_path, topology_errors, semantic_errors, warnings)


# --- next_draft_step --------------------------------------------------------


def next_draft_step(workflow: Any) -> NextStepResult:
    """Pick the next step with remaining draft work. Pure and deterministic.

    Steps are visited in topological order, ties broken alphabetically by label.
    The first step carrying a TODO sentinel or ``_plan_*`` field is returned with
    prompt-shaped ``work`` items. A draft subworkflow is descended only once its
    outer step is itself fully concrete. Non-drafts report ``draft: false``.
    """
    if not is_draft_workflow(workflow):
        return NextStepResult(draft=False)
    return _next_draft_step_in(workflow, [])


def _next_draft_step_in(workflow: dict, prefix: StepPath) -> NextStepResult:
    steps = workflow.get("steps")
    step_labels = {label for label, _ in _iterate_steps(steps)}
    output_refs = _collect_output_refs(workflow.get("outputs"), step_labels)
    for label, step in _topo_ordered_steps(steps):
        if not isinstance(step, dict):
            continue
        step_path = [*prefix, label]
        work = _step_work_items(step, label, output_refs)
        if work:
            return NextStepResult(draft=True, step=step_path, work=work)
        if is_draft_workflow(step.get("run")):
            inner = _next_draft_step_in(step["run"], step_path)
            if inner.draft:
                return inner
    return NextStepResult(draft=False)


def _topo_ordered_steps(steps: Any) -> list[tuple[str, Any]]:
    """Topological order of steps; ties and cycles resolved alphabetically by label."""
    entries = list(_iterate_steps(steps))
    by_label = dict(entries)
    deps: dict[str, set[str]] = {}
    for label, step in entries:
        step_deps: set[str] = set()
        if isinstance(step, dict):
            for _, in_value in _iterate_step_input_entries(step.get("in")):
                for ref in _extract_source_refs(in_value):
                    dep_label, port = _split_source_ref(ref, by_label)
                    if port is not None and dep_label != label and dep_label in by_label:
                        step_deps.add(dep_label)
        deps[label] = step_deps

    ordered: list[tuple[str, Any]] = []
    remaining = set(by_label)
    while remaining:
        ready = sorted(label for label in remaining if not deps[label])
        if not ready:
            # Cycle or unresolvable refs: drain alphabetically so this stays
            # total; validate_draft reports the underlying problem.
            ordered.extend((label, by_label[label]) for label in sorted(remaining))
            break
        for label in ready:
            ordered.append((label, by_label[label]))
            remaining.discard(label)
            for other_deps in deps.values():
                other_deps.discard(label)
    return ordered


def _collect_output_refs(outputs: Any, step_labels: set[str]) -> dict[str, dict[str, set[str]]]:
    """Map step label -> port -> labels of workflow outputs referencing it."""
    by_step_port: dict[str, dict[str, set[str]]] = {}
    for label, output in _iterate_labeled(outputs):
        ref = _read_output_source(output)
        if ref is None:
            continue
        step_label, port = _split_source_ref(ref, step_labels)
        if port is not None:
            by_step_port.setdefault(step_label, {}).setdefault(port, set()).add(label)
    return by_step_port


def _sentinel_hint(sentinel: str) -> str | None:
    return None if sentinel == "TODO" else sentinel[len("TODO_") :]


def _step_work_items(step: dict, step_label: str, output_refs: dict[str, dict[str, set[str]]]) -> list[str]:
    work: list[str] = []
    if is_todo_sentinel(step.get("tool_id")):
        work.append("TODO[tool_id]: pick a Galaxy Tool Shed wrapper for this step")
    if is_todo_sentinel(step.get("tool_version")):
        work.append("TODO[tool_version]: pick the wrapper version")

    if isinstance(step.get("in"), dict):
        for key in step["in"]:
            if not is_todo_sentinel(key):
                continue
            hint = _sentinel_hint(key)
            hint_fragment = f" (semantic hint: '{hint}')" if hint is not None else ""
            work.append(f"TODO[in.{key}]: assign the real wrapper input port name{hint_fragment}")

    step_output_refs = output_refs.get(step_label, {})
    for out_id in _iterate_step_out_ids(step.get("out")):
        if not is_todo_sentinel(out_id):
            continue
        parts: list[str] = []
        hint = _sentinel_hint(out_id)
        if hint is not None:
            parts.append(f"semantic hint: '{hint}'")
        refs = sorted(step_output_refs.get(out_id, ()))
        if refs:
            word = "output" if len(refs) == 1 else "outputs"
            quoted = ", ".join(f"'{r}'" for r in refs)
            parts.append(f"referenced by workflow {word} {quoted}")
        hint_fragment = f" ({'; '.join(parts)})" if parts else ""
        work.append(f"TODO[out.{out_id}]: assign the real wrapper output port name{hint_fragment}")

    for field in _present_plan_fields(step):
        work.append(f"{field}: {step[field].strip()}")
    return work


# --- extract_draft_subset ---------------------------------------------------


class _Drop(BaseModel):
    path: StepPath
    reason: DropReason
    round: int


class _LevelResult(BaseModel):
    workflow: dict[str, Any]
    dropped_steps: list[_Drop]
    dropped_outputs: list[DroppedOutput]
    rewritten_step_inputs: list[RewrittenStepInput]


def extract_draft_subset(workflow: Any) -> ExtractResult:
    """Trim a draft down to its concrete subset. Pure and idempotent.

    Drops every step carrying a TODO sentinel or ``_plan_*`` field, then
    cascade-drops steps whose ``in:`` goes dead, then drops workflow outputs whose
    source went away. Multi-source inputs are rewritten to their surviving refs;
    an input with a ``default:`` survives losing all its refs. The result keeps
    ``class: GalaxyWorkflowDraft`` — promotion is the caller's decision. Non-draft
    inputs pass through unchanged.

    ``dropped_steps`` is ordered per workflow level by cascade round, then step
    path; each surviving subworkflow's drops follow its level's. A ``cascade``
    reason may cite a surviving subworkflow step whose inner workflow lost the
    referenced output — its own inner drops carry the underlying cause.
    """
    if not is_draft_workflow(workflow):
        return ExtractResult(workflow=workflow)
    level = _extract_level(workflow, [])
    return ExtractResult(
        workflow=level.workflow,
        dropped_steps=[DroppedStep(path=d.path, reason=d.reason) for d in level.dropped_steps],
        dropped_outputs=level.dropped_outputs,
        rewritten_step_inputs=level.rewritten_step_inputs,
    )


def _extract_level(workflow: dict, prefix: StepPath) -> _LevelResult:
    step_entries = [(label, step) for label, step in _iterate_steps(workflow.get("steps")) if isinstance(step, dict)]
    step_labels = {label for label, _ in step_entries}

    drops: dict[str, _Drop] = {}
    for label, step in step_entries:
        reason = _direct_drop_reason(step)
        if reason is not None:
            drops[label] = _Drop(path=[*prefix, label], reason=reason, round=0)

    # Only inline draft subworkflows are descended; other run: forms are opaque.
    inner_results: dict[str, _LevelResult] = {}
    for label, step in step_entries:
        if label not in drops and is_draft_workflow(step.get("run")):
            inner_results[label] = _extract_level(step["run"], [*prefix, label])

    round_ = 1
    while True:
        live_ports = _compute_live_ports(step_entries, drops, inner_results)
        changed = False
        for label, step in step_entries:
            if label in drops:
                continue
            depends_on = _check_step_cascade(step, prefix, drops, live_ports, step_labels)
            if depends_on is not None:
                drops[label] = _Drop(path=[*prefix, label], reason=CascadeReason(depends_on=depends_on), round=round_)
                changed = True
        if not changed:
            break
        round_ += 1

    live_ports = _compute_live_ports(step_entries, drops, inner_results)

    rewritten: list[RewrittenStepInput] = []
    for label, step in step_entries:
        if label not in drops:
            rewritten.extend(_compute_input_rewrites(step, [*prefix, label], drops, live_ports))

    trimmed_outputs, dropped_outputs = _trim_outputs(workflow.get("outputs"), drops, live_ports, prefix)
    trimmed: dict[str, Any] = {}
    for key, value in workflow.items():
        if key == "steps":
            trimmed[key] = _trim_steps(value, drops, inner_results, live_ports)
        elif key == "outputs":
            trimmed[key] = trimmed_outputs
        else:
            trimmed[key] = value
    trimmed["class"] = DRAFT_CLASS

    dropped_steps = sorted(drops.values(), key=lambda d: (d.round, _path_key(d.path)))
    for label, inner in inner_results.items():
        if label in drops:
            continue
        dropped_steps.extend(inner.dropped_steps)
        dropped_outputs.extend(inner.dropped_outputs)
        rewritten.extend(inner.rewritten_step_inputs)

    return _LevelResult(
        workflow=trimmed,
        dropped_steps=dropped_steps,
        dropped_outputs=dropped_outputs,
        rewritten_step_inputs=rewritten,
    )


def _direct_drop_reason(step: dict) -> StepHasTodoReason | StepHasPlanFieldReason | None:
    """TODO sentinels first, then plan fields, mirroring the planning order."""
    locations = _step_todo_locations(step)
    if locations:
        return StepHasTodoReason(locations=locations)
    fields = _present_plan_fields(step)
    if fields:
        return StepHasPlanFieldReason(fields=fields)
    return None


def _compute_live_ports(
    step_entries: list[tuple[str, dict]], drops: dict[str, _Drop], inner_results: dict[str, _LevelResult]
) -> dict[str, set[str]]:
    """Surviving output ports per step label (dropped steps map to an empty set).

    An inline draft subworkflow exposes only its surviving inner outputs; every
    other step exposes :func:`_step_out_ports`.
    """
    live_ports: dict[str, set[str]] = {}
    for label, step in step_entries:
        if label in drops:
            live_ports[label] = set()
        elif label in inner_results:
            inner_outputs = inner_results[label].workflow.get("outputs")
            live_ports[label] = {out_label for out_label, _ in _iterate_labeled(inner_outputs)}
        else:
            live_ports[label] = _step_out_ports(step)
    return live_ports


def _check_step_cascade(
    step: dict, prefix: StepPath, drops: dict[str, _Drop], live_ports: dict[str, set[str]], step_labels: set[str]
) -> list[StepPath] | None:
    """Return the cited dead dependencies if any ``in:`` entry went fully dead, else None."""
    depends_on: dict[str, StepPath] = {}
    cascade = False
    for _, in_value in _iterate_step_input_entries(step.get("in")):
        refs = _extract_source_refs(in_value)
        if not refs:
            continue
        any_alive = False
        local_deps: list[tuple[str, StepPath]] = []
        for ref in refs:
            ref_step, ref_port = _split_source_ref(ref, step_labels)
            # Workflow-input refs are always alive; dangling refs are treated as
            # alive so only validate_draft reports them.
            if ref_port is None or ref_step not in step_labels:
                any_alive = True
            elif ref_step in drops:
                local_deps.append((ref_step, drops[ref_step].path))
            elif ref_port not in live_ports.get(ref_step, set()):
                # Step survives but its inner workflow lost the port.
                local_deps.append((ref_step, [*prefix, ref_step]))
            else:
                any_alive = True
        if not any_alive and not (isinstance(in_value, dict) and "default" in in_value):
            cascade = True
            for key, path in local_deps:
                depends_on.setdefault(key, path)
    if not cascade:
        return None
    return sorted(depends_on.values(), key=_path_key)


def _ref_is_dead(ref: str, drops: dict[str, _Drop], live_ports: dict[str, set[str]]) -> bool:
    # live_ports is keyed by every step label at this level, so it doubles as
    # the label universe for shorthand resolution.
    ref_step, ref_port = _split_source_ref(ref, live_ports)
    if ref_port is None:
        return False
    if ref_step in drops:
        return True
    ports = live_ports.get(ref_step)
    return ports is not None and ref_port not in ports


def _input_refs(value: Any) -> list[str]:
    """Source refs carried directly by a step-input value (string, list, or dict ``source``)."""
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        refs: list[str] = []
        for entry in value:
            if isinstance(entry, str):
                refs.append(entry)
            elif isinstance(entry, dict):
                refs.extend(_input_refs({"source": entry.get("source")}))
        return refs
    if isinstance(value, dict):
        source = value.get("source")
        if isinstance(source, str):
            return [source]
        if isinstance(source, list):
            return [s for s in source if isinstance(s, str)]
    return []


def _compute_input_rewrites(
    step: dict, step_path: StepPath, drops: dict[str, _Drop], live_ports: dict[str, set[str]]
) -> list[RewrittenStepInput]:
    rewrites: list[RewrittenStepInput] = []
    for in_key, value in _iterate_step_input_entries(step.get("in")):
        refs = _input_refs(value)
        removed = [r for r in refs if _ref_is_dead(r, drops, live_ports)]
        if removed:
            surviving = [r for r in refs if not _ref_is_dead(r, drops, live_ports)]
            rewrites.append(
                RewrittenStepInput(path=step_path, in_key=in_key, removed_refs=removed, surviving_refs=surviving)
            )
    return rewrites


def _trim_steps(
    steps: Any, drops: dict[str, _Drop], inner_results: dict[str, _LevelResult], live_ports: dict[str, set[str]]
) -> Any:
    if isinstance(steps, list):
        return [
            _trim_step(entry, _list_step_label(entry), inner_results, drops, live_ports)
            for entry in steps
            if isinstance(entry, dict) and _list_step_label(entry) not in drops
        ]
    if isinstance(steps, dict):
        return {
            label: (_trim_step(step, label, inner_results, drops, live_ports) if isinstance(step, dict) else step)
            for label, step in steps.items()
            if label not in drops
        }
    return steps


def _trim_step(
    step: dict,
    label: str,
    inner_results: dict[str, _LevelResult],
    drops: dict[str, _Drop],
    live_ports: dict[str, set[str]],
) -> dict:
    trimmed: dict[str, Any] = {}
    for key, value in step.items():
        if key == "in":
            trimmed[key] = _rewrite_step_in(value, drops, live_ports)
        elif key == "run" and label in inner_results:
            trimmed[key] = inner_results[label].workflow
        else:
            trimmed[key] = value
    return trimmed


def _rewrite_step_in(step_in: Any, drops: dict[str, _Drop], live_ports: dict[str, set[str]]) -> Any:
    if isinstance(step_in, list):
        return [
            _rewrite_source_carrier(entry, drops, live_ports) if isinstance(entry, dict) else entry for entry in step_in
        ]
    if isinstance(step_in, dict):
        return {key: _rewrite_step_input_value(value, drops, live_ports) for key, value in step_in.items()}
    return step_in


def _collapse(refs: list[str]) -> str | list[str]:
    return refs[0] if len(refs) == 1 else refs


def _rewrite_source_carrier(entry: dict, drops: dict[str, _Drop], live_ports: dict[str, set[str]]) -> dict:
    """Rewrite a dict's ``source:`` to its surviving refs; drop the key if none survive."""
    source = entry.get("source")
    if isinstance(source, str):
        surviving = [] if _ref_is_dead(source, drops, live_ports) else [source]
    elif isinstance(source, list):
        surviving = [s for s in source if isinstance(s, str) and not _ref_is_dead(s, drops, live_ports)]
    else:
        return entry
    rewritten: dict[str, Any] = {}
    for key, value in entry.items():
        if key != "source":
            rewritten[key] = value
        elif surviving:
            rewritten[key] = _collapse(surviving)
    return rewritten


def _rewrite_step_input_value(value: Any, drops: dict[str, _Drop], live_ports: dict[str, set[str]]) -> Any:
    refs = _input_refs(value)
    surviving = [r for r in refs if not _ref_is_dead(r, drops, live_ports)]
    if len(surviving) == len(refs):
        return value
    if isinstance(value, dict):
        return _rewrite_source_carrier(value, drops, live_ports)
    # A string or bare list with no survivors would have cascaded the step.
    return _collapse(surviving) if surviving else value


def _trim_outputs(
    outputs: Any, drops: dict[str, _Drop], live_ports: dict[str, set[str]], prefix: StepPath
) -> tuple[Any, list[DroppedOutput]]:
    dropped: list[DroppedOutput] = []

    def keep(label: str, value: Any) -> bool:
        ref = _read_output_source(value)
        if ref is None or not _ref_is_dead(ref, drops, live_ports):
            return True
        ref_step, _ = _split_source_ref(ref, live_ports)
        cited = drops[ref_step].path if ref_step in drops else [*prefix, ref_step]
        dropped.append(DroppedOutput(path=prefix, label=label, reason=CascadeReason(depends_on=[cited])))
        return False

    trimmed: Any = outputs
    if isinstance(outputs, list):
        trimmed = [
            entry
            for entry in outputs
            if keep(entry["id"] if isinstance(entry, dict) and isinstance(entry.get("id"), str) else "", entry)
        ]
    elif isinstance(outputs, dict):
        trimmed = {label: value for label, value in outputs.items() if keep(label, value)}
    dropped.sort(key=lambda d: d.label)
    return trimmed, dropped


# --- Visualization overlay --------------------------------------------------

PLANNED_CLASS: Final[str] = "planned"


class DraftPlannedReason(BaseModel):
    """Why a rendered step is planned: formatted TODO locations and its ``_plan_*`` fields."""

    todos: list[str] = []
    plan_fields: dict[str, str] = {}


class DraftOverlay(BaseModel):
    """Which rendered step nodes of a draft are planned, keyed by step render identity."""

    planned_steps: set[str] = set()
    planned_reason: dict[str, DraftPlannedReason] = {}

    def edge_is_planned(self, source_label: str, target_label: str, output_name: str, input_id: str) -> bool:
        """An edge is planned if either endpoint step is planned or a port it touches is a TODO."""
        return (
            source_label in self.planned_steps
            or target_label in self.planned_steps
            or is_todo_sentinel(output_name)
            or is_todo_sentinel(input_id)
        )


def raw_step_render_identity(step: Any, iter_key: str) -> str:
    """Render identity of a raw step dict: its non-empty ``label``, else its iteration key.

    Matches ``step.label or step.id`` on the normalized step, so overlays built
    from the raw draft key the same way visualizers look nodes up.
    """
    if isinstance(step, dict) and isinstance(step.get("label"), str) and step["label"]:
        return step["label"]
    return iter_key


def resolve_draft_overlay(workflow: Any) -> DraftOverlay | None:
    """Build the planned-node overlay for a raw draft; ``None`` for non-drafts.

    A top-level step is planned if it or any step nested under it carries a
    TODO sentinel or a non-empty ``_plan_*`` field. Workflow-level hits (such as
    a TODO ``outputSource`` port) mark no node.
    """
    survey = detect_draft(workflow)
    if not survey.is_draft:
        return None
    identity_by_key = {key: raw_step_render_identity(step, key) for key, step in _iterate_steps(workflow.get("steps"))}
    overlay = DraftOverlay()

    def reason_for(path: StepPath) -> DraftPlannedReason | None:
        if not path:
            return None
        identity = identity_by_key.get(path[0], path[0])
        overlay.planned_steps.add(identity)
        return overlay.planned_reason.setdefault(identity, DraftPlannedReason())

    for todo in survey.todos:
        reason = reason_for(todo.path)
        if reason is not None:
            reason.todos.append(format_todo_location(todo.location))
    for plan in survey.plan_fields:
        reason = reason_for(plan.path)
        if reason is not None:
            reason.plan_fields[plan.field] = plan.value
    return overlay


def draft_as_workflow(workflow: dict[str, Any]) -> dict[str, Any]:
    """Copy of a draft re-classed ``GalaxyWorkflow`` at every inline draft level.

    Lets tooling that only understands concrete Format2 (normalization, and so
    rendering) read a draft. TODO sentinels stay as plain strings and
    ``_plan_*`` fields as extras; nothing is validated or stripped.
    """

    def reclass(doc: dict[str, Any]) -> dict[str, Any]:
        copied = {**doc, "class": "GalaxyWorkflow"}
        steps = doc.get("steps")
        if isinstance(steps, dict):
            copied["steps"] = {key: reclass_step(step) for key, step in steps.items()}
        elif isinstance(steps, list):
            copied["steps"] = [reclass_step(step) for step in steps]
        return copied

    def reclass_step(step: Any) -> Any:
        if isinstance(step, dict) and is_draft_workflow(step.get("run")):
            return {**step, "run": reclass(step["run"])}
        return step

    return reclass(workflow)


def prepare_draft_for_render(workflow: Any, draft_overlay: bool = True) -> tuple[Any, DraftOverlay | None]:
    """Return ``(renderable_workflow, overlay)`` for a visualizer's raw input.

    Non-drafts pass through with no overlay. A draft is re-classed via
    :func:`draft_as_workflow`; its overlay is omitted when *draft_overlay* is false.
    """
    if not is_draft_workflow(workflow):
        return workflow, None
    overlay = resolve_draft_overlay(workflow) if draft_overlay else None
    return draft_as_workflow(workflow), overlay
