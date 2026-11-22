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


class LoopNotOnSubworkflowStep(Linter):
    """Only a step that runs a subworkflow may have a ``loop``; Galaxy refuses a loop on any other step."""

    severity = "error"
    applies_to = ("format2", "native")
    profile = "structural"


class LoopMissingWhen(Linter):
    """A step with a ``loop`` needs a ``when`` expression, which ends the loop, as in CWL v1.3."""

    severity = "error"
    applies_to = ("format2", "native")
    profile = "structural"


class LoopHasNoInputs(Linter):
    """A ``loop`` must name at least one step input fed into the next iteration."""

    severity = "error"
    applies_to = ("format2", "native")
    profile = "structural"


class LoopInputHasNoValue(Linter):
    """Each ``loop`` input needs at least one of ``outputSource``, ``default`` and ``valueFrom``."""

    severity = "error"
    applies_to = ("format2", "native")
    profile = "structural"


class LoopOutputSourceListInvalid(Linter):
    """Several ``outputSource`` outputs need two or more labels and ``pickValue`` ``first_non_null`` or ``the_only_non_null``.

    Also refused, as Galaxy does: ``linkMerge`` ``merge_flattened``, and ``linkMerge`` or
    ``pickValue`` on a single ``outputSource``.
    """

    severity = "error"
    applies_to = ("format2", "native")
    profile = "structural"


class LoopReferenceNotFound(Linter):
    """``loop`` inputs must name inputs, and their ``outputSource`` outputs, of the subworkflow the step runs."""

    severity = "error"
    applies_to = ("format2", "native")
    profile = "structural"


class OutputMethodWithoutLoop(Linter):
    """``outputMethod`` is only valid on a step with a ``loop``."""

    severity = "error"
    applies_to = ("format2",)
    profile = "structural"
