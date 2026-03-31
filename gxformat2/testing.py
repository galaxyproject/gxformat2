"""Reusable declarative test harness for YAML-driven workflow operation tests.

Extracts the test infrastructure from gxformat2's own declarative tests into
an importable module. Callers inject their own operations dict and fixture
loader, making this usable from any project (Galaxy, Planemo, etc.).

Path element types for assertions:
  - str: dict key lookup (falls back to attribute access)
  - int: list index
  - "$length": terminal, returns len(current object)
  - {field: value}: find first list item where item.field == value

Assertion modes:
  - value: exact equality
  - value_contains: substring containment
  - value_set: unordered set comparison
  - value_matches: regex match
  - value_truthy / value_falsy: boolean-ish checks
  - value_type: isinstance check ("dict", "list", "str", "int", "float", "bool")
"""

import os
import re
from typing import (
    Any,
    Callable,
    Dict,
    Iterator,
    List,
    Optional,
    Tuple,
    Union,
)

import yaml
from pydantic import BaseModel, model_validator

PathElement = Union[str, int, Dict[str, Any]]

_UNSET = object()

_TYPE_MAP = {
    "dict": dict,
    "list": list,
    "str": str,
    "int": int,
    "float": float,
    "bool": bool,
}


class Assertion(BaseModel):
    """A single path-based assertion against an operation result."""

    model_config = {"arbitrary_types_allowed": True}

    path: List[PathElement]
    value: Any = _UNSET
    value_contains: Optional[str] = None
    value_set: Optional[List[Any]] = None
    value_matches: Optional[str] = None
    value_truthy: Optional[bool] = None
    value_falsy: Optional[bool] = None
    value_type: Optional[str] = None

    @model_validator(mode="after")
    def _check_exactly_one_mode(self) -> "Assertion":
        modes = [
            self.value is not _UNSET,
            self.value_contains is not None,
            self.value_set is not None,
            self.value_matches is not None,
            self.value_truthy is not None,
            self.value_falsy is not None,
            self.value_type is not None,
        ]
        if sum(modes) != 1:
            raise ValueError(
                "Assertion must specify exactly one of: value, value_contains, value_set, value_matches, value_truthy, value_falsy, value_type"
            )
        return self


class TestCase(BaseModel):
    """A single declarative test case."""

    fixture: str
    operation: str
    expect_error: bool = False
    assertions: List[Assertion] = []


class ExpectationSuite(BaseModel):
    """Top-level model: maps test IDs to test cases."""

    root: Dict[str, TestCase]

    @classmethod
    def from_yaml(cls, path: str) -> "ExpectationSuite":
        with open(path) as f:
            raw = yaml.safe_load(f)
        if not raw:
            return cls(root={})
        return cls(root=raw)


def navigate(obj: Any, path: List[PathElement]) -> Any:
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


def assert_value(obj: Any, expected: Any):
    """Assert exact equality."""
    assert obj == expected, f"expected {expected!r}, got {obj!r}"


def assert_value_contains(obj: Any, expected: str):
    """Assert that expected is a substring of obj."""
    assert expected in obj, f"expected {expected!r} in {obj!r}"


def assert_value_set(obj: Any, expected_items: list):
    """Assert unordered set equality.

    For frozensets of NamedTuples: converts each item via _asdict() and
    compares as sets of frozen key-value pairs.
    For frozensets of primitives: plain set comparison.
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


def assert_value_matches(obj: Any, pattern: str):
    """Assert that obj matches the given regex pattern."""
    assert re.search(pattern, str(obj)), f"expected {str(obj)!r} to match {pattern!r}"


def assert_value_truthy(obj: Any):
    """Assert that obj is truthy."""
    assert obj, f"expected truthy value, got {obj!r}"


def assert_value_falsy(obj: Any):
    """Assert that obj is falsy."""
    assert not obj, f"expected falsy value, got {obj!r}"


def assert_value_type(obj: Any, expected_type: str):
    """Assert that obj is an instance of the named type."""
    typ = _TYPE_MAP.get(expected_type)
    if typ is None:
        raise ValueError(f"Unknown type name {expected_type!r}, expected one of {list(_TYPE_MAP)}")
    assert isinstance(obj, typ), f"expected type {expected_type}, got {type(obj).__name__}"


def load_expectation_cases(expectations_dir: str) -> Iterator[Tuple[str, TestCase]]:
    """Yield (test_id, TestCase) for every expectation YAML in a directory."""
    for fname in sorted(os.listdir(expectations_dir)):
        if not fname.endswith(".yml"):
            continue
        suite = ExpectationSuite.from_yaml(os.path.join(expectations_dir, fname))
        for test_id, case in suite.root.items():
            yield test_id, case


def run_assertion(obj: Any, assertion: Assertion):
    """Run a single assertion against a navigated object."""
    navigated = navigate(obj, assertion.path)
    if assertion.value is not _UNSET:
        assert_value(navigated, assertion.value)
    elif assertion.value_contains is not None:
        assert_value_contains(navigated, assertion.value_contains)
    elif assertion.value_set is not None:
        assert_value_set(navigated, assertion.value_set)
    elif assertion.value_matches is not None:
        assert_value_matches(navigated, assertion.value_matches)
    elif assertion.value_truthy is not None:
        assert_value_truthy(navigated)
    elif assertion.value_falsy is not None:
        assert_value_falsy(navigated)
    elif assertion.value_type is not None:
        assert_value_type(navigated, assertion.value_type)


def run_declarative_case(
    case: TestCase,
    operations: Dict[str, Callable[..., Any]],
    load_fixture: Callable[[str], Any],
):
    """Execute one declarative test case.

    Args:
        case: TestCase with fixture, operation, and optionally assertions / expect_error
        operations: mapping of operation name to callable
        load_fixture: callable that takes a fixture name and returns the loaded workflow dict
    """
    operation = operations[case.operation]

    if case.expect_error:
        try:
            operation(load_fixture(case.fixture))
        except Exception:
            return
        raise AssertionError(f"Expected operation {case.operation!r} to raise an exception")

    result = operation(load_fixture(case.fixture))
    for assertion in case.assertions:
        run_assertion(result, assertion)


class DeclarativeTestSuite:
    """Bundles operations + fixture loader for declarative YAML tests.

    Usage::

        suite = DeclarativeTestSuite(
            operations={"normalize": normalize_fn},
            load_fixture=my_loader,
            expectations_dir="/path/to/expectations",
        )

        @suite.pytest_params()
        def test_declarative(test_id, case):
            suite.run(test_id, case)
    """

    def __init__(
        self,
        operations: Dict[str, Callable[..., Any]],
        load_fixture: Callable[[str], Any],
        expectations_dir: Optional[str] = None,
        cases: Optional[List[Tuple[str, TestCase]]] = None,
    ):
        self.operations = operations
        self.load_fixture = load_fixture
        if cases is not None:
            self._cases = list(cases)
        elif expectations_dir is not None:
            self._cases = list(load_expectation_cases(expectations_dir))
        else:
            raise ValueError("Either expectations_dir or cases must be provided")

    @property
    def cases(self) -> List[Tuple[str, TestCase]]:
        return self._cases

    def pytest_params(self):
        """Return pytest.mark.parametrize decorator with test IDs."""
        try:
            import pytest as _pytest
        except ImportError:
            raise ImportError("pytest is required for pytest_params() but is not installed")
        return _pytest.mark.parametrize(
            "test_id,case",
            self._cases,
            ids=[c[0] for c in self._cases],
        )

    def run(self, test_id: str, case: TestCase):
        """Execute a single declarative test case."""
        run_declarative_case(case, self.operations, self.load_fixture)
