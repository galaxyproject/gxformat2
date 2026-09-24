"""Round-trip lock for inline ``GalaxyUserTool`` steps across native ↔ format2."""

import copy

from gxformat2.examples import load
from gxformat2.normalized import (
    to_format2,
    to_native,
)
from gxformat2.normalized._format2 import GalaxyUserToolStub

SYNTHETIC_NATIVE_UDT = {
    "a_galaxy_workflow": "true",
    "format-version": "0.1",
    "name": "synthetic-udt",
    "steps": {
        "0": {
            "id": 0,
            "type": "data_input",
            "label": "the_input",
            "tool_state": {},
            "inputs": [{"name": "the_input", "description": ""}],
            "outputs": [],
        },
        "1": {
            "id": 1,
            "type": "tool",
            "label": "my_tool",
            "name": "cat_user_defined",
            "tool_state": {},
            "input_connections": {"input1": {"id": 0, "output_name": "output"}},
            "inputs": [],
            "outputs": [],
            "tool_representation": {
                "class": "GalaxyUserTool",
                "id": "cat_user_defined",
                "version": "0.1",
                "name": "cat_user_defined",
                "description": "concatenates a file",
                "container": "busybox",
                "shell_command": "cat '$(inputs.input1.path)' > output.txt",
                "inputs": [{"name": "input1", "type": "data", "format": "txt"}],
                "outputs": [
                    {
                        "name": "output1",
                        "type": "data",
                        "format": "txt",
                        "from_work_dir": "output.txt",
                    }
                ],
            },
        },
    },
}


def _udt_step(native_dict):
    return next(s for s in native_dict["steps"].values() if s.get("type") == "tool")


class TestInlineToolRoundTrip:
    def test_native_to_format2_to_native_preserves_tool_representation(self):
        original = copy.deepcopy(SYNTHETIC_NATIVE_UDT)
        original_rep = _udt_step(original)["tool_representation"]

        f2 = to_format2(copy.deepcopy(SYNTHETIC_NATIVE_UDT))
        tool_step = next(s for s in f2.steps if s.is_inline_tool_step)
        assert isinstance(tool_step.run, GalaxyUserToolStub)
        assert tool_step.run.class_ == "GalaxyUserTool"

        roundtripped = to_native(f2.to_dict())
        rt_rep = next(s.tool_representation for s in roundtripped.steps.values() if s.tool_representation is not None)
        assert rt_rep == original_rep

    def test_format2_to_native_to_format2_preserves_user_tool_stub(self):
        wf_dict = load("synthetic-user-defined-tool.gxwf.yml")
        original = copy.deepcopy(wf_dict)
        original_run = original["steps"]["my_tool"]["run"]

        native = to_native(wf_dict)
        rt_rep = next(s.tool_representation for s in native.steps.values() if s.tool_representation is not None)
        assert rt_rep == original_run

        f2 = to_format2(native.to_dict())
        tool_step = next(s for s in f2.steps if s.is_inline_tool_step)
        rep = tool_step.inline_tool_representation
        assert rep == original_run

    def test_format2_to_native_to_format2_preserves_state_and_when(self):
        wf_dict = load("synthetic-user-defined-tool.gxwf.yml")
        step = wf_dict["steps"]["my_tool"]
        step["run"]["inputs"].append({"name": "n_lines", "type": "integer"})
        step["state"] = {"n_lines": 5}
        step["when"] = "$(inputs.n_lines > 0)"

        native = to_native(wf_dict)
        native_step = next(s for s in native.steps.values() if s.tool_representation is not None)
        assert native_step.tool_state == {"__page__": 0, "n_lines": 5}

        f2 = to_format2(native.to_dict())
        tool_step = next(s for s in f2.steps if s.is_inline_tool_step)
        assert tool_step.tool_id is None
        assert tool_step.tool_state == {"n_lines": 5}
        assert tool_step.when == "$(inputs.n_lines > 0)"

    def test_native_to_format2_preserves_step_fields(self):
        native = copy.deepcopy(SYNTHETIC_NATIVE_UDT)
        udt_step = _udt_step(native)
        udt_step["tool_state"] = {"__page__": 0, "__rerun_remap_job_id__": None, "n_lines": 5}
        udt_step["when"] = "$(inputs.n_lines > 0)"
        udt_step["uuid"] = "8d4e0e2c-7a6b-4f3e-9c1d-2b5a6f7e8d90"
        udt_step["errors"] = "tool is not installed"

        f2 = to_format2(native)
        tool_step = next(s for s in f2.steps if s.is_inline_tool_step)
        assert tool_step.tool_state == {"n_lines": 5}
        assert tool_step.when == "$(inputs.n_lines > 0)"
        assert tool_step.uuid == "8d4e0e2c-7a6b-4f3e-9c1d-2b5a6f7e8d90"
        assert tool_step.errors == "tool is not installed"

    def test_native_to_format2_omits_empty_tool_state(self):
        f2 = to_format2(copy.deepcopy(SYNTHETIC_NATIVE_UDT))
        tool_step = next(s for s in f2.steps if s.is_inline_tool_step)
        assert tool_step.tool_state is None

    def test_round_trip_is_idempotent(self):
        """A second native→format2→native pass must yield the same tool_representation."""
        first = to_format2(SYNTHETIC_NATIVE_UDT)
        first_native = to_native(first.to_dict())
        second = to_format2(first_native.to_dict())
        second_native = to_native(second.to_dict())

        first_rep = next(
            s.tool_representation for s in first_native.steps.values() if s.tool_representation is not None
        )
        second_rep = next(
            s.tool_representation for s in second_native.steps.values() if s.tool_representation is not None
        )
        assert first_rep == second_rep
