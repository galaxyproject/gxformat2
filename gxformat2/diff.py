"""Structural diff of two Format2 workflows (either may be a ``GalaxyWorkflowDraft``).

Steps match on their step key, the identity source references and
:func:`gxformat2.draft.detect_draft` use: the dict key, or for list-form steps
the label, else the id, else the index id normalization assigns. ``_plan_*``
fields never count as changes; they are reported per step so consumers can
map a step back to its source. Only the top level is compared; subworkflow
contents and workflow metadata (label, doc, tags, comments, report) are not.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, computed_field

from gxformat2.draft import iterate_steps, present_plan_fields, draft_as_workflow, is_draft_workflow
from gxformat2.normalized import (
    normalized_format2,
    NormalizedFormat2,
    NormalizedWorkflowStep,
    resolve_source_reference,
)
from gxformat2.normalized._format2 import ImportReference
from gxformat2.yaml import ordered_load_path

INPUT_FIELDS: tuple[str, ...] = ("type", "collection_type", "optional", "format", "default")
STEP_FIELDS: tuple[str, ...] = ("label", "type", "tool_id", "tool_version", "when", "run")
STATE_SEPARATOR = "|"

WorkflowSource = dict[str, Any] | str | Path | os.PathLike[str]


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
    type: str
    tool_id: str | None = None
    tool_version: str | None = None
    plan_fields: dict[str, str] = {}
    upstream: list[str] = []
    downstream: list[str] = []
    workflow_outputs: list[str] = []
    connections: list[str] = []


class StepChange(BaseModel):
    """A step present on both sides whose fields, state or edges differ."""

    label: str | None = None
    fields: dict[str, ValueChange] = {}
    state: dict[str, StateChange] = {}
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
    def text(self) -> str:
        return f"{_ref_text((self.source, self.source_port))} -> {self.target}/{self.target_port}"


@dataclass
class _Side:
    """One workflow reduced to what the diff compares."""

    is_draft: bool
    inputs: dict[str, Any]
    outputs: dict[str, _Ref | None]
    steps: dict[str, NormalizedWorkflowStep]
    plan_fields: dict[str, dict[str, str]]
    edges: list[_Edge]
    unlabeled_steps: list[str]

    def edges_into(self, key: str) -> list[_Edge]:
        return [edge for edge in self.edges if edge.target == key]

    def edges_out_of(self, key: str) -> list[_Edge]:
        return [edge for edge in self.edges if edge.source == key and edge.source_port is not None]

    def outputs_from(self, key: str) -> list[str]:
        return [label for label, ref in self.outputs.items() if ref is not None and ref[0] == key]


def _load(workflow: WorkflowSource) -> dict[str, Any]:
    if isinstance(workflow, (str, Path, os.PathLike)):
        workflow = ordered_load_path(str(workflow))
    if not isinstance(workflow, dict):
        raise TypeError("expected a Format2 workflow mapping")
    if "$graph" in workflow and "class" not in workflow:
        raise ValueError("$graph documents are not supported by diff_workflows")
    return workflow


def _side(raw: dict[str, Any]) -> _Side:
    is_draft = is_draft_workflow(raw)
    nf2: NormalizedFormat2 = normalized_format2(draft_as_workflow(raw) if is_draft else raw)
    raw_steps = list(iterate_steps(raw))
    if len(raw_steps) != len(nf2.steps):
        raise ValueError("could not align raw steps with normalized steps")

    steps: dict[str, NormalizedWorkflowStep] = {}
    plan_fields: dict[str, dict[str, str]] = {}
    unlabeled: list[str] = []
    list_form = isinstance(raw.get("steps"), list)
    for (key, raw_step), step in zip(raw_steps, nf2.steps):
        steps[key] = step
        if isinstance(raw_step, dict):
            plan_fields[key] = {field: raw_step[field] for field in present_plan_fields(raw_step)}
            if list_form and not any(isinstance(raw_step.get(f), str) and raw_step[f] for f in ("label", "id")):
                unlabeled.append(key)

    input_ids = [inp.id for inp in nf2.inputs if inp.id]
    aliases: dict[str, str] = {}
    for key, step in steps.items():
        aliases.setdefault(step.id, key)
        if step.label:
            aliases.setdefault(step.label, key)
        aliases[key] = key

    def resolve(source: str) -> _Ref:
        if source in input_ids:
            return source, None
        step_label, port = resolve_source_reference(source, aliases.keys())
        return aliases.get(step_label, step_label), port

    edges: list[_Edge] = []
    for key, step in steps.items():
        for step_input in step.in_:
            sources = step_input.source
            if sources is None or step_input.id is None:
                continue
            for source in [sources] if isinstance(sources, str) else sources:
                node, port = resolve(source)
                edges.append(_Edge(source=node, source_port=port, target=key, target_port=step_input.id))

    outputs = {
        output.id: None if output.outputSource is None else resolve(output.outputSource)
        for output in nf2.outputs
        if output.id is not None
    }

    return _Side(
        is_draft=is_draft,
        inputs={inp.id: _input_fields(inp) for inp in nf2.inputs if inp.id},
        outputs=outputs,
        steps=steps,
        plan_fields=plan_fields,
        edges=edges,
        unlabeled_steps=unlabeled,
    )


def _input_fields(inp: Any) -> dict[str, Any]:
    dumped = inp.model_dump(by_alias=True, mode="json")
    fields = {field: dumped.get(field) for field in INPUT_FIELDS}
    if fields["optional"] is None:
        fields["optional"] = False
    if isinstance(fields["format"], str):
        fields["format"] = [fields["format"]]
    return fields


def _flatten_state(value: Any, prefix: str = "") -> dict[str, Any]:
    """Leaf paths of a state dict, nested keys joined by ``|``; lists and markers are leaves."""
    if isinstance(value, dict) and value and "__class__" not in value:
        flat: dict[str, Any] = {}
        for key, child in value.items():
            flat.update(_flatten_state(child, f"{prefix}{STATE_SEPARATOR}{key}" if prefix else str(key)))
        return flat
    return {prefix: value} if prefix else {}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, default=str)


def _step_state(step: NormalizedWorkflowStep) -> dict[str, Any]:
    state = step.state if step.state is not None else step.tool_state
    return _flatten_state(state or {})


def _step_field(step: NormalizedWorkflowStep, field: str) -> Any:
    if field == "type":
        return step.type_.value
    if field == "run":
        return _run_reference(step.run)
    return getattr(step, field)


def _run_reference(run: Any) -> str | dict[str, str] | None:
    """A linked run's URL or path, or its ``@import``; ``None`` for inline runs."""
    if isinstance(run, str):
        return run
    if isinstance(run, ImportReference):
        return {"@import": run.import_path}
    return None


def _set_change(before: set[str], after: set[str]) -> SetChange:
    return SetChange(added=sorted(after - before), removed=sorted(before - after))


def _summary(side: _Side, key: str) -> StepSummary:
    step = side.steps[key]
    edges_in = side.edges_into(key)
    edges_out = side.edges_out_of(key)
    return StepSummary(
        label=step.label,
        type=step.type_.value,
        tool_id=step.tool_id,
        tool_version=step.tool_version,
        plan_fields=side.plan_fields.get(key, {}),
        upstream=sorted({edge.source for edge in edges_in}),
        downstream=sorted({edge.target for edge in edges_out}),
        workflow_outputs=side.outputs_from(key),
        connections=sorted({edge.text for edge in edges_in + edges_out}),
    )


def _step_change(before: _Side, after: _Side, key: str) -> StepChange | None:
    b_step, a_step = before.steps[key], after.steps[key]
    fields = {}
    for field in STEP_FIELDS:
        b_value, a_value = _step_field(b_step, field), _step_field(a_step, field)
        if _canonical(b_value) != _canonical(a_value):
            fields[field] = ValueChange(before=b_value, after=a_value)

    b_state, a_state = _step_state(b_step), _step_state(a_step)
    state: dict[str, StateChange] = {}
    for path in [*b_state, *(p for p in a_state if p not in b_state)]:
        if path not in a_state:
            state[path] = StateChange(kind="removed", before=b_state[path])
        elif path not in b_state:
            state[path] = StateChange(kind="added", after=a_state[path])
        elif _canonical(b_state[path]) != _canonical(a_state[path]):
            state[path] = StateChange(kind="changed", before=b_state[path], after=a_state[path])

    b_in, a_in = before.edges_into(key), after.edges_into(key)
    b_out, a_out = before.edges_out_of(key), after.edges_out_of(key)
    change = StepChange(
        label=a_step.label,
        fields=fields,
        state=state,
        connections_in=_set_change({e.text for e in b_in}, {e.text for e in a_in}),
        connections_out=_set_change({e.text for e in b_out}, {e.text for e in a_out}),
        upstream=_set_change({e.source for e in b_in}, {e.source for e in a_in}),
        downstream=_set_change({e.target for e in b_out}, {e.target for e in a_out}),
        plan_fields_before=before.plan_fields.get(key, {}),
        plan_fields_after=after.plan_fields.get(key, {}),
    )
    edge_sets = (change.connections_in, change.connections_out)
    if not fields and not state and all(edge_set.is_empty for edge_set in edge_sets):
        return None
    return change


# --- Diff -------------------------------------------------------------------


def diff_workflows(before: WorkflowSource, after: WorkflowSource) -> WorkflowDiff:
    """Compare two Format2 workflows (dicts or paths); either may be a draft."""
    b_side, a_side = _side(_load(before)), _side(_load(after))

    inputs = InputsDiff(
        added=[i for i in a_side.inputs if i not in b_side.inputs],
        removed=[i for i in b_side.inputs if i not in a_side.inputs],
    )
    for input_id, b_fields in b_side.inputs.items():
        a_fields = a_side.inputs.get(input_id)
        if a_fields is None:
            continue
        changed = {
            field: ValueChange(before=b_fields[field], after=a_fields[field])
            for field in INPUT_FIELDS
            if _canonical(b_fields[field]) != _canonical(a_fields[field])
        }
        if changed:
            inputs.changed[input_id] = changed

    outputs = OutputsDiff(
        added=[o for o in a_side.outputs if o not in b_side.outputs],
        removed=[o for o in b_side.outputs if o not in a_side.outputs],
        changed={
            label: ValueChange(before=_ref_text(ref), after=_ref_text(a_side.outputs[label]))
            for label, ref in b_side.outputs.items()
            if label in a_side.outputs and ref != a_side.outputs[label]
        },
    )

    steps = StepsDiff(
        added={key: _summary(a_side, key) for key in a_side.steps if key not in b_side.steps},
        removed={key: _summary(b_side, key) for key in b_side.steps if key not in a_side.steps},
    )
    for key in a_side.steps:
        if key in b_side.steps:
            change = _step_change(b_side, a_side, key)
            if change is not None:
                steps.changed[key] = change

    fed = {edge.source for edge in a_side.edges if edge.source_port is None}
    warnings = [
        f"{side} has unlabeled steps matched by position: {', '.join(unlabeled)}"
        for side, unlabeled in (("BEFORE", b_side.unlabeled_steps), ("AFTER", a_side.unlabeled_steps))
        if unlabeled
    ]
    return WorkflowDiff(
        before_is_draft=b_side.is_draft,
        after_is_draft=a_side.is_draft,
        inputs=inputs,
        outputs=outputs,
        steps=steps,
        unwired_inputs=[i for i in a_side.inputs if i not in fed],
        warnings=warnings,
    )


# --- Rendering --------------------------------------------------------------


def _value(value: Any) -> str:
    if value is None:
        return "(none)"
    return value if isinstance(value, str) else json.dumps(value)


def _step_heading(key: str, label: str | None) -> str:
    return key if not label or label == key else f"{key} ({label})"


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
        return f"    state {path}: added {_value(change.after)}"
    if change.kind == "removed":
        return f"    state {path}: removed (was {_value(change.before)})"
    return f"    state {path}: {_value(change.before)} -> {_value(change.after)}"


def _step_change_lines(key: str, change: StepChange) -> list[str]:
    lines = [f"Step changed: {_step_heading(key, change.label)}"]
    lines.extend(f"    {field}: {_value(v.before)} -> {_value(v.after)}" for field, v in change.fields.items())
    lines.extend(_state_line(path, state_change) for path, state_change in change.state.items())
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
state, when and connections, and AFTER inputs that feed no step.
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
