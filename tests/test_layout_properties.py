"""Unit tests for the layout graph-property checkers.

The checkers in ``gxformat2.layout._properties`` are the cross-language layout
contract (run from declarative YAML by ``tests/test_interop_tests.py``). These
tests pin both directions: real laid-out documents satisfy every property, and
deliberately-broken documents trip the matching checker.
"""

import copy

import pytest

from gxformat2.examples import load
from gxformat2.layout import apply_layout
from gxformat2.layout._properties import (
    _BASE_CHECKERS,
    all_nodes_positioned,
    downstream_right_of_upstream,
    GRAPH_PROPERTY_CHECKERS,
    no_position_collisions,
    roots_leftmost,
)
from gxformat2.testing import run_declarative_case
from gxformat2.testing import TestCase as DeclarativeCase

ALL_CHECKERS = [
    downstream_right_of_upstream,
    all_nodes_positioned,
    no_position_collisions,
    roots_leftmost,
]

# A minimal valid laid-out Format2 doc: input -> cat.
_BASE = {
    "class": "GalaxyWorkflow",
    "inputs": {"the_input": {"type": "data", "position": {"left": 0, "top": 0}}},
    "steps": {
        "cat": {
            "tool_id": "cat1",
            "in": {"input1": "the_input"},
            "position": {"left": 220, "top": 0},
        }
    },
}


@pytest.mark.parametrize("checker", ALL_CHECKERS, ids=[c.__name__ for c in ALL_CHECKERS])
@pytest.mark.parametrize("fixture", ["synthetic-basic.gxwf.yml", "real-basic-without-step-input-label.ga"])
def test_real_layout_satisfies_property(checker, fixture):
    wf = load(fixture)
    apply_layout(wf, overwrite=True)
    checker(wf)  # raises AssertionError on violation


def test_registry_exposes_all_checkers():
    assert set(GRAPH_PROPERTY_CHECKERS) == {c.__name__ for c in ALL_CHECKERS}


def test_unknown_graph_property_raises_keyerror():
    case = DeclarativeCase(
        fixture="synthetic-basic.gxwf.yml",
        operation="layout_format2",
        graph_properties=["not_a_real_property"],
    )
    with pytest.raises(KeyError):
        run_declarative_case(
            case,
            operations={"layout_format2": lambda wf: apply_layout(wf, overwrite=True)},
            load_fixture=load,
            graph_property_checkers=GRAPH_PROPERTY_CHECKERS,
        )


def test_downstream_right_of_upstream_fires_when_target_not_right():
    wf = copy.deepcopy(_BASE)
    wf["steps"]["cat"]["position"]["left"] = 0  # equal, not strictly right
    with pytest.raises(AssertionError):
        downstream_right_of_upstream(wf)


def test_all_nodes_positioned_fires_when_position_missing():
    wf = copy.deepcopy(_BASE)
    del wf["steps"]["cat"]["position"]
    with pytest.raises(AssertionError):
        all_nodes_positioned(wf)


def test_no_position_collisions_fires_on_shared_coordinate():
    wf = copy.deepcopy(_BASE)
    wf["steps"]["cat"]["position"] = {"left": 0, "top": 0}  # collides with input
    with pytest.raises(AssertionError):
        no_position_collisions(wf)


def test_roots_leftmost_fires_when_root_not_leftmost():
    wf = copy.deepcopy(_BASE)
    wf["inputs"]["the_input"]["position"]["left"] = 220
    wf["steps"]["cat"]["position"]["left"] = 0
    with pytest.raises(AssertionError):
        roots_leftmost(wf)


def test_registry_checkers_recurse_into_subworkflows():
    # A broken position inside an embedded subworkflow escapes the base checker
    # (it only sees the top level) but must be caught by the registered checker.
    wf = load("synthetic-tool-with-inline-subworkflow.gxwf.yml")
    apply_layout(wf, overwrite=True)
    wf["steps"]["nested"]["run"]["steps"]["inner_tool"]["position"]["left"] = 0  # collides with input
    base = _BASE_CHECKERS["no_position_collisions"]
    base(wf)  # top level is still fine
    with pytest.raises(AssertionError):
        GRAPH_PROPERTY_CHECKERS["no_position_collisions"](wf)
