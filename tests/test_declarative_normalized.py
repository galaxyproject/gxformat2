"""Declarative normalization tests driven by YAML expectation files.

Expectation files live in gxformat2/examples/expectations/.
Each file contains named test cases with a fixture, operation, and assertions.
Assertions use path-value pairs navigated against the normalized workflow object.

Path element types:
  - str: dict key lookup (falls back to attribute access)
  - int: list index
  - "$length": terminal, returns len(current object)
  - {field: value}: find first list item where item.field == value

Assertion modes:
  - value: exact equality (None, str, int, list, dict)
  - value_contains: substring containment check (str in str)
  - value_set: unordered set comparison; each item is a flat {key: value} dict
    compared against NamedTuple._asdict() or plain set membership

Special case:
  - assertions may be omitted or empty: operation succeeding is the test
  - expect_error: true: operation must raise an exception
"""

import os
from typing import Any

import pytest
import yaml

from gxformat2.examples import EXAMPLES_DIR, load
from gxformat2.lint import lint_format2 as _lint_format2_impl
from gxformat2.lint import lint_ga as _lint_ga_impl
from gxformat2.linting import LintContext
from gxformat2.normalized import (
    ensure_format2,
    ensure_native,
    expanded_format2,
    expanded_native,
    normalized_format2,
    normalized_native,
    to_format2,
    to_native,
)
from gxformat2.schema.gxformat2 import GalaxyWorkflow as Format2Lax
from gxformat2.schema.gxformat2_strict import GalaxyWorkflow as Format2Strict
from gxformat2.schema.native import NativeGalaxyWorkflow as NativeLax
from gxformat2.schema.native_strict import NativeGalaxyWorkflow as NativeStrict


def _validate_format2(wf_dict):
    return Format2Lax.model_validate(wf_dict)


def _validate_format2_strict(wf_dict):
    return Format2Strict.model_validate(wf_dict)


def _validate_native(wf_dict):
    return NativeLax.model_validate(wf_dict)


def _validate_native_strict(wf_dict):
    return NativeStrict.model_validate(wf_dict)


def _lint_format2(wf_dict):
    nf2 = ensure_format2(wf_dict, expand=True)
    ctx = LintContext()
    _lint_format2_impl(ctx, nf2, raw_dict=wf_dict)
    return {
        "errors": ctx.error_messages,
        "warnings": ctx.warn_messages,
        "error_count": len(ctx.error_messages),
        "warn_count": len(ctx.warn_messages),
    }


def _lint_native(wf_dict):
    nnw = ensure_native(wf_dict)
    ctx = LintContext()
    _lint_ga_impl(ctx, nnw, raw_dict=wf_dict)
    return {
        "errors": ctx.error_messages,
        "warnings": ctx.warn_messages,
        "error_count": len(ctx.error_messages),
        "warn_count": len(ctx.warn_messages),
    }


EXPECTATIONS_DIR = os.path.join(EXAMPLES_DIR, "expectations")
OPERATIONS = {
    "normalized_format2": normalized_format2,
    "normalized_native": normalized_native,
    "expanded_format2": expanded_format2,
    "expanded_native": expanded_native,
    "to_format2": to_format2,
    "to_native": to_native,
    "ensure_format2": ensure_format2,
    "ensure_native": ensure_native,
    "validate_format2": _validate_format2,
    "validate_format2_strict": _validate_format2_strict,
    "validate_native": _validate_native,
    "validate_native_strict": _validate_native_strict,
    "lint_format2": _lint_format2,
    "lint_native": _lint_native,
}


def _load_expectations():
    """Yield (test_id, case_dict) for every expectation YAML in the directory."""
    for fname in sorted(os.listdir(EXPECTATIONS_DIR)):
        if not fname.endswith(".yml"):
            continue
        with open(os.path.join(EXPECTATIONS_DIR, fname)) as f:
            suite = yaml.safe_load(f)
        if not suite:
            continue
        for test_id, case in suite.items():
            yield test_id, case


def _navigate(obj: Any, path: list) -> Any:
    """Walk an object by a list of path elements."""
    for element in path:
        if element == "$length":
            return len(obj)
        elif isinstance(element, dict):
            field, value = next(iter(element.items()))
            obj = next(item for item in obj if getattr(item, field) == value)
        elif isinstance(element, int):
            obj = obj[element]
        elif isinstance(element, str):
            if isinstance(obj, dict):
                obj = obj[element]
            else:
                if not hasattr(obj, element):
                    raise AttributeError(f"{type(obj).__name__} has no attribute {element!r}")
                obj = getattr(obj, element)
        else:
            raise TypeError(f"Unexpected path element: {element!r}")
    return obj


def _assert_value(obj: Any, expected: Any):
    """Assert exact equality."""
    assert obj == expected, f"expected {expected!r}, got {obj!r}"


def _assert_value_contains(obj: Any, expected: str):
    """Assert that expected is a substring of obj."""
    assert expected in obj, f"expected {expected!r} in {obj!r}"


def _assert_value_set(obj: Any, expected_items: list):
    """Assert unordered set equality.

    For frozensets of NamedTuples (e.g. unique_tools): converts each item via
    _asdict() and compares as sets of frozen key-value pairs.
    For frozensets of primitives (e.g. connected_paths): plain set comparison.
    """
    if isinstance(obj, frozenset):
        if not expected_items:
            assert obj == frozenset(), f"expected empty set, got {obj!r}"
        elif hasattr(next(iter(obj)), "_asdict"):
            actual = {tuple(sorted(item._asdict().items())) for item in obj}
            expected = {tuple(sorted(d.items())) for d in expected_items}
            assert actual == expected, f"expected {expected_items!r}, got {obj!r}"
        else:
            assert obj == frozenset(expected_items), f"expected {expected_items!r}, got {obj!r}"
    else:
        assert set(obj) == set(expected_items), f"expected {expected_items!r}, got {obj!r}"


_ALL_CASES = list(_load_expectations())


@pytest.mark.parametrize(
    "test_id,case",
    _ALL_CASES,
    ids=[c[0] for c in _ALL_CASES],
)
def test_declarative(test_id, case):
    fixture = case["fixture"]
    operation = OPERATIONS[case["operation"]]
    expect_error = case.get("expect_error", False)

    if expect_error:
        with pytest.raises(Exception, match=r".+"):
            operation(load(fixture))
        return

    wf = operation(load(fixture))
    for assertion in case.get("assertions", []):
        path = assertion["path"]
        obj = _navigate(wf, path)
        if "value" in assertion:
            _assert_value(obj, assertion["value"])
        elif "value_contains" in assertion:
            _assert_value_contains(obj, assertion["value_contains"])
        elif "value_set" in assertion:
            _assert_value_set(obj, assertion["value_set"])
        else:
            raise ValueError(f"Assertion has no recognized mode: {assertion}")
