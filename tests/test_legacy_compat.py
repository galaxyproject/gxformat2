"""Negative tests for ConversionOptions.legacy_compat=False (issue #205).

When legacy_compat is off, the legacy aliases the pre-rewrite converter
accepted are not normalized away.  Most produce a ValidationError; the
``$link`` int case loses its source resolution silently.
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from gxformat2.examples import load
from gxformat2.normalized import normalized_format2


def _lc_off(name: str):
    return normalized_format2(load(name), legacy_compat=False)


def test_outputs_alias_dropped_without_compat():
    # extra="allow" keeps the key but _normalize_step never reads it
    n = _lc_off("synthetic-legacy-outputs-alias.gxwf.yml")
    assert n.steps[0].out == []


def test_step_form_input_rejected_without_compat():
    # ``type: input`` is not a valid WorkflowStepType -- pydantic rejects.
    with pytest.raises(ValidationError):
        _lc_off("synthetic-legacy-step-form-input.gxwf.yml")


def test_int_link_still_works_without_compat():
    # C is fixed unconditionally (schema bug, not legacy alias).
    n = _lc_off("synthetic-legacy-int-link.gxwf.yml")
    assert n.steps[0].in_[0].source == "0"


def test_float_tool_version_rejected_without_compat():
    with pytest.raises(ValidationError):
        _lc_off("synthetic-legacy-float-tool-version.gxwf.yml")


def test_list_source_still_works_without_compat():
    # F is fixed unconditionally (schema permits the form via mapPredicate: source).
    n = _lc_off("synthetic-legacy-list-source.gxwf.yml")
    assert n.steps[0].in_[0].source == ["input1", "input2"]
