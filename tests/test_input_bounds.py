"""Numeric workflow input bounds survive native/Format 2 conversion."""

import json

import pytest

from gxformat2.converter import python_to_workflow
from gxformat2.normalized import to_format2, to_native


@pytest.mark.parametrize(
    ("input_type", "bounds"),
    [
        ("int", {"min": 1, "max": 5}),
        ("int", {"min": 0}),
        ("float", {"max": 0.5}),
    ],
)
def test_format2_input_bounds_survive_native_round_trip(input_type, bounds):
    workflow = {"class": "GalaxyWorkflow", "inputs": {"n": {"type": input_type, **bounds}}, "steps": {}}

    native = to_native(workflow).to_dict()
    state = native["steps"]["0"]["tool_state"]
    assert state["validators"] == [
        {"type": "in_range", "min": bounds.get("min"), "max": bounds.get("max"), "negate": False}
    ]

    restored = to_format2(native).to_dict()["inputs"][0]
    assert {key: restored[key] for key in bounds} == bounds
    assert {key for key in ("min", "max") if key in restored} == set(bounds)

    legacy_state = json.loads(python_to_workflow(workflow)["steps"]["0"]["tool_state"])
    assert legacy_state["validators"] == state["validators"]


@pytest.mark.parametrize(
    ("input_type", "validator", "expected"),
    [
        ("integer", {"type": "in_range", "min": 1, "max": 5, "negate": False}, {"min": 1, "max": 5}),
        ("float", {"type": "in_range", "min": None, "max": 0.5, "negate": False}, {"max": 0.5}),
    ],
)
def test_native_range_validator_exports_as_input_bounds(input_type, validator, expected):
    native = to_native({"class": "GalaxyWorkflow", "inputs": {"n": {"type": "int"}}, "steps": {}}).to_dict()
    state = native["steps"]["0"]["tool_state"]
    state["parameter_type"] = input_type
    state["validators"] = [validator]

    restored = to_format2(native).to_dict()["inputs"][0]
    assert {key: restored[key] for key in expected} == expected
    assert {key for key in ("min", "max") if key in restored} == set(expected)


def test_non_range_validator_does_not_create_bounds():
    native = to_native({"class": "GalaxyWorkflow", "inputs": {"n": {"type": "int"}}, "steps": {}}).to_dict()
    native["steps"]["0"]["tool_state"]["validators"] = [{"type": "regex", "expression": "[0-9]+", "negate": False}]

    restored = to_format2(native).to_dict()["inputs"][0]
    assert "min" not in restored
    assert "max" not in restored
