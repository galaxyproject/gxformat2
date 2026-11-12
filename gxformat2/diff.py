"""Structural diff of two Format2 workflows (either may be a ``GalaxyWorkflowDraft``).

Steps are reported under their step key, the identity source references and
:func:`gxformat2.draft.detect_draft` use: the dict key, or for list-form steps
the label, else the id, else the index id normalization assigns. List-form steps
with the same ``id`` on both sides match first, so a relabel is a label change.
Inline subworkflows are diffed too, with their ids prefixed by the parent step
key and ``/``. ``_plan_*`` fields never count as changes; they are reported per
step so consumers can map a step back to its source. Workflow metadata (label,
doc, tags, comments, report) is not compared.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections.abc import Callable, Container, Iterable
from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, computed_field

from gxformat2.draft import draft_as_workflow, is_draft_workflow, iterate_steps, present_plan_fields
from gxformat2.normalized import (
    normalized_format2,
    NormalizedFormat2,
    NormalizedWorkflowStep,
    resolve_source_reference,
)
from gxformat2.normalized._format2 import ImportReference
from gxformat2.schema.gxformat2 import BaseInputParameter, WorkflowStepOutput
from gxformat2.yaml import ordered_load_path

INPUT_FIELDS: tuple[str, ...] = (
    "type",
    "collection_type",
    "optional",
    "format",
    "default",
    "min",
    "max",
    "restrictions",
    "suggestions",
    "restrictOnConnections",
    "validators",
    "fields",
    "column_definitions",
)
# A missing value for these input fields means this value.
INPUT_FIELD_ABSENT_VALUES: dict[str, Any] = {"optional": False, "restrictOnConnections": False}
STATE_SEPARATOR = "|"
INPUT_PORT = "output"
# Declared ``out`` entry fields; undeclared extra keys are not actions.
OUT_ACTION_FIELDS: set[str] = set(WorkflowStepOutput.model_fields) - {"id"}

WorkflowSource = dict[str, Any] | str | os.PathLike[str]


# --- Result models ----------------------------------------------------------


class ValueChange(BaseModel):
    """A value that differs between BEFORE and AFTER."""

    before: Any = None
    after: Any = None


class StateChange(ValueChange):
    """A state leaf that was added, removed or changed."""

    kind: Literal["added", "removed", "changed"]


class SetChange(BaseModel):
    """Members only in AFTER (``added``) or only in BEFORE (``removed``), sorted."""

    added: list[str] = []
    removed: list[str] = []

    @property
    def is_empty(self) -> bool:
        """Whether nothing was added or removed."""
        return not self.added and not self.removed


class InputsDiff(BaseModel):
    """Workflow input ids added or removed, and per-input field changes."""

    added: list[str] = []
    removed: list[str] = []
    changed: dict[str, dict[str, ValueChange]] = {}


class OutputsDiff(BaseModel):
    """Workflow output ids added or removed, and ``outputSource`` changes."""

    added: list[str] = []
    removed: list[str] = []
    changed: dict[str, ValueChange] = {}


class StepSummary(BaseModel):
    """An added or removed step, with its edges on the side it exists on."""

    label: str | None = None
    id: str | None = None
    type: str
    tool_id: str | None = None
    tool_version: str | None = None
    plan_fields: dict[str, str] = {}
    upstream: list[str] = []
    downstream: list[str] = []
    workflow_outputs: list[str] = []
    connections: list[str] = []


class StepChange(BaseModel):
    """A step present on both sides whose fields, state, input defaults, output actions or edges differ."""

    label: str | None = None
    fields: dict[str, ValueChange] = {}
    state: dict[str, StateChange] = {}
    in_defaults: dict[str, ValueChange] = {}
    out_actions: dict[str, ValueChange] = {}
    connections_in: SetChange = SetChange()
    connections_out: SetChange = SetChange()
    upstream: SetChange = SetChange()
    downstream: SetChange = SetChange()
    plan_fields_before: dict[str, str] = {}
    plan_fields_after: dict[str, str] = {}


class StepsDiff(BaseModel):
    """Steps keyed by step key: added and changed in AFTER order, removed in BEFORE order."""

    added: dict[str, StepSummary] = {}
    removed: dict[str, StepSummary] = {}
    changed: dict[str, StepChange] = {}


class WorkflowDiff(BaseModel):
    """Result of :func:`diff_workflows`."""

    before_is_draft: bool
    after_is_draft: bool
    inputs: InputsDiff = InputsDiff()
    outputs: OutputsDiff = OutputsDiff()
    steps: StepsDiff = StepsDiff()
    unwired_inputs: list[str] = []
    warnings: list[str] = []

    @computed_field  # type: ignore[prop-decorator]
    @property
    def has_changes(self) -> bool:
        """Whether anything differs; ``unwired_inputs`` and ``warnings`` don't count."""
        sections = (self.inputs, self.outputs, self.steps)
        return any(section.added or section.removed or section.changed for section in sections)


# --- Workflow view ------------------------------------------------------------


# (step key or input id, port); inputs have no port.
_Ref = tuple[str, str | None]


def _ref_text(ref: _Ref | None) -> str | None:
    if ref is None:
        return None
    node, port = ref
    return node if port is None else f"{node}/{port}"


@dataclass(frozen=True)
class _Edge:
    source: str
    source_port: str | None
    target: str
    target_port: str

    @property
    def from_input(self) -> bool:
        return self.source_port is None

    @property
    def text(self) -> str:
        return f"{_ref_text((self.source, self.source_port))} -> {self.target}/{self.target_port}"


@dataclass(frozen=True)
class _Neighborhood:
    """A step's port-level edges and the nodes at their other ends."""

    connections_in: set[str]
    connections_out: set[str]
    upstream: set[str]
    downstream: set[str]


@dataclass(frozen=True)
class _StepView:
    """One step reduced to the values the diff compares."""

    fields: dict[str, Any]
    state: dict[str, Any]
    in_defaults: dict[str, Any]
    out_actions: dict[str, dict[str, Any]]
    plan_fields: dict[str, str]
    raw_id: str | None
    # (raw, normalized) run of an inline subworkflow step.
    inline_run: tuple[dict[str, Any], NormalizedFormat2] | None


@dataclass
class _Side:
    """One workflow (or inline subworkflow, ids prefixed) reduced to what the diff compares."""

    list_form: bool
    inputs: dict[str, dict[str, Any]]
    outputs: dict[str, _Ref | None]
    steps: dict[str, _StepView]
    edges: list[_Edge]
    unlabeled_steps: list[str]

    def neighborhood(self, key: str) -> _Neighborhood:
        edges_in = [edge for edge in self.edges if edge.target == key]
        edges_out = [edge for edge in self.edges if edge.source == key and not edge.from_input]
        return _Neighborhood(
            connections_in={edge.text for edge in edges_in},
            connections_out={edge.text for edge in edges_out},
            upstream={edge.source for edge in edges_in},
            downstream={edge.target for edge in edges_out},
        )

    def outputs_from(self, key: str) -> list[str]:
        return [label for label, ref in self.outputs.items() if ref is not None and ref[0] == key]

    def renamed(self, keys: dict[str, str]) -> _Side:
        """This side with step keys renamed per *keys*; input ids are left alone."""
        if not keys:
            return self

        def step(key: str) -> str:
            return keys.get(key, key)

        return _Side(
            list_form=self.list_form,
            inputs=self.inputs,
            outputs={
                label: ref if ref is None or ref[1] is None else (step(ref[0]), ref[1])
                for label, ref in self.outputs.items()
            },
            steps={step(key): view for key, view in self.steps.items()},
            edges=[
                _Edge(
                    edge.source if edge.from_input else step(edge.source),
                    edge.source_port,
                    step(edge.target),
                    edge.target_port,
                )
                for edge in self.edges
            ],
            unlabeled_steps=self.unlabeled_steps,
        )


def _load(workflow: WorkflowSource) -> dict[str, Any]:
    if isinstance(workflow, (str, os.PathLike)):
        workflow = ordered_load_path(str(workflow))
    if not isinstance(workflow, dict):
        raise TypeError("expected a Format2 workflow mapping")
    if "$graph" in workflow and "class" not in workflow:
        raise ValueError("$graph documents are not supported by diff_workflows")
    return workflow


def _normalize(raw: dict[str, Any]) -> tuple[bool, NormalizedFormat2]:
    is_draft = is_draft_workflow(raw)
    return is_draft, normalized_format2(draft_as_workflow(raw) if is_draft else raw)


def _side(raw: dict[str, Any], nf2: NormalizedFormat2, prefix: str = "") -> _Side:
    """Reduce a workflow to a :class:`_Side`, every step key and input id prefixed with *prefix*."""
    raw_steps = list(iterate_steps(raw))
    if len(raw_steps) != len(nf2.steps):
        raise ValueError("could not align raw steps with normalized steps")
    input_ids = {inp.id for inp in nf2.inputs if inp.id}
    resolve = _source_resolver({key: step for (key, _), step in zip(raw_steps, nf2.steps)}, input_ids, prefix)

    edges: list[_Edge] = []
    for (key, _), step in zip(raw_steps, nf2.steps):
        for step_input in step.in_:
            sources = step_input.source
            if sources is None or step_input.id is None:
                continue
            for source in [sources] if isinstance(sources, str) else sources:
                edges.append(_Edge(*resolve(source), target=prefix + key, target_port=step_input.id))
    list_form = isinstance(raw.get("steps"), list)
    return _Side(
        list_form=list_form,
        inputs={prefix + inp.id: _input_fields(inp) for inp in nf2.inputs if inp.id},
        outputs={
            prefix + output.id: None if output.outputSource is None else resolve(output.outputSource)
            for output in nf2.outputs
            if output.id is not None
        },
        steps={prefix + key: _step_view(step, raw_step) for (key, raw_step), step in zip(raw_steps, nf2.steps)},
        edges=edges,
        unlabeled_steps=[prefix + key for key, raw_step in raw_steps if list_form and not _has_identity(raw_step)],
    )


def _has_identity(raw_step: dict[str, Any]) -> bool:
    return any(isinstance(raw_step.get(field), str) and raw_step[field] for field in ("label", "id"))


def _source_resolver(
    steps: dict[str, NormalizedWorkflowStep], input_ids: set[str], prefix: str
) -> Callable[[str], _Ref]:
    """Resolve a source to ``(step key, port)`` or ``(input id, None)``, longest label first, then prefix it."""
    aliases: dict[str, str] = {}
    for key, step in steps.items():
        aliases.setdefault(step.id, key)
        if step.label:
            aliases.setdefault(step.label, key)
        aliases[key] = key
    known_labels = aliases.keys() | input_ids

    def resolve(source: str) -> _Ref:
        label, port = resolve_source_reference(source, known_labels)
        # An input's only port is ``output``; ``<input>/output`` means ``<input>``.
        if label in input_ids and port == INPUT_PORT:
            return prefix + label, None
        return prefix + aliases.get(label, label), port

    return resolve


def _input_fields(inp: BaseInputParameter) -> dict[str, Any]:
    dumped = inp.model_dump(by_alias=True, mode="json")
    fields = {field: dumped.get(field) for field in INPUT_FIELDS}
    for field, absent in INPUT_FIELD_ABSENT_VALUES.items():
        if fields[field] is None:
            fields[field] = absent
    if isinstance(fields["format"], str):
        fields["format"] = [fields["format"]]
    return fields


def _step_view(step: NormalizedWorkflowStep, raw_step: Any) -> _StepView:
    fields = {
        "label": step.label,
        "type": step.type_.value,
        "tool_id": step.tool_id,
        "tool_version": step.tool_version,
        "when": step.when,
        "run": _run_reference(step.run),
    }
    raw = raw_step if isinstance(raw_step, dict) else {}
    raw_run = raw.get("run")
    raw_id = raw.get("id")
    return _StepView(
        fields=fields,
        state=_flatten_state((step.state if step.state is not None else step.tool_state) or {}),
        in_defaults={inp.id: inp.default for inp in step.in_ if inp.id is not None and inp.default is not None},
        out_actions=_out_actions(step),
        plan_fields={field: raw[field] for field in present_plan_fields(raw)},
        raw_id=raw_id if isinstance(raw_id, str) else None,
        inline_run=(
            (raw_run, step.run) if isinstance(step.run, NormalizedFormat2) and isinstance(raw_run, dict) else None
        ),
    )


def _flatten_state(value: Any, prefix: str = "") -> dict[str, Any]:
    """Leaf paths of a state dict, nested keys joined by ``|``; lists and markers are leaves."""
    if isinstance(value, dict) and value and "__class__" not in value:
        flat: dict[str, Any] = {}
        for key, child in value.items():
            flat.update(_flatten_state(child, f"{prefix}{STATE_SEPARATOR}{key}" if prefix else str(key)))
        return flat
    return {prefix: value} if prefix else {}


def _run_reference(run: Any) -> str | dict[str, str] | None:
    """Return a linked run's URL or path, or its ``@import``; ``None`` for inline runs."""
    if isinstance(run, str):
        return run
    if isinstance(run, ImportReference):
        return {"@import": run.import_path}
    return None


def _out_actions(step: NormalizedWorkflowStep) -> dict[str, dict[str, Any]]:
    """Set output actions (``rename``, ``hide``, ...) per declared ``out`` port; bare ports are skipped.

    ``false`` and empty values mean no action, the same as an absent one.
    """
    actions: dict[str, dict[str, Any]] = {}
    for out in step.out:
        dumped = out.model_dump(by_alias=True, mode="json", include=OUT_ACTION_FIELDS)
        set_actions = {action: value for action, value in dumped.items() if value}
        if out.id is not None and set_actions:
            actions[out.id] = set_actions
    return actions


# --- Comparison ---------------------------------------------------------------


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _differing_keys(before: dict[str, Any], after: dict[str, Any]) -> list[str]:
    """Keys one side lacks or whose values differ, BEFORE keys first."""
    return [
        key
        for key in [*before, *(k for k in after if k not in before)]
        if key not in before or key not in after or _canonical(before[key]) != _canonical(after[key])
    ]


def _value_changes(before: dict[str, Any], after: dict[str, Any]) -> dict[str, ValueChange]:
    """Differing values by key; the side lacking a key is ``None``."""
    return {key: ValueChange(before=before.get(key), after=after.get(key)) for key in _differing_keys(before, after)}


def _state_changes(before: dict[str, Any], after: dict[str, Any]) -> dict[str, StateChange]:
    return {
        path: StateChange(
            kind="added" if path not in before else "removed" if path not in after else "changed",
            before=before.get(path),
            after=after.get(path),
        )
        for path in _differing_keys(before, after)
    }


def _set_change(before: set[str], after: set[str]) -> SetChange:
    return SetChange(added=sorted(after - before), removed=sorted(before - after))


def _only_in(keys: Iterable[str], other: Container[str]) -> list[str]:
    return [key for key in keys if key not in other]


def _summary(side: _Side, key: str) -> StepSummary:
    view, edges = side.steps[key], side.neighborhood(key)
    return StepSummary(
        label=view.fields["label"],
        id=view.raw_id,
        type=view.fields["type"],
        tool_id=view.fields["tool_id"],
        tool_version=view.fields["tool_version"],
        plan_fields=view.plan_fields,
        upstream=sorted(edges.upstream),
        downstream=sorted(edges.downstream),
        workflow_outputs=side.outputs_from(key),
        connections=sorted(edges.connections_in | edges.connections_out),
    )


def _step_change(before: _Side, after: _Side, key: str) -> StepChange | None:
    b_view, a_view = before.steps[key], after.steps[key]
    b_edges, a_edges = before.neighborhood(key), after.neighborhood(key)
    change = StepChange(
        label=a_view.fields["label"],
        fields=_value_changes(b_view.fields, a_view.fields),
        state=_state_changes(b_view.state, a_view.state),
        in_defaults=_value_changes(b_view.in_defaults, a_view.in_defaults),
        out_actions=_value_changes(b_view.out_actions, a_view.out_actions),
        connections_in=_set_change(b_edges.connections_in, a_edges.connections_in),
        connections_out=_set_change(b_edges.connections_out, a_edges.connections_out),
        upstream=_set_change(b_edges.upstream, a_edges.upstream),
        downstream=_set_change(b_edges.downstream, a_edges.downstream),
        plan_fields_before=b_view.plan_fields,
        plan_fields_after=a_view.plan_fields,
    )
    # upstream/downstream are node-level views of the port-level edges, so they never decide membership.
    differs = change.fields or change.state or change.in_defaults or change.out_actions
    if not differs and change.connections_in.is_empty and change.connections_out.is_empty:
        return None
    return change


# --- Diff -------------------------------------------------------------------


def _id_renames(before: _Side, after: _Side) -> dict[str, str]:
    """BEFORE -> AFTER keys of list-form steps paired by an ``id`` unique on each side.

    A pair whose AFTER key is still another BEFORE step's key is dropped, leaving both to key matching.
    """
    if not (before.list_form and after.list_form):
        return {}
    b_ids, a_ids = _unique_ids(before), _unique_ids(after)
    renames = {b_ids[i]: a_ids[i] for i in b_ids if i in a_ids and b_ids[i] != a_ids[i]}
    while blocked := [b for b, a in renames.items() if a in before.steps and a not in renames]:
        for b in blocked:
            del renames[b]
    return renames


def _unique_ids(side: _Side) -> dict[str, str]:
    keys_by_id: dict[str, list[str]] = {}
    for key, view in side.steps.items():
        if view.raw_id:
            keys_by_id.setdefault(view.raw_id, []).append(key)
    return {step_id: keys[0] for step_id, keys in keys_by_id.items() if len(keys) == 1}


def _merge(target: dict[str, Any], entries: dict[str, Any]) -> None:
    for key, value in entries.items():
        if key in target:
            raise ValueError(f"diff key {key!r} names both a step and a step in an inline subworkflow")
        target[key] = value


def _diff_level(diff: WorkflowDiff, b_side: _Side, a_side: _Side) -> None:
    """Add one level's differences to *diff*, then recurse into inline subworkflows on both sides."""
    b_side = b_side.renamed(_id_renames(b_side, a_side))

    diff.inputs.added.extend(_only_in(a_side.inputs, b_side.inputs))
    diff.inputs.removed.extend(_only_in(b_side.inputs, a_side.inputs))
    inputs_changed = {
        input_id: _value_changes(b_fields, a_side.inputs[input_id])
        for input_id, b_fields in b_side.inputs.items()
        if input_id in a_side.inputs
    }
    _merge(diff.inputs.changed, {input_id: changed for input_id, changed in inputs_changed.items() if changed})

    diff.outputs.added.extend(_only_in(a_side.outputs, b_side.outputs))
    diff.outputs.removed.extend(_only_in(b_side.outputs, a_side.outputs))
    # Refs compare as tuples: step ``a/b`` and port ``b`` of step ``a`` render alike.
    _merge(
        diff.outputs.changed,
        {
            label: ValueChange(before=_ref_text(ref), after=_ref_text(a_side.outputs[label]))
            for label, ref in b_side.outputs.items()
            if label in a_side.outputs and ref != a_side.outputs[label]
        },
    )

    _merge(diff.steps.added, {key: _summary(a_side, key) for key in _only_in(a_side.steps, b_side.steps)})
    _merge(diff.steps.removed, {key: _summary(b_side, key) for key in _only_in(b_side.steps, a_side.steps)})
    matched = [key for key in a_side.steps if key in b_side.steps]
    changes = {key: _step_change(b_side, a_side, key) for key in matched}
    _merge(diff.steps.changed, {key: change for key, change in changes.items() if change is not None})

    diff.warnings.extend(
        f"{name} has unlabeled steps matched by position: {', '.join(unlabeled)}"
        for name, unlabeled in (("BEFORE", b_side.unlabeled_steps), ("AFTER", a_side.unlabeled_steps))
        if unlabeled
    )

    for key in matched:
        b_run, a_run = b_side.steps[key].inline_run, a_side.steps[key].inline_run
        if b_run is not None and a_run is not None:
            _diff_level(diff, _side(*b_run, prefix=f"{key}/"), _side(*a_run, prefix=f"{key}/"))


def diff_workflows(before: WorkflowSource, after: WorkflowSource) -> WorkflowDiff:
    """Compare two Format2 workflows (dicts or paths); either may be a draft."""
    b_raw, a_raw = _load(before), _load(after)
    (b_is_draft, b_nf2), (a_is_draft, a_nf2) = _normalize(b_raw), _normalize(a_raw)
    b_side, a_side = _side(b_raw, b_nf2), _side(a_raw, a_nf2)
    diff = WorkflowDiff(before_is_draft=b_is_draft, after_is_draft=a_is_draft)
    _diff_level(diff, b_side, a_side)
    fed = {edge.source for edge in a_side.edges if edge.from_input}
    diff.unwired_inputs = _only_in(a_side.inputs, fed)
    return diff


# --- Rendering --------------------------------------------------------------


def _value(value: Any) -> str:
    if value is None:
        return "(none)"
    return value if isinstance(value, str) else json.dumps(value)


def _state_value(value: Any) -> str:
    """Like :func:`_value`, but a leaf that is present shows ``null`` and ``""`` as such."""
    return json.dumps(value) if value is None or value == "" else _value(value)


def _step_heading(key: str, label: str | None) -> str:
    """The key, plus the label when it isn't the key or, for a nested step, its last segment."""
    return key if not label or label in (key, key.rsplit("/", 1)[-1]) else f"{key} ({label})"


def _summary_lines(verb: str, key: str, summary: StepSummary) -> list[str]:
    tool_parts = [part for part in (summary.tool_id, summary.tool_version) if part]
    tool = f" [{' '.join(tool_parts)}]" if tool_parts else ""
    lines = [f"Step {verb}: {_step_heading(key, summary.label)}{tool}"]
    for name, members in (
        ("upstream", summary.upstream),
        ("downstream", summary.downstream),
        ("workflow outputs", summary.workflow_outputs),
    ):
        if members:
            lines.append(f"    {name}: {', '.join(members)}")
    lines.extend(f"    has {field}" for field in summary.plan_fields)
    return lines


def _state_line(path: str, change: StateChange) -> str:
    if change.kind == "added":
        return f"    state {path}: added {_state_value(change.after)}"
    if change.kind == "removed":
        return f"    state {path}: removed (was {_state_value(change.before)})"
    return f"    state {path}: {_state_value(change.before)} -> {_state_value(change.after)}"


def _step_change_lines(key: str, change: StepChange) -> list[str]:
    lines = [f"Step changed: {_step_heading(key, change.label)}"]
    lines.extend(f"    {field}: {_value(v.before)} -> {_value(v.after)}" for field, v in change.fields.items())
    lines.extend(_state_line(path, state_change) for path, state_change in change.state.items())
    lines.extend(
        f"    in {port} default: {_value(v.before)} -> {_value(v.after)}" for port, v in change.in_defaults.items()
    )
    lines.extend(
        f"    out {port} actions: {_value(v.before)} -> {_value(v.after)}" for port, v in change.out_actions.items()
    )
    lines.extend(f"    - {edge}" for edge in change.connections_in.removed + change.connections_out.removed)
    lines.extend(f"    + {edge}" for edge in change.connections_in.added + change.connections_out.added)
    return lines


def render_text(diff: WorkflowDiff) -> str:
    """Render a :class:`WorkflowDiff` as plain text."""
    lines = [f"warning: {warning}" for warning in diff.warnings]
    if not diff.has_changes:
        lines.append("No differences.")
    for noun, section in (("Input", diff.inputs), ("Output", diff.outputs)):
        lines.extend(f"{noun} added: {item}" for item in section.added)
        lines.extend(f"{noun} removed: {item}" for item in section.removed)
    for input_id, fields in diff.inputs.changed.items():
        lines.extend(
            f"Input changed: {input_id} {field}: {_value(v.before)} -> {_value(v.after)}" for field, v in fields.items()
        )
    for output_id, v in diff.outputs.changed.items():
        lines.append(f"Output changed: {output_id} source: {_value(v.before)} -> {_value(v.after)}")
    for key, summary in diff.steps.removed.items():
        lines.extend(_summary_lines("removed", key, summary))
    for key, summary in diff.steps.added.items():
        lines.extend(_summary_lines("added", key, summary))
    for key, change in diff.steps.changed.items():
        lines.extend(_step_change_lines(key, change))
    if diff.unwired_inputs:
        lines.append(f"AFTER inputs feeding no step: {', '.join(diff.unwired_inputs)}")
    return "\n".join(lines)


# --- CLI --------------------------------------------------------------------

SCRIPT_DESCRIPTION = """
Compare two Format 2 Galaxy workflows (either may be a GalaxyWorkflowDraft) and
report added and removed inputs, outputs and steps, per-step changes to tool,
run, state, when, step input defaults, output actions and connections, and
AFTER inputs that feed no step. Inline subworkflows are compared too, their
step keys prefixed with the parent step key and "/".
"""


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("before", metavar="BEFORE", type=str, help="workflow before the change (.gxwf.yml)")
    parser.add_argument("after", metavar="AFTER", type=str, help="workflow after the change (.gxwf.yml)")
    parser.add_argument("--json", action="store_true", default=False, help="print the diff as JSON")
    parser.add_argument(
        "--exit-code", action="store_true", default=False, help="exit with status 1 when the workflows differ"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Entry point for ``gxwf-diff``."""
    args = _parser().parse_args(sys.argv[1:] if argv is None else argv)
    diff = diff_workflows(args.before, args.after)
    if args.json:
        print(diff.model_dump_json(indent=2))
    else:
        print(render_text(diff))
    return 1 if args.exit_code and diff.has_changes else 0


if __name__ == "__main__":
    sys.exit(main())
