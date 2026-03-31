"""Declarative normalization tests driven by YAML expectation files.

Expectation files live in gxformat2/examples/expectations/.
Uses gxformat2.testing for the harness — this module just provides
the operations dict and fixture loader.
"""

import os

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
from gxformat2.testing import DeclarativeTestSuite


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

suite = DeclarativeTestSuite(
    operations=OPERATIONS,
    load_fixture=load,
    expectations_dir=EXPECTATIONS_DIR,
)


@suite.pytest_params()
def test_declarative(test_id, case):
    suite.run(test_id, case)
