"""Integrity tests for the lint profile catalog."""

from gxformat2.lint_profiles import (
    iwc_rule_ids,
    lint_profiles_by_id,
    LINT_PROFILES_PATH,
    load_lint_profiles,
    rules_for_profile,
)


def test_catalog_loads():
    profiles = load_lint_profiles()
    assert profiles, "lint_profiles.yml is empty"


def test_three_canonical_profiles_present():
    ids = {p.id for p in load_lint_profiles()}
    assert {"structural", "best-practices", "release"} <= ids


def test_rules_for_profile_returns_list():
    rules = rules_for_profile("structural")
    assert "NativeStepKeyNotInteger" in rules


def test_iwc_union():
    union = iwc_rule_ids()
    structural = set(rules_for_profile("structural"))
    best_practices = set(rules_for_profile("best-practices"))
    release = set(rules_for_profile("release"))
    assert union == structural | best_practices | release


def test_no_duplicate_ids_within_profile():
    for profile in load_lint_profiles():
        assert len(profile.rules) == len(set(profile.rules)), f"profile {profile.id} has duplicate rule IDs"


def test_catalog_path_exists():
    import os

    assert os.path.exists(LINT_PROFILES_PATH)


def test_profiles_keyed_by_id():
    by_id = lint_profiles_by_id()
    for pid, profile in by_id.items():
        assert pid == profile.id
