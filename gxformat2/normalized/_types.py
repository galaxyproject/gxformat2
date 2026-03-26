"""Shared types for normalized workflow models."""

from typing import NamedTuple, Optional


class ToolReference(NamedTuple):
    """A unique tool identity within a workflow."""

    tool_id: str
    tool_version: Optional[str]
