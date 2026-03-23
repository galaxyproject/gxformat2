"""Expanded workflow models with all references resolved.

These models inherit from the normalized models and narrow ``run`` /
``subworkflow`` fields to guarantee all external references have been
resolved to inline workflow definitions.
"""

from __future__ import annotations

from pydantic import Field

from ._format2 import NormalizedFormat2, NormalizedWorkflowStep
from ._native import NormalizedNativeStep, NormalizedNativeWorkflow


class ExpandedWorkflowStep(NormalizedWorkflowStep):
    """Format2 step with run fully resolved."""

    run: ExpandedFormat2 | None = Field(default=None, description="Always resolved or absent.")


class ExpandedFormat2(NormalizedFormat2):
    """Format2 workflow with all references expanded."""

    steps: list[ExpandedWorkflowStep] = Field(default_factory=list)


class ExpandedNativeStep(NormalizedNativeStep):
    """Native step with subworkflow references resolved."""

    subworkflow: ExpandedNativeWorkflow | None = Field(default=None)


class ExpandedNativeWorkflow(NormalizedNativeWorkflow):
    """Native workflow with all subworkflow references resolved."""

    steps: dict[str, ExpandedNativeStep] = Field(default_factory=dict)


ExpandedWorkflowStep.model_rebuild()
ExpandedFormat2.model_rebuild()
ExpandedNativeStep.model_rebuild()
ExpandedNativeWorkflow.model_rebuild()
