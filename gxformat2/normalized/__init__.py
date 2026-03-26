"""Normalized and expanded workflow models with fully resolved types.

These models sit above the auto-generated pydantic schema models and
provide uniform, narrowed types suitable for downstream consumers that
want typed access without handling representational flexibility.
"""

from ._conversion import (
    ensure_format2,
    ensure_native,
    expanded_format2,
    expanded_native,
    ExpandedFormat2,
    ExpandedNativeStep,
    ExpandedNativeWorkflow,
    ExpandedWorkflowStep,
    INPUT_STEP_TYPES,
    native_input_to_format2_type,
    POST_JOB_ACTIONS,
    to_format2,
    to_native,
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
    "ensure_format2",
    "ensure_native",
    "expanded_format2",
    "expanded_native",
    "ExpandedFormat2",
    "ExpandedNativeStep",
    "ExpandedNativeWorkflow",
    "ExpandedWorkflowStep",
    "INPUT_STEP_TYPES",
    "native_input_to_format2_type",
    "NormalizedFormat2",
    "NormalizedNativeStep",
    "NormalizedNativeWorkflow",
    "NormalizedWorkflowStep",
    "POST_JOB_ACTIONS",
    "SourceReference",
    "normalized_format2",
    "normalized_native",
    "resolve_source_reference",
    "to_format2",
    "to_native",
)
