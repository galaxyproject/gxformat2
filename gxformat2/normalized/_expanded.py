"""Expanded workflow models with all references resolved.

These models inherit from the normalized models and narrow ``run`` /
``subworkflow`` fields to guarantee all external references have been
resolved to inline workflow definitions.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from pydantic import Field

from gxformat2.options import (
    ConversionOptions,
    default_url_resolver,
    MAX_EXPANSION_DEPTH,
)

from ._format2 import normalized_format2, NormalizedFormat2, NormalizedWorkflowStep
from ._native import normalized_native, NormalizedNativeStep, NormalizedNativeWorkflow

log = logging.getLogger(__name__)


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


class _ExpansionContext:
    """Internal context for tracking cycle detection during expansion."""

    def __init__(self, options: ConversionOptions, resolving_urls: frozenset[str] = frozenset()):
        self.options = options
        self._resolving_urls = resolving_urls
        self._resolver = options.url_resolver or default_url_resolver

    def resolve_url(self, url: str) -> dict[str, Any]:
        if url in self._resolving_urls:
            raise ValueError(f"Circular subworkflow reference: {url}")
        if len(self._resolving_urls) >= MAX_EXPANSION_DEPTH:
            raise ValueError(f"Max expansion depth ({MAX_EXPANSION_DEPTH}) exceeded")
        return self._resolver(url)

    def resolve_import(self, path: str) -> dict[str, Any]:
        if self.options.workflow_directory is None:
            raise ValueError(f"Cannot resolve @import '{path}' without workflow_directory")
        from gxformat2.yaml import ordered_load_path

        full_path = os.path.join(self.options.workflow_directory, path)
        return ordered_load_path(full_path)

    def child(self, url: str) -> _ExpansionContext:
        return _ExpansionContext(self.options, self._resolving_urls | {url})


def expanded_format2(
    workflow: dict[str, Any] | str | Path | NormalizedFormat2,
    options: ConversionOptions | None = None,
) -> ExpandedFormat2:
    """Normalize and expand a Format2 workflow, resolving all references.

    Resolves ``@import``, URL, and TRS URL references in step ``run``
    fields.  Uses ``options.url_resolver`` (or the built-in default) for
    HTTP fetches.
    """
    options = options or ConversionOptions(expand=True)
    if not isinstance(workflow, NormalizedFormat2):
        workflow = normalized_format2(workflow)
    ctx = _ExpansionContext(options)
    return _expand_format2(workflow, ctx)


def expanded_native(
    workflow: dict[str, Any] | str | Path | NormalizedNativeWorkflow,
    options: ConversionOptions | None = None,
) -> ExpandedNativeWorkflow:
    """Normalize and expand a native workflow, resolving all subworkflow references.

    Resolves ``content_id`` URL references by fetching and converting
    them.  Uses ``options.url_resolver`` (or the built-in default) for
    HTTP fetches.
    """
    options = options or ConversionOptions(expand=True)
    if not isinstance(workflow, NormalizedNativeWorkflow):
        workflow = normalized_native(workflow)
    ctx = _ExpansionContext(options)
    return _expand_native(workflow, ctx)


def _expand_format2(wf: NormalizedFormat2, ctx: _ExpansionContext) -> ExpandedFormat2:
    expanded_steps: list[ExpandedWorkflowStep] = []
    for step in wf.steps:
        expanded_run: ExpandedFormat2 | None = None
        if isinstance(step.run, NormalizedFormat2):
            expanded_run = _expand_format2(step.run, ctx)
        elif isinstance(step.run, str):
            resolved = _resolve_run_reference(step.run, ctx)
            child_ctx = ctx.child(step.run)
            normalized = normalized_format2(resolved)
            expanded_run = _expand_format2(normalized, child_ctx)
        elif isinstance(step.run, dict):
            if "@import" in step.run:
                resolved = ctx.resolve_import(step.run["@import"])
            else:
                resolved = step.run
            child_ctx = ctx.child(str(step.run.get("@import", id(step.run))))
            normalized = normalized_format2(resolved)
            expanded_run = _expand_format2(normalized, child_ctx)

        step_data = step.model_dump(by_alias=True, exclude={"run"})
        expanded_steps.append(ExpandedWorkflowStep(**step_data, run=expanded_run))

    wf_data = wf.model_dump(by_alias=True, exclude={"steps"})
    return ExpandedFormat2(**wf_data, steps=expanded_steps)


def _expand_native(wf: NormalizedNativeWorkflow, ctx: _ExpansionContext) -> ExpandedNativeWorkflow:
    expanded_steps: dict[str, ExpandedNativeStep] = {}
    for key, step in wf.steps.items():
        expanded_sub: ExpandedNativeWorkflow | None = None
        if step.subworkflow is not None:
            expanded_sub = _expand_native(step.subworkflow, ctx)
        elif step.content_id and _is_resolvable_url(step.content_id):
            try:
                resolved = ctx.resolve_url(step.content_id)
                child_ctx = ctx.child(step.content_id)
                # Fetched content could be native or format2 — detect and normalize
                if resolved.get("a_galaxy_workflow") == "true":
                    normalized = normalized_native(resolved)
                else:
                    # Format2 content fetched for native expansion —
                    # cross-format conversion not yet supported here.
                    log.warning(
                        "Fetched format2 workflow from %s for native expansion — "
                        "cross-format expansion not yet supported, leaving as reference",
                        step.content_id,
                    )
                    step_data = step.model_dump(by_alias=True)
                    expanded_steps[key] = ExpandedNativeStep(**step_data)
                    continue
                expanded_sub = _expand_native(normalized, child_ctx)
            except Exception:
                log.warning("Failed to resolve %s, leaving as reference", step.content_id, exc_info=True)
                step_data = step.model_dump(by_alias=True)
                expanded_steps[key] = ExpandedNativeStep(**step_data)
                continue

        step_data = step.model_dump(by_alias=True, exclude={"subworkflow"})
        if expanded_sub is not None:
            step_data.pop("content_id", None)
        expanded_steps[key] = ExpandedNativeStep(**step_data, subworkflow=expanded_sub)

    # Expand subworkflows dict too
    expanded_subworkflows: dict[str, ExpandedNativeWorkflow] | None = None
    if wf.subworkflows:
        expanded_subworkflows = {k: _expand_native(v, ctx) for k, v in wf.subworkflows.items()}

    wf_data = wf.model_dump(by_alias=True, exclude={"steps", "subworkflows"})
    return ExpandedNativeWorkflow(**wf_data, steps=expanded_steps, subworkflows=expanded_subworkflows)


def _resolve_run_reference(url: str, ctx: _ExpansionContext) -> dict[str, Any]:
    """Resolve a URL run reference to a workflow dict."""
    return ctx.resolve_url(url)


def _is_resolvable_url(content_id: str) -> bool:
    """Check if a content_id is a URL that can be fetched."""
    return content_id.startswith(("http://", "https://", "base64://"))
