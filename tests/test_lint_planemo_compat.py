"""Back-compat shim tests for the legacy Planemo signature.

Planemo calls ``lint_format2(ctx, workflow_dict, path=path)`` and
``lint_ga(ctx, workflow_dict, path=path)`` with a raw dict. The migration to
normalized models would have broken Planemo; this exercises the shim that
accepts either a dict or a normalized model.
"""

from gxformat2.examples import load
from gxformat2.lint import lint_format2, lint_ga
from gxformat2.linting import LintContext


def test_lint_ga_accepts_raw_dict_and_path():
    ctx = LintContext()
    wf_dict = load("real-unicycler-assembly.ga")
    lint_ga(ctx, wf_dict, path="/fake/path.ga")
    assert ctx.error_messages == []


def test_lint_format2_accepts_raw_dict_and_path():
    ctx = LintContext()
    wf_dict = load("synthetic-basic.gxwf.yml")
    lint_format2(ctx, wf_dict, path="/fake/path.gxwf.yml")
    assert ctx.error_messages == []


def test_lint_ga_still_accepts_normalized_model():
    from gxformat2.normalized import ensure_native

    ctx = LintContext()
    wf_dict = load("real-unicycler-assembly.ga")
    nnw = ensure_native(wf_dict)
    lint_ga(ctx, nnw, raw_dict=wf_dict)
    assert ctx.error_messages == []


def test_lint_format2_still_accepts_normalized_model():
    from gxformat2.normalized import ensure_format2

    ctx = LintContext()
    wf_dict = load("synthetic-basic.gxwf.yml")
    nf2 = ensure_format2(wf_dict, expand=True)
    lint_format2(ctx, nf2, raw_dict=wf_dict)
    assert ctx.error_messages == []
