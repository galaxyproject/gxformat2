"""Schema-rule catalog loader.

Schema rules describe checks already enforced by the pydantic decode layer.
Each rule ships with positive and negative fixtures; the catalog contract is
tested end-to-end by running fixtures through validators — not by inspecting
ValidationError shapes.
"""

import os
from enum import Enum
from typing import List

import yaml
from pydantic import BaseModel

SCHEMA_RULES_PATH = os.path.join(os.path.dirname(__file__), "schema_rules.yml")


class Severity(str, Enum):
    """Rule severity level."""

    error = "error"
    warning = "warning"


class AppliesTo(str, Enum):
    """Which workflow format a schema rule applies to."""

    format2 = "format2"
    native = "native"


class Scope(str, Enum):
    """Validator flavors that reject the negative fixture.

    - ``both``: both lax and strict reject (e.g. missing required field).
    - ``strict``: only strict rejects (e.g. unknown extra field).
    - ``lax``: only lax rejects — unusual, reserved for completeness.
    """

    both = "both"
    strict = "strict"
    lax = "lax"


class SchemaRuleTests(BaseModel):
    """Positive/negative fixture references for a schema rule."""

    positive: List[str]
    negative: List[str]


class SchemaRule(BaseModel):
    """Declarative schema-rule entry loaded from schema_rules.yml."""

    id: str
    severity: Severity
    applies_to: List[AppliesTo]
    scope: Scope
    description: str = ""
    tests: SchemaRuleTests


def load_schema_rules() -> List[SchemaRule]:
    """Parse schema_rules.yml into validated SchemaRule models."""
    with open(SCHEMA_RULES_PATH) as f:
        raw = yaml.safe_load(f)
    rules: List[SchemaRule] = []
    for rule_id, body in raw.items():
        rules.append(SchemaRule(id=rule_id, **body))
    return rules
