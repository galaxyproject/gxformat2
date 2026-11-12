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


class StepLabelNotUnique(Linter):
    """Step labels (including inputs) must be unique within a workflow; Galaxy refuses duplicates at import."""

    severity = "error"
    applies_to = ("format2", "native")
    profile = "structural"


class FrameReferenceNotFound(Linter):
    """Frame ``contains_steps`` / ``contains_comments`` entries must name a step, input or comment of the workflow."""

    severity = "error"
    applies_to = ("format2",)
    profile = "structural"


class FrameIsEmpty(Linter):
    """Frames should contain at least one step or comment; Galaxy draws an empty one as a bare box."""

    severity = "warning"
    applies_to = ("format2",)
    profile = "best-practices"
