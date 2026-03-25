"""Convenience functions for accessing normalized workflow components.

:func:`steps`, :func:`inputs`, and :func:`outputs` return typed Pydantic
model lists from any workflow representation.  The ``_normalized`` variants
return plain dicts for backward compatibility (used by Planemo).
"""

from __future__ import annotations

from os import PathLike
from typing import Any

from gxformat2.normalized import NormalizedFormat2, NormalizedNativeWorkflow, NormalizedWorkflowStep
from gxformat2.options import ConversionOptions
from gxformat2.schema.gxformat2 import GalaxyWorkflow, WorkflowInputParameter, WorkflowOutputParameter
from gxformat2.schema.native import NativeGalaxyWorkflow
from gxformat2.to_format2 import ensure_format2

# Any input ensure_format2 accepts
Workflow = (
    dict[str, Any]
    | str
    | PathLike
    | NormalizedFormat2
    | NormalizedNativeWorkflow
    | GalaxyWorkflow
    | NativeGalaxyWorkflow
)


# --- Typed model accessors ---------------------------------------------------


def steps(
    workflow_dict: Workflow | None = None,
    workflow_path: str | PathLike | None = None,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> list[WorkflowInputParameter | NormalizedWorkflowStep]:
    """Return input parameters followed by steps as typed models."""
    nf2 = _ensure_format2(workflow_dict, workflow_path, options, expand)
    return list(nf2.inputs) + list(nf2.steps)


def inputs(
    workflow_dict: Workflow | None = None,
    workflow_path: str | PathLike | None = None,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> list[WorkflowInputParameter]:
    """Return normalized inputs as typed models."""
    nf2 = _ensure_format2(workflow_dict, workflow_path, options, expand)
    return list(nf2.inputs)


def outputs(
    workflow_dict: Workflow | None = None,
    workflow_path: str | PathLike | None = None,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> list[WorkflowOutputParameter]:
    """Return normalized outputs as typed models."""
    nf2 = _ensure_format2(workflow_dict, workflow_path, options, expand)
    return list(nf2.outputs)


# --- Deprecated dict accessors (backward compat for Planemo) ------------------


def steps_normalized(
    workflow_dict: Workflow | None = None,
    workflow_path: str | PathLike | None = None,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> list[dict[str, Any]]:
    """Walk over a normalized step rep. across workflow formats.

    .. deprecated:: Use :func:`steps` for typed model access.

    Returns a list of dicts — input steps followed by tool/subworkflow steps.
    """
    nf2 = _ensure_format2(workflow_dict, workflow_path, options, expand)
    return _dump_list(nf2.inputs) + _dump_list(nf2.steps)


def inputs_normalized(
    workflow_dict: Workflow | None = None,
    workflow_path: str | PathLike | None = None,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> list[dict[str, Any]]:
    """Return normalized input steps as dicts.

    .. deprecated:: Use :func:`inputs` for typed model access.
    """
    nf2 = _ensure_format2(workflow_dict, workflow_path, options, expand)
    return _dump_list(nf2.inputs)


def outputs_normalized(
    workflow_dict: Workflow | None = None,
    workflow_path: str | PathLike | None = None,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> list[dict[str, Any]]:
    """Return normalized outputs as dicts.

    .. deprecated:: Use :func:`outputs` for typed model access.
    """
    nf2 = _ensure_format2(workflow_dict, workflow_path, options, expand)
    return _dump_list(nf2.outputs)


# --- Internal -----------------------------------------------------------------


def _dump_list(items) -> list[dict[str, Any]]:
    return [
        item.to_dict() if hasattr(item, "to_dict") else item.model_dump(by_alias=True, exclude_none=True, mode="json")
        for item in items
    ]


def _ensure_format2(
    workflow_dict: Workflow | None,
    workflow_path: str | PathLike | None,
    options: ConversionOptions | None = None,
    expand: bool = False,
) -> NormalizedFormat2:
    workflow = workflow_path or workflow_dict
    if workflow is None:
        raise ValueError("Either workflow_dict or workflow_path must be provided")
    return ensure_format2(workflow, options=options, expand=expand)
