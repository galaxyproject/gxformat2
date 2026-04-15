"""Lint profile catalog loader.

Profiles group lint-rule IDs into named sets (``structural``,
``best-practices``, ``release``). Unknown IDs are tolerated — audit tooling
compares against the registered ``Linter`` subclasses to flag unimplemented
entries as INFO.
"""

import os
from typing import Dict, List, Set

import yaml
from pydantic import BaseModel

LINT_PROFILES_PATH = os.path.join(os.path.dirname(__file__), "lint_profiles.yml")


class LintProfile(BaseModel):
    id: str
    description: str = ""
    rules: List[str]


def load_lint_profiles() -> List[LintProfile]:
    """Parse lint_profiles.yml into validated ``LintProfile`` models."""
    with open(LINT_PROFILES_PATH) as f:
        raw = yaml.safe_load(f) or {}
    profiles: List[LintProfile] = []
    for profile_id, body in raw.items():
        profiles.append(LintProfile(id=profile_id, **body))
    return profiles


def lint_profiles_by_id() -> Dict[str, LintProfile]:
    """Return profiles keyed by id."""
    return {p.id: p for p in load_lint_profiles()}


def rules_for_profile(profile_id: str) -> List[str]:
    """Return the ordered rule ID list for a named profile."""
    return lint_profiles_by_id()[profile_id].rules


def iwc_rule_ids() -> Set[str]:
    """Union of structural, best-practices, and release rule IDs."""
    profiles = lint_profiles_by_id()
    rule_ids: Set[str] = set()
    for name in ("structural", "best-practices", "release"):
        if name in profiles:
            rule_ids.update(profiles[name].rules)
    return rule_ids
