"""Legacy compatibility pre-pass for Format2 workflow dicts.

Restores aliases and shorthand forms that the pre-rewrite ``converter.py``
accepted but the new normalize/validate pipeline drops or rejects. Gated
by ``ConversionOptions.legacy_compat`` (default ``True``); a future major
release can flip the default off.

Covers:

* **A** - step-level ``outputs:`` aliased to ``out:``.
* **B** - step-form ``type: input``/``input_collection``/``parameter_input``
  lifted into top-level ``inputs:``.
* **D** - non-string ``tool_version`` (e.g. unquoted YAML float ``0.1``)
  coerced to ``str``.

C (int ``$link``) and F (bare-list dict-form ``in:`` value) were originally
gated here but are bugs against the schema, not legacy aliases, and are
fixed unconditionally elsewhere.

Recurses into inline subworkflow ``run:`` dicts.
"""

from __future__ import annotations

from typing import Any

_INPUT_STEP_TYPES = {"input", "input_collection", "parameter_input"}


def apply_legacy_compat(workflow: dict[str, Any]) -> dict[str, Any]:
    """Apply A, B, D, F shims to a Format2 workflow dict in place-ish.

    Returns a new dict; nested dicts may be shared with the input where no
    rewrite was needed.
    """
    workflow = _lift_step_form_inputs(workflow)

    steps = workflow.get("steps")
    if isinstance(steps, dict):
        cleaned: dict[str, Any] | list[Any] = {
            k: _clean_step(v) if isinstance(v, dict) else v for k, v in steps.items()
        }
        workflow = {**workflow, "steps": cleaned}
    elif isinstance(steps, list):
        cleaned = [_clean_step(s) if isinstance(s, dict) else s for s in steps]
        workflow = {**workflow, "steps": cleaned}

    return workflow


def _clean_step(step: dict[str, Any]) -> dict[str, Any]:
    step = _alias_outputs_to_out(step)
    step = _coerce_tool_version(step)

    run = step.get("run")
    if isinstance(run, dict) and run.get("class") == "GalaxyWorkflow":
        step = {**step, "run": apply_legacy_compat(run)}

    return step


def _alias_outputs_to_out(step: dict[str, Any]) -> dict[str, Any]:
    if "outputs" in step and "out" not in step:
        step = {**step}
        step["out"] = step.pop("outputs")
    return step


def _coerce_tool_version(step: dict[str, Any]) -> dict[str, Any]:
    tv = step.get("tool_version")
    if isinstance(tv, (int, float)) and not isinstance(tv, bool):
        step = {**step, "tool_version": str(tv)}
    return step


def _lift_step_form_inputs(workflow: dict[str, Any]) -> dict[str, Any]:
    """Move step entries with ``type: input`` (etc.) into top-level ``inputs:``."""
    steps = workflow.get("steps")
    inputs = workflow.get("inputs")

    lifted: dict[str, Any] = {}
    remaining_dict: dict[str, Any] | None = None
    remaining_list: list[Any] | None = None

    if isinstance(steps, dict):
        remaining_dict = {}
        for key, step in steps.items():
            if isinstance(step, dict) and step.get("type") in _INPUT_STEP_TYPES:
                lifted_key = step.get("label") or step.get("id") or key
                lifted[str(lifted_key)] = _step_to_input(step)
            else:
                remaining_dict[key] = step
    elif isinstance(steps, list):
        remaining_list = []
        for step in steps:
            if isinstance(step, dict) and step.get("type") in _INPUT_STEP_TYPES:
                lifted_key = step.get("label") or step.get("id")
                if lifted_key is None:
                    remaining_list.append(step)
                    continue
                lifted[str(lifted_key)] = _step_to_input(step)
            else:
                remaining_list.append(step)

    if not lifted:
        return workflow

    new_workflow = dict(workflow)
    if remaining_dict is not None:
        new_workflow["steps"] = remaining_dict
    elif remaining_list is not None:
        new_workflow["steps"] = remaining_list

    if isinstance(inputs, dict):
        merged = {**lifted, **inputs}
        new_workflow["inputs"] = merged
    elif isinstance(inputs, list):
        existing_keys = {entry.get("id") or entry.get("label") for entry in inputs if isinstance(entry, dict)}
        extra = []
        for k, v in lifted.items():
            if k in existing_keys:
                continue
            extra.append({"id": k, **v})
        new_workflow["inputs"] = extra + list(inputs)
    else:
        new_workflow["inputs"] = lifted

    return new_workflow


def _step_to_input(step: dict[str, Any]) -> dict[str, Any]:
    """Strip step-only keys to leave a top-level input parameter dict."""
    step_only = {
        "id",
        "label",
        "type",
        "position",
        "tool_id",
        "tool_version",
        "in",
        "out",
        "run",
        "state",
        "tool_state",
    }
    raw_type = step.get("type")
    type_alias = {
        "input": "data",
        "input_collection": "collection",
        "parameter_input": None,
    }
    out: dict[str, Any] = {}
    for k, v in step.items():
        if k in step_only:
            continue
        out[k] = v
    if raw_type == "parameter_input":
        if "type" not in out and "parameter_type" in out:
            out["type"] = out.pop("parameter_type")
    elif raw_type in type_alias:
        mapped = type_alias[raw_type]
        if mapped is not None and "type" not in out:
            out["type"] = mapped
    return out
