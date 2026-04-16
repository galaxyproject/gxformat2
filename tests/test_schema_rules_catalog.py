"""Parametrized runner for the schema-rule catalog.

Positive fixtures must pass both lax and strict validation. Negative fixtures
must fail per the rule's declared scope and continue to pass in the opposite
flavor (documenting that it IS scope-specific). Validators are selected from
the fixture filename extension.
"""

import os
from typing import List, Tuple

import pytest
from pydantic import ValidationError

from gxformat2.examples import EXAMPLES_DIR, load, load_catalog
from gxformat2.schema_rules import AppliesTo, load_schema_rules, SchemaRule, Scope
from gxformat2.validators import validator_for_fixture

RUNNER = "tests/test_schema_rules_catalog.py"
RULES: List[SchemaRule] = load_schema_rules()


def _fixture_applies_to(fixture: str) -> AppliesTo:
    return AppliesTo.native if fixture.endswith(".ga") else AppliesTo.format2


def _positive_cases() -> List[Tuple[str, str]]:
    return [(rule.id, fx) for rule in RULES for fx in rule.tests.positive]


def _negative_cases() -> List[Tuple[str, str, Scope]]:
    return [(rule.id, fx, rule.scope) for rule in RULES for fx in rule.tests.negative]


def _referenced_fixtures() -> set:
    return {fx for rule in RULES for fx in rule.tests.positive + rule.tests.negative}


@pytest.mark.parametrize("rule_id,fixture", _positive_cases())
def test_positive_fixture_passes_lax_and_strict(rule_id, fixture):
    wf = load(fixture)
    validator_for_fixture(fixture, strict=False)(wf)
    validator_for_fixture(fixture, strict=True)(wf)


@pytest.mark.parametrize("rule_id,fixture,scope", _negative_cases())
def test_negative_fixture_matches_scope(rule_id, fixture, scope):
    wf = load(fixture)
    if scope in (Scope.both, Scope.strict):
        with pytest.raises(ValidationError):
            validator_for_fixture(fixture, strict=True)(wf)
    if scope == Scope.strict:
        validator_for_fixture(fixture, strict=False)(wf)
    if scope in (Scope.both, Scope.lax):
        with pytest.raises(ValidationError):
            validator_for_fixture(fixture, strict=False)(wf)
    if scope == Scope.lax:
        validator_for_fixture(fixture, strict=True)(wf)


def test_schema_rules_have_fixtures():
    """Every rule ships with at least one positive and one negative fixture."""
    for rule in RULES:
        assert rule.tests.positive, f"{rule.id}: empty positive fixture list"
        assert rule.tests.negative, f"{rule.id}: empty negative fixture list"


def test_fixture_format_matches_applies_to():
    """A rule's fixtures must have extensions consistent with its `applies_to`."""
    for rule in RULES:
        for fx in rule.tests.positive + rule.tests.negative:
            fmt = _fixture_applies_to(fx)
            assert (
                fmt in rule.applies_to
            ), f"{rule.id}: fixture {fx} is {fmt.value} but rule applies_to={[a.value for a in rule.applies_to]}"


def test_schema_rule_fixtures_exist_on_disk():
    """Every fixture in schema_rules.yml resolves to a file."""
    missing = []
    for fx in _referenced_fixtures():
        path_f2 = os.path.join(EXAMPLES_DIR, "format2", fx)
        path_na = os.path.join(EXAMPLES_DIR, "native", fx)
        if not (os.path.exists(path_f2) or os.path.exists(path_na)):
            missing.append(fx)
    assert not missing, f"schema_rules.yml fixtures not on disk: {missing}"


def test_schema_rule_fixtures_in_catalog():
    """Every fixture referenced by schema_rules.yml appears in examples catalog.yml."""
    cataloged = {entry.name for entry in load_catalog()}
    missing = _referenced_fixtures() - cataloged
    assert not missing, f"schema_rules.yml references fixtures not in catalog.yml: {missing}"


def test_schema_rule_fixtures_reference_runner():
    """Catalog entries for schema-rule fixtures list this runner in their tests."""
    referenced = _referenced_fixtures()
    offenders = [entry.name for entry in load_catalog() if entry.name in referenced and RUNNER not in entry.tests]
    assert not offenders, f"catalog entries missing {RUNNER}: {offenders}"


def test_no_orphan_runner_tags_in_catalog():
    """Catalog entries listing this runner must be referenced by schema_rules.yml."""
    referenced = _referenced_fixtures()
    orphaned = [entry.name for entry in load_catalog() if RUNNER in entry.tests and entry.name not in referenced]
    assert not orphaned, f"catalog entries tag {RUNNER} but no schema rule references them: {orphaned}"
