"""Inline ``GalaxyUserTool`` stubs must survive ``_expand_format2`` unchanged."""

from gxformat2.examples import load
from gxformat2.normalized import (
    ensure_format2,
    ExpandedFormat2,
)
from gxformat2.normalized._format2 import GalaxyUserToolStub


class TestExpandInlineUserTool:
    def test_user_tool_stub_passes_through_expansion(self):
        wf = ensure_format2(load("synthetic-user-defined-tool.gxwf.yml"), expand=True)
        step = wf.steps[0]
        assert isinstance(step.run, GalaxyUserToolStub)
        assert step.run.id == "cat_user_defined"
        assert step.run.version == "0.1"

    def test_user_tool_stub_does_not_recurse_as_workflow(self):
        wf = ensure_format2(load("synthetic-user-defined-tool.gxwf.yml"), expand=True)
        step = wf.steps[0]
        assert not isinstance(step.run, ExpandedFormat2)
        assert step.run is not None

    def test_user_tool_stub_no_expand_remains_stub(self):
        wf = ensure_format2(load("synthetic-user-defined-tool.gxwf.yml"))
        step = wf.steps[0]
        assert isinstance(step.run, GalaxyUserToolStub)
        assert step.run.id == "cat_user_defined"

    def test_user_tool_inside_subworkflow_expands(self):
        outer = {
            "class": "GalaxyWorkflow",
            "inputs": {"x": "data"},
            "outputs": {},
            "steps": {
                "inner": {
                    "run": {
                        "class": "GalaxyWorkflow",
                        "inputs": {"x": "data"},
                        "outputs": {},
                        "steps": {
                            "tool_step": {
                                "run": {
                                    "class": "GalaxyUserTool",
                                    "id": "cat_user_defined",
                                    "version": "0.1",
                                    "name": "cat_user_defined",
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
                                "in": {"input1": "x"},
                            }
                        },
                    },
                    "in": {"x": "x"},
                }
            },
        }
        wf = ensure_format2(outer, expand=True)
        inner = wf.steps[0].run
        assert isinstance(inner, ExpandedFormat2)
        tool_step = inner.steps[0]
        assert isinstance(tool_step.run, GalaxyUserToolStub)
        assert tool_step.run.id == "cat_user_defined"
