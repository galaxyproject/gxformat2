"""Declarative normalization tests driven by YAML expectation files.

Expectation files live in gxformat2/examples/expectations/.
Uses gxformat2.testing for the harness — this module just provides
the operations dict and fixture loader.
"""

import os
from typing import Any, Callable, Dict

from gxformat2.examples import EXAMPLES_DIR, load
from gxformat2.lint import lint_best_practices_format2 as _lint_bp_format2_impl
from gxformat2.lint import lint_best_practices_ga as _lint_bp_ga_impl
from gxformat2.lint import lint_format2 as _lint_format2_impl
from gxformat2.lint import lint_ga as _lint_ga_impl
from gxformat2.linting import LintContext
from gxformat2.mermaid import workflow_to_mermaid as _mermaid_impl
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
from gxformat2.normalized._conversion import ExpandedFormat2
from gxformat2.normalized._native import NormalizedNativeWorkflow
from gxformat2.testing import DeclarativeTestSuite
from gxformat2.validators import (
    validate_format2,
    validate_format2_strict,
    validate_native,
    validate_native_strict,
)


def _lint_format2(wf_dict):
    ctx = LintContext()
    try:
        nf2 = ensure_format2(wf_dict, expand=True)
    except Exception:
        nf2 = None
    if nf2 is not None:
        _lint_format2_impl(ctx, nf2, raw_dict=wf_dict)
    else:
        # Model build failed — still run raw_dict structural checks
        _lint_format2_impl(ctx, ExpandedFormat2(), raw_dict=wf_dict)
    return {
        "errors": ctx.error_messages,
        "warnings": ctx.warn_messages,
        "error_count": len(ctx.error_messages),
        "warn_count": len(ctx.warn_messages),
    }


def _empty_nnw():
    return NormalizedNativeWorkflow()


def _lint_native(wf_dict):
    ctx = LintContext()
    try:
        nnw = ensure_native(wf_dict)
    except Exception:
        nnw = None
    if nnw is not None:
        _lint_ga_impl(ctx, nnw, raw_dict=wf_dict)
    else:
        # Model build failed — still run raw_dict structural checks
        _lint_ga_impl(ctx, _empty_nnw(), raw_dict=wf_dict)
    return {
        "errors": ctx.error_messages,
        "warnings": ctx.warn_messages,
        "error_count": len(ctx.error_messages),
        "warn_count": len(ctx.warn_messages),
    }


def _lint_best_practices_format2(wf_dict):
    ctx = LintContext()
    _lint_bp_format2_impl(ctx, wf_dict)
    return {
        "errors": ctx.error_messages,
        "warnings": ctx.warn_messages,
        "error_count": len(ctx.error_messages),
        "warn_count": len(ctx.warn_messages),
    }


def _lint_best_practices_native(wf_dict):
    ctx = LintContext()
    _lint_bp_ga_impl(ctx, wf_dict)
    return {
        "errors": ctx.error_messages,
        "warnings": ctx.warn_messages,
        "error_count": len(ctx.error_messages),
        "warn_count": len(ctx.warn_messages),
    }


def _workflow_to_mermaid(wf_dict):
    return _mermaid_impl(wf_dict)


def _workflow_to_mermaid_lines(wf_dict):
    return _mermaid_impl(wf_dict).split("\n")


def _workflow_to_mermaid_with_comments_lines(wf_dict):
    return _mermaid_impl(wf_dict, comments=True).split("\n")


EXPECTATIONS_DIR = os.path.join(EXAMPLES_DIR, "expectations")
OPERATIONS: Dict[str, Callable[..., Any]] = {
    "normalized_format2": normalized_format2,
    "normalized_native": normalized_native,
    "expanded_format2": expanded_format2,
    "expanded_native": expanded_native,
    "to_format2": to_format2,
    "to_native": to_native,
    "ensure_format2": ensure_format2,
    "ensure_native": ensure_native,
    "validate_format2": validate_format2,
    "validate_format2_strict": validate_format2_strict,
    "validate_native": validate_native,
    "validate_native_strict": validate_native_strict,
    "lint_format2": _lint_format2,
    "lint_native": _lint_native,
    "lint_best_practices_format2": _lint_best_practices_format2,
    "lint_best_practices_native": _lint_best_practices_native,
    "workflow_to_mermaid": _workflow_to_mermaid,
    "workflow_to_mermaid_lines": _workflow_to_mermaid_lines,
    "workflow_to_mermaid_with_comments_lines": _workflow_to_mermaid_with_comments_lines,
}

suite = DeclarativeTestSuite(
    operations=OPERATIONS,
    load_fixture=load,
    expectations_dir=EXPECTATIONS_DIR,
)


@suite.pytest_params()
def test_declarative(test_id, case):
    suite.run(test_id, case)
