"""Step input ``valueFrom`` (CWL ``WorkflowStepInput.valueFrom``) <-> native ``in[name].value_from``.

These convert whole workflows through the dict API Galaxy uses; field-level
cases are in ``expectations/step_input_value_from.yml``.
"""

import json
from typing import Any

import pytest
from pydantic import ValidationError

from gxformat2.converter import python_to_workflow
from gxformat2.examples import load
from gxformat2.export import from_galaxy_native
from gxformat2.normalized import normalized_format2, NormalizedFormat2


def _format2_step_inputs(workflow: dict[str, Any] | NormalizedFormat2) -> dict[str, Any]:
    """Map step label -> input id -> its source, default and valueFrom, recursing into subworkflows."""
    nf2 = workflow if isinstance(workflow, NormalizedFormat2) else normalized_format2(workflow)
    steps: dict[str, Any] = {}
    for step in nf2.steps:
        entry: dict[str, Any] = {
            "in": {
                step_input.id: step_input.model_dump(include={"source", "default", "valueFrom"}, exclude_none=True)
                for step_input in step.in_
            }
        }
        if isinstance(step.run, NormalizedFormat2):
            entry["run"] = _format2_step_inputs(step.run)
        steps[step.label or step.id] = entry
    return steps


def _native_step_inputs(native: dict[str, Any]) -> dict[str, Any]:
    """Map step label -> its ``in`` and connected input names, recursing into subworkflows."""
    steps: dict[str, Any] = {}
    for key, step in native["steps"].items():
        entry: dict[str, Any] = {"in": step.get("in"), "connected": sorted(step.get("input_connections", {}))}
        if step.get("subworkflow"):
            entry["subworkflow"] = _native_step_inputs(step["subworkflow"])
        steps[step.get("label") or key] = entry
    return steps


def test_format2_value_from_reaches_native():
    native = python_to_workflow(load("synthetic-step-input-value-from.gxwf.yml"))
    steps = {step["label"]: step for step in native["steps"].values()}

    assert steps["on_connection"]["in"] == {"parameter": {"value_from": "$(self + 1)"}}
    assert list(steps["on_connection"]["input_connections"]) == ["parameter"]
    assert steps["on_default"]["in"] == {"parameter": {"default": 4, "value_from": "$(self * 2)"}}
    assert steps["on_nothing"]["in"] == {"parameter": {"value_from": "$(7)"}}
    assert steps["subworkflow"]["in"] == {"inner_int": {"value_from": "$(self + 1)"}}


def test_format2_value_from_round_trip():
    workflow = load("synthetic-step-input-value-from.gxwf.yml")
    expected = _format2_step_inputs(workflow)

    round_tripped = from_galaxy_native(python_to_workflow(workflow))

    assert _format2_step_inputs(round_tripped) == expected


def test_native_value_from_round_trip():
    native = load("converted-step-input-value-from.ga")
    expected = _native_step_inputs(native)
    assert expected["on_default"]["in"] == {"parameter": {"default": 4, "value_from": "$(self * 2)"}}

    round_tripped = python_to_workflow(from_galaxy_native(native))

    assert _native_step_inputs(round_tripped) == expected


def test_exported_value_from_sits_next_to_source():
    exported = from_galaxy_native(load("converted-step-input-value-from.ga"))

    assert exported["steps"]["on_connection"]["in"] == {"parameter": {"source": "n", "valueFrom": "$(self + 1)"}}
    assert exported["steps"]["on_nothing"]["in"] == {"parameter": {"valueFrom": "$(7)"}}


def test_value_from_in_list_form():
    workflow = load("synthetic-step-input-value-from.gxwf.yml")
    workflow["steps"]["on_connection"]["in"] = [{"id": "parameter", "source": "n", "valueFrom": "$(self + 1)"}]

    native = python_to_workflow(workflow)

    assert native["steps"]["1"]["in"] == {"parameter": {"value_from": "$(self + 1)"}}


@pytest.mark.parametrize("step_type", ["pause", "pick_value"])
def test_value_from_on_other_step_types_is_kept_for_galaxy_to_refuse(step_type):
    workflow = load("synthetic-step-input-value-from.gxwf.yml")
    workflow["steps"]["on_connection"] = {"type": step_type, "in": {"input": {"source": "n", "valueFrom": "$(self)"}}}

    native = python_to_workflow(workflow)

    assert native["steps"]["1"]["in"] == {"input": {"value_from": "$(self)"}}


@pytest.mark.parametrize("step_type", ["pause", "pick_value"])
def test_default_only_entries_on_other_step_types_stay_dropped(step_type):
    # As on main: these step types never carried their ``in`` defaults to native.
    workflow = load("synthetic-step-input-value-from.gxwf.yml")
    workflow["steps"]["on_connection"] = {"type": step_type, "in": {"input": {"source": "n", "default": 4}}}

    native = python_to_workflow(workflow)

    assert "in" not in native["steps"]["1"]


def test_native_value_from_that_is_not_a_string_names_its_location():
    with pytest.raises(ValidationError, match=r"steps\.2\.in\.parameter\.value_from\n  Input should be a valid string"):
        from_galaxy_native(load("converted-step-input-value-from-not-string.ga"))


@pytest.mark.parametrize("fixture", ["synthetic-nested-subworkflow.gxwf.yml", "synthetic-when-step.gxwf.yml"])
def test_workflow_without_value_from_gains_no_value_from_keys(fixture):
    native = python_to_workflow(load(fixture))
    exported = from_galaxy_native(native)

    for converted in (native, exported):
        text = json.dumps(converted)
        assert '"value_from"' not in text
        assert '"valueFrom"' not in text

