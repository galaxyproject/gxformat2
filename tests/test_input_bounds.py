"""Legacy converter emits the same numeric input bounds as the normalized one.

Normalized conversion is covered by declarative cases on
``synthetic-numeric-input-bounds.gxwf.yml`` and ``synthetic-numeric-range-validators.ga``.
"""

import json

from gxformat2.converter import python_to_workflow
from gxformat2.examples import load
from gxformat2.normalized import to_native


def test_legacy_converter_input_bounds_match_normalized():
    workflow = load("synthetic-numeric-input-bounds.gxwf.yml")
    native_steps = to_native(workflow).to_dict()["steps"]
    legacy_steps = python_to_workflow(workflow)["steps"]
    for step_id, native_step in native_steps.items():
        legacy_state = json.loads(legacy_steps[step_id]["tool_state"])
        assert legacy_state["validators"] == native_step["tool_state"]["validators"]
