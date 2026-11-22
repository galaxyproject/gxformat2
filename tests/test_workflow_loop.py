"""Round trips of workflow loops: Format2 ``loop``/``outputMethod`` <-> native ``loop``.

Field-level conversions are covered by ``expectations/workflow_loop.yml``; these
tests compare every loop field of a whole workflow, nested loops included, after
a conversion there and back through the dict API Galaxy uses.
"""

import copy
import json
from typing import Any

import pytest

from gxformat2.converter import python_to_workflow
from gxformat2.examples import load
from gxformat2.export import from_galaxy_native
from gxformat2.normalized import normalized_format2, NormalizedFormat2

FORMAT2_LOOP_FIXTURES = ["synthetic-loop-single-variable.gxwf.yml", "synthetic-loop-cases.gxwf.yml"]


def _format2_loops(workflow: dict[str, Any] | NormalizedFormat2) -> dict[str, Any]:
    """Map each step label to its loop fields, recursing into inline subworkflows."""
    nf2 = workflow if isinstance(workflow, NormalizedFormat2) else normalized_format2(workflow)
    loops: dict[str, Any] = {}
    for step in nf2.steps:
        entry: dict[str, Any] = {
            "when": step.when,
            "loop": None if step.loop is None else [rule.model_dump(exclude_none=True) for rule in step.loop],
            "outputMethod": step.outputMethod,
        }
        if isinstance(step.run, NormalizedFormat2):
            entry["run"] = _format2_loops(step.run)
        loops[step.label or step.id] = entry
    return loops


def _native_loops(native: dict[str, Any]) -> dict[str, Any]:
    """Map each step label to its ``when`` and ``loop``, recursing into subworkflows."""
    loops: dict[str, Any] = {}
    for key, step in native["steps"].items():
        entry = {"when": step.get("when"), "loop": step.get("loop")}
        if step.get("subworkflow"):
            entry["subworkflow"] = _native_loops(step["subworkflow"])
        loops[step.get("label") or key] = entry
    return loops


@pytest.mark.parametrize("fixture", FORMAT2_LOOP_FIXTURES)
def test_format2_loop_round_trip(fixture):
    workflow = load(fixture)
    expected = _format2_loops(workflow)
    assert any(entry["loop"] for entry in expected.values())

    round_tripped = from_galaxy_native(python_to_workflow(workflow))

    assert _format2_loops(round_tripped) == expected


def _without_default_output_method(loops: dict[str, Any]) -> dict[str, Any]:
    """Drop ``output_method: last_iteration``, which export leaves out and Galaxy defaults."""
    loops = copy.deepcopy(loops)
    for entry in loops.values():
        loop = entry["loop"]
        if loop and loop.get("output_method") == "last_iteration":
            del loop["output_method"]
        if "subworkflow" in entry:
            entry["subworkflow"] = _without_default_output_method(entry["subworkflow"])
    return loops


def test_native_loop_round_trip():
    native = load("converted-loop-cases.ga")
    expected = _native_loops(native)
    assert expected["two_variables"]["loop"]["output_method"] == "last_iteration"
    assert expected["nested"]["subworkflow"]["inner"]["loop"] == {"inputs": {"i1": {"output_source": "o1"}}}

    round_tripped = python_to_workflow(from_galaxy_native(native))

    # Equal up to the default output_method, which Galaxy writes and export leaves out.
    assert "output_method" not in round_tripped["steps"]["2"]["loop"]
    assert _native_loops(round_tripped) == _without_default_output_method(expected)


def test_exported_loop_is_an_id_map():
    exported = from_galaxy_native(load("converted-loop-cases.ga"))

    assert exported["steps"]["two_variables"]["loop"] == {"i1": {"outputSource": "o1"}, "i2": {"outputSource": "o2"}}
    assert exported["steps"]["nested"]["run"]["steps"]["inner"]["loop"] == {"i1": {"outputSource": "o1"}}


@pytest.mark.parametrize("fixture", ["synthetic-nested-subworkflow.gxwf.yml", "synthetic-when-step.gxwf.yml"])
def test_workflow_without_loop_gains_no_loop_keys(fixture):
    native = python_to_workflow(load(fixture))
    exported = from_galaxy_native(native)

    for converted in (native, exported):
        text = json.dumps(converted)
        for key in ("loop", "outputMethod", "output_method"):
            assert f'"{key}"' not in text


def _single_variable_with(**step_fields: Any) -> dict[str, Any]:
    workflow = load("synthetic-loop-single-variable.gxwf.yml")
    workflow["steps"]["count"].update(step_fields)
    return workflow


def test_loop_entry_without_id_is_refused():
    workflow = _single_variable_with(loop=[{"outputSource": "o1"}])

    with pytest.raises(ValueError, match="Step count: loop entry 0 has no id"):
        python_to_workflow(workflow)


def test_duplicate_loop_input_is_refused():
    workflow = _single_variable_with(loop=[{"id": "i1", "outputSource": "o1"}, {"id": "i1", "default": 5}])

    with pytest.raises(ValueError, match="Step count: loop input 'i1' has more than one rule"):
        python_to_workflow(workflow)


def test_output_method_without_loop_is_refused():
    workflow = _single_variable_with(outputMethod="all_iterations")
    del workflow["steps"]["count"]["loop"]

    with pytest.raises(ValueError, match="Step count: outputMethod is only valid with a loop"):
        python_to_workflow(workflow)


@pytest.mark.parametrize(
    "step",
    [
        {"tool_id": "add_one", "in": {"input": "start"}},
        {"type": "pause", "in": {"input": "start"}},
        {"type": "pick_value", "in": {"a": "start", "b": "start"}},
    ],
    ids=["tool", "pause", "pick_value"],
)
def test_misplaced_loop_is_kept_for_galaxy_to_refuse(step):
    workflow = load("synthetic-loop-single-variable.gxwf.yml")
    workflow["steps"]["count"] = {**step, "when": "$(inputs.input < 10)", "loop": {"input": "output"}}

    native = python_to_workflow(workflow)

    assert native["steps"]["1"]["loop"] == {"inputs": {"input": {"output_source": "output"}}}
    assert normalized_format2(from_galaxy_native(native)).steps[0].loop[0].outputSource == "output"


def test_native_input_step_with_loop_is_refused():
    native = load("converted-loop-cases.ga")
    native["steps"]["0"]["loop"] = {"inputs": {"i1": {"output_source": "o1"}}}

    with pytest.raises(ValueError, match="a workflow input has a loop"):
        from_galaxy_native(native)
