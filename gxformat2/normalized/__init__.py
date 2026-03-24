"""Normalized and expanded workflow models with fully resolved types.

These models sit above the auto-generated pydantic schema models and
provide uniform, narrowed types suitable for downstream consumers that
want typed access without handling representational flexibility.
"""

from ._expanded import (
    expanded_format2,
    expanded_native,
    ExpandedFormat2,
    ExpandedNativeStep,
    ExpandedNativeWorkflow,
    ExpandedWorkflowStep,
)
from ._format2 import (
    normalized_format2,
    NormalizedFormat2,
    NormalizedWorkflowStep,
    resolve_source_reference,
    SourceReference,
)
from ._native import (
    normalized_native,
    NormalizedNativeStep,
    NormalizedNativeWorkflow,
)

__all__ = (
    "expanded_format2",
    "expanded_native",
    "ExpandedFormat2",
    "ExpandedNativeStep",
    "ExpandedNativeWorkflow",
    "ExpandedWorkflowStep",
    "NormalizedFormat2",
    "NormalizedNativeStep",
    "NormalizedNativeWorkflow",
    "NormalizedWorkflowStep",
    "SourceReference",
    "normalized_format2",
    "normalized_native",
    "resolve_source_reference",
)
