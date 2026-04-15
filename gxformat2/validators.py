"""Shared pydantic-validator dispatch for workflow dict inputs.

Callers pass a parsed workflow dict and get a pydantic model back (or a
ValidationError). Used by the declarative-operation runner and the
schema-rule catalog runner.
"""

from typing import Callable

from gxformat2.schema.gxformat2 import GalaxyWorkflow as Format2Lax
from gxformat2.schema.gxformat2_strict import GalaxyWorkflow as Format2Strict
from gxformat2.schema.native import NativeGalaxyWorkflow as NativeLax
from gxformat2.schema.native_strict import NativeGalaxyWorkflow as NativeStrict


def validate_format2(wf_dict):
    """Validate a Format2 workflow dict with the lax (open) schema."""
    return Format2Lax.model_validate(wf_dict)


def validate_format2_strict(wf_dict):
    """Validate a Format2 workflow dict with the strict (closed) schema."""
    return Format2Strict.model_validate(wf_dict)


def validate_native(wf_dict):
    """Validate a native Galaxy workflow dict with the lax (open) schema."""
    return NativeLax.model_validate(wf_dict)


def validate_native_strict(wf_dict):
    """Validate a native Galaxy workflow dict with the strict (closed) schema."""
    return NativeStrict.model_validate(wf_dict)


def validator_for_fixture(fixture_name: str, strict: bool) -> Callable[[dict], object]:
    """Pick the validator matching a fixture filename's format.

    `.ga` → native; anything else → format2. `strict` picks the closed-schema
    flavor that rejects unknown fields.
    """
    if fixture_name.endswith(".ga"):
        return validate_native_strict if strict else validate_native
    return validate_format2_strict if strict else validate_format2
