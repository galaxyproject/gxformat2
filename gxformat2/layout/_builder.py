"""Compute and apply node positions for Galaxy workflows.

The coordinates come from the cross-language topological layout in
``gxformat2.cytoscape`` so they match ``gxwf-viz --layout topological`` and
the TypeScript port. This module turns those coordinates into ``position``
records (``{left, top}``) merged back into a workflow document, replacing the
degenerate ``(10*i, 10*i)`` diagonal fallback from
``gxformat2.model.ensure_step_position``.

See galaxyproject/galaxy#22954.
"""

from __future__ import annotations

import copy
from pathlib import Path
from typing import Any, Optional, Union

from gxformat2._labels import unlabeled_node_id
from gxformat2.cytoscape import cytoscape_elements, topological_positions
from gxformat2.layout._sugiyama import check_acyclic, layered_positions
from gxformat2.normalized import ensure_format2, NormalizedFormat2
from gxformat2.normalized._conversion import INPUT_STEP_TYPES
from gxformat2.schema.gxformat2 import GalaxyWorkflow

#: Sentinel value for ``position:`` that requests automatic layout.
AUTO = "auto"

WorkflowInput = Union[dict, str, Path, GalaxyWorkflow, NormalizedFormat2]


def layout_positions(workflow: WorkflowInput, *, strategy: str = "topological") -> dict[str, dict[str, int]]:
    """Compute node positions keyed by node id.

    Node ids are Format2 input ids / step labels (the same ids the Cytoscape
    builder emits). Values are ``{"left": x, "top": y}`` integer records.

    Accepts anything ``ensure_format2()`` supports, plus an already normalized
    ``NormalizedFormat2`` instance.
    """
    if strategy not in ("topological", "layered"):
        raise ValueError(f'Unknown layout strategy "{strategy}". Valid values: topological, layered.')

    if isinstance(workflow, NormalizedFormat2):
        nf2 = workflow
    else:
        # Strip positions first: the layout strategies ignore them, and an
        # ``auto`` sentinel would fail schema validation in ensure_format2.
        if isinstance(workflow, dict):
            workflow = _strip_positions(workflow)
        nf2 = ensure_format2(workflow)

    elements = cytoscape_elements(nf2, layout="preset")
    if strategy == "topological":
        # Cycles are invalid in Galaxy; refuse rather than bake garbage
        # positions. cytoscape.topological_positions has a silent diagonal
        # fallback for cyclic graphs (it must stay resilient for the viz path),
        # so we detect up front here. ``layered`` raises during layering.
        check_acyclic(elements)
        positions = topological_positions(elements)
    else:  # layered
        positions = layered_positions(elements)
    return {node_id: {"left": p.x, "top": p.y} for node_id, p in positions.items()}


def _is_native(workflow: dict) -> bool:
    return workflow.get("a_galaxy_workflow") == "true"


def _strip_positions(workflow: dict) -> dict:
    """Return a deep copy with all ``position`` records removed.

    Used to feed ensure_format2 a document free of ``auto`` sentinels (which
    are not valid positions). Topological layout does not read positions.
    """
    cleaned = copy.deepcopy(workflow)
    container_keys = ("steps",) if _is_native(cleaned) else ("inputs", "steps")
    for container_key in container_keys:
        container = cleaned.get(container_key)
        items = container.values() if isinstance(container, dict) else container
        for item in items or []:
            if isinstance(item, dict):
                item.pop("position", None)
    return cleaned


def _should_write(existing: Any, overwrite: bool) -> bool:
    """Decide whether to write a position given any existing value.

    - missing -> write
    - ``auto`` sentinel -> always write
    - explicit mapping -> write only when ``overwrite``
    """
    if existing is None:
        return True
    if existing == AUTO:
        return True
    return overwrite


def _ensure_mapping(value: Any) -> dict:
    """Coerce a Format2 shorthand value (e.g. ``data``) into mapping form."""
    if isinstance(value, dict):
        return value
    return {"type": value}


def _format2_node_id(item: Any, key: Optional[str], *, is_input: bool) -> Optional[str]:
    """Id cytoscape assigns to a Format2 node, used to match computed positions.

    Mirrors ``cytoscape._builder``: inputs are identified by id, steps by
    label-then-id. In the dict container form that id is the mapping ``key``;
    only the list form has to read it off the item. Single derivation so the
    dict and list paths cannot disagree with each other or with cytoscape.
    """
    if key is not None:
        return key
    if is_input:
        return item.get("id")
    return item.get("label") or item.get("id")


def _apply_to_container(
    container: Any, positions: dict[str, dict[str, int]], overwrite: bool, *, is_input: bool
) -> Any:
    """Merge positions into a Format2 inputs/steps container (dict or list).

    Returns the (possibly replaced) container. Mutates in place where possible
    so ruamel ``CommentedMap`` documents keep their comments.
    """
    if isinstance(container, dict):
        for key in list(container.keys()):
            node_id = _format2_node_id(container[key], key, is_input=is_input)
            pos = positions.get(node_id) if node_id is not None else None
            if pos is None:
                continue
            value = _ensure_mapping(container[key])
            if _should_write(value.get("position"), overwrite):
                value["position"] = dict(pos)
            container[key] = value
        return container
    if isinstance(container, list):
        for item in container:
            if not isinstance(item, dict):
                continue
            node_id = _format2_node_id(item, None, is_input=is_input)
            pos = positions.get(node_id) if node_id is not None else None
            if pos is None:
                continue
            if _should_write(item.get("position"), overwrite):
                item["position"] = dict(pos)
        return container
    return container


def _apply_format2(workflow: dict, positions: dict[str, dict[str, int]], overwrite: bool) -> dict:
    for container_key in ("inputs", "steps"):
        container = workflow.get(container_key)
        if container is None:
            continue
        workflow[container_key] = _apply_to_container(
            container, positions, overwrite, is_input=container_key == "inputs"
        )
    return workflow


def _native_node_id(key: str, step: dict) -> str:
    """Reproduce the node id ensure_format2 assigns to a native step.

    Shares ``unlabeled_node_id`` with the native→Format2 conversion so the two
    cannot drift.
    """
    return unlabeled_node_id(step.get("label"), step.get("id", key), step.get("type") in INPUT_STEP_TYPES)


def _apply_native(workflow: dict, positions: dict[str, dict[str, int]], overwrite: bool) -> dict:
    steps = workflow.get("steps")
    if not isinstance(steps, dict):
        return workflow
    for key, step in steps.items():
        if not isinstance(step, dict):
            continue
        pos = positions.get(_native_node_id(key, step))
        if pos is None:
            continue
        if _should_write(step.get("position"), overwrite):
            step["position"] = dict(pos)
    return workflow


def apply_layout(workflow: dict, *, strategy: str = "topological", overwrite: bool = False) -> dict:
    """Merge computed positions into a workflow document, mutating it in place.

    Works on both Format2 and native (``a_galaxy_workflow``) dicts. Existing
    explicit positions are preserved unless ``overwrite`` is True; a
    ``position: auto`` sentinel is always replaced. Returns ``workflow``.

    ``workflow`` must be a dict (the CLI loads files to dicts before calling
    this, so the ``auto`` sentinel is handled). Only top-level nodes are laid
    out; nested subworkflow steps are treated as single nodes, matching the
    Cytoscape builder.
    """
    positions = layout_positions(workflow, strategy=strategy)
    if _is_native(workflow):
        return _apply_native(workflow, positions, overwrite)
    return _apply_format2(workflow, positions, overwrite)
