"""Lint rule classes.

Each ``Linter`` subclass carries metadata only (severity, applies_to,
profile). Emission happens in ``gxformat2/lint.py`` via
``LintContext.warn`` / ``LintContext.error`` with ``linter=<Subclass>``.
"""

from gxformat2.linting import Linter


class NativeStepKeyNotInteger(Linter):
    """Native workflow step keys must be string representations of integers."""

    severity = "error"
    applies_to = ("native",)
    profile = "structural"
