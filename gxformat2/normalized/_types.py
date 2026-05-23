"""Shared types for normalized workflow models."""

from typing import NamedTuple, Optional


class ToolReference(NamedTuple):
    """A unique tool identity within a workflow."""

    tool_id: str
    tool_version: Optional[str]


INLINE_TOOL_CLASSES: tuple[str, ...] = ("GalaxyUserTool",)
"""Workflow-step ``run`` / ``tool_representation`` class names that identify an embedded inline tool.

Currently only ``GalaxyUserTool`` (per-user dynamic tools) is supported end-to-end;
admin ``GalaxyTool`` representations may join this tuple once converter/validator
support is in place.
"""
