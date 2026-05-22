"""Inline-tool step helpers on ``NormalizedNativeStep`` and ``NormalizedWorkflowStep``."""

from gxformat2.examples import load
from gxformat2.normalized import (
    ensure_format2,
    normalized_native,
    NormalizedNativeStep,
    NormalizedWorkflowStep,
)
from gxformat2.normalized._format2 import GalaxyUserToolStub


def _native_step_with_representation(class_: str) -> NormalizedNativeStep:
    return NormalizedNativeStep.model_validate(
        {
            "id": 0,
            "type": "tool",
            "tool_representation": {
                "class": class_,
                "id": "cat_user_defined",
                "version": "0.1",
                "name": "cat_user_defined",
                "container": "busybox",
                "shell_command": "cat '$(inputs.input1.path)' > output.txt",
                "inputs": [{"name": "input1", "type": "data", "format": "txt"}],
                "outputs": [
                    {"name": "output1", "type": "data", "format": "txt", "from_work_dir": "output.txt"}
                ],
            },
        }
    )


class TestNormalizedNativeStepInlineHelpers:
    def test_is_inline_tool_step_user_tool(self):
        step = _native_step_with_representation("GalaxyUserTool")
        assert step.is_inline_tool_step
        assert step.inline_tool_class == "GalaxyUserTool"

    def test_is_inline_tool_step_admin_tool(self):
        step = _native_step_with_representation("GalaxyTool")
        assert step.is_inline_tool_step
        assert step.inline_tool_class == "GalaxyTool"

    def test_is_inline_tool_step_false_when_no_representation(self):
        step = NormalizedNativeStep.model_validate(
            {"id": 0, "type": "tool", "tool_id": "cat", "tool_version": "1.0"}
        )
        assert not step.is_inline_tool_step
        assert step.inline_tool_class is None

    def test_is_inline_tool_step_false_when_unrelated_class(self):
        step = NormalizedNativeStep.model_validate(
            {"id": 0, "type": "tool", "tool_representation": {"class": "GalaxyWorkflow"}}
        )
        assert not step.is_inline_tool_step
        assert step.inline_tool_class == "GalaxyWorkflow"


class TestNormalizedWorkflowStepInlineHelpers:
    def test_user_tool_stub_recognized(self):
        wf = ensure_format2(load("synthetic-user-defined-tool.gxwf.yml"))
        step = wf.steps[0]
        assert step.is_inline_tool_step
        assert isinstance(step.run, GalaxyUserToolStub)
        rep = step.inline_tool_representation
        assert rep is not None
        assert rep["class"] == "GalaxyUserTool"
        assert rep["id"] == "cat_user_defined"

    def test_inline_tool_representation_excludes_none(self):
        wf = ensure_format2(load("synthetic-user-defined-tool.gxwf.yml"))
        rep = wf.steps[0].inline_tool_representation
        assert rep is not None
        assert all(v is not None for v in rep.values())

    def test_subworkflow_step_is_not_inline_tool(self):
        outer = {
            "class": "GalaxyWorkflow",
            "inputs": {"x": "data"},
            "outputs": {},
            "steps": {
                "sub": {
                    "run": {"class": "GalaxyWorkflow", "inputs": {"x": "data"}, "outputs": {}, "steps": {}},
                    "in": {"x": "x"},
                }
            },
        }
        wf = ensure_format2(outer)
        assert not wf.steps[0].is_inline_tool_step
        assert wf.steps[0].inline_tool_representation is None

    def test_tool_id_step_is_not_inline_tool(self):
        step = NormalizedWorkflowStep.model_validate({"id": "s1", "type": "tool", "tool_id": "cat"})
        assert not step.is_inline_tool_step
        assert step.inline_tool_representation is None

    def test_none_run_is_not_inline_tool(self):
        step = NormalizedWorkflowStep.model_validate({"id": "s1", "type": "tool"})
        assert not step.is_inline_tool_step
        assert step.inline_tool_representation is None
