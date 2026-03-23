"""Load native Galaxy workflow dicts into typed pydantic models.

The auto-generated schema in ``gxformat2.schema.native`` defines strict
pydantic models.  This module sits *outside* the auto-generated code and
provides a ``load_native`` helper that can optionally normalize known
Galaxy serialization quirks before validation.
"""

from __future__ import annotations

from typing import Any

from gxformat2.schema.native import NativeGalaxyWorkflow


def load_native(data: dict[str, Any], *, strict: bool = True) -> NativeGalaxyWorkflow:
    """Load a native Galaxy workflow dict into a :class:`NativeGalaxyWorkflow`.

    Parameters
    ----------
    data:
        Raw workflow dict (e.g. parsed from a ``.ga`` JSON file).
    strict:
        When *True* (default) the dict is validated as-is.  When *False*,
        known Galaxy serialization quirks are normalized before validation
        (e.g. ``tags: ""`` → ``tags: []``).
    """
    if not strict:
        data = _normalize(data)
    return NativeGalaxyWorkflow.model_validate(data)


def _normalize(data: dict[str, Any]) -> dict[str, Any]:
    """Fix known Galaxy serialization quirks in a native workflow dict."""
    data = data.copy()
    _normalize_tags(data)
    if "steps" in data and isinstance(data["steps"], dict):
        steps: dict[str, Any] = {}
        for key, step in data["steps"].items():
            step = _normalize_step(step)
            steps[key] = step
        data["steps"] = steps
    return data


def _normalize_step(step: dict[str, Any]) -> dict[str, Any]:
    """Normalize a single step dict."""
    step = step.copy()
    if step.get("subworkflow") and isinstance(step["subworkflow"], dict):
        step["subworkflow"] = _normalize(step["subworkflow"])
    _normalize_post_job_actions(step)
    return step


def _normalize_post_job_actions(step: dict[str, Any]) -> None:
    """Fix post_job_actions where action_arguments is a scalar instead of dict."""
    pjas = step.get("post_job_actions")
    if not isinstance(pjas, dict):
        return
    normalized = {}
    for key, pja in pjas.items():
        if isinstance(pja, dict):
            args = pja.get("action_arguments")
            if args is not None and not isinstance(args, dict):
                pja = pja.copy()
                pja["action_arguments"] = None
            normalized[key] = pja
        else:
            normalized[key] = pja
    step["post_job_actions"] = normalized


def _normalize_tags(data: dict[str, Any]) -> None:
    """Normalize ``tags`` field in-place on *data*.

    Galaxy sometimes serializes tags as an empty string ``""`` or as a
    comma-separated string instead of a list.
    """
    tags = data.get("tags")
    if isinstance(tags, str):
        data["tags"] = [t.strip() for t in tags.split(",") if t.strip()] if tags else []
