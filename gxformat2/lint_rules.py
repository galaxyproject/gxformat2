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


class CreatorMissingIdentifier(Linter):
    """Creators should have a persistent identifier: an ORCID iD for a person, a ROR iD for an organisation in ROR."""

    severity = "info"
    applies_to = ("format2", "native")
    profile = "best-practices"


class CreatorIdentifierNotURI(Linter):
    """Creator identifiers should be fully qualified URIs, e.g. ``https://orcid.org/<iD>`` rather than a bare ORCID iD."""

    severity = "warning"
    applies_to = ("format2", "native")
    profile = "best-practices"


class CreatorIdentifierNotCanonical(Linter):
    """ORCID and ROR URIs should use the canonical ``https://orcid.org/`` or ``https://ror.org/`` form."""

    severity = "warning"
    applies_to = ("format2", "native")
    profile = "best-practices"


class CreatorIdentifierInvalid(Linter):
    """ORCID and ROR iDs must be well formed and their check digits must match."""

    severity = "warning"
    applies_to = ("format2", "native")
    profile = "best-practices"


class CreatorIdentifierTypeMismatch(Linter):
    """An ``Organization`` with an ORCID iD, or a ``Person`` with a ROR iD, is probably misclassified."""

    severity = "warning"
    applies_to = ("format2", "native")
    profile = "best-practices"
