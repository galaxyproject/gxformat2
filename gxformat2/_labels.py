"""Utilities for handling unlabelled objects when translating workflow formats."""

from __future__ import annotations

UNLABELED_INPUT_PREFIX = "_unlabeled_input_"
UNLABELED_STEP_PREFIX = "_unlabeled_step_"


def unlabeled_node_id(label: Optional[str], step_id, is_input: bool) -> str:
    """Node id for a workflow step: its label, else a synthetic unlabeled sentinel.

    Single source of truth for the native-step → Format2-label mapping, shared by
    native→Format2 conversion and by layout position matching, so the two cannot
    drift.
    """
    if label is not None:
        return label
    prefix = UNLABELED_INPUT_PREFIX if is_input else UNLABELED_STEP_PREFIX
    return f"{prefix}{step_id}"


class Labels:
    """Track labels assigned and generate anonymous ones."""

    def __init__(self):
        """Initialize labels that have been encountered or generated."""
        self.seen_labels = set()
        self.anonymous_labels = 0

    def ensure_new_output_label(self, label: str | None):
        """Ensure supplied label has value or generate an anonymous one."""
        if label is None:
            self.anonymous_labels += 1
            label = f"_anonymous_output_{self.anonymous_labels}"
        assert label not in self.seen_labels
        self.seen_labels.add(label)
        return label

    @staticmethod
    def is_anonymous_output_label(label: str):
        """Predicate determining if supplied label was generated for anonymous output."""
        # label likely can't be null according to the schema definition - but we've got a test
        # in Galaxy that doesn't define a label in order to great a .ga file without output
        # labels (which is completely normal).
        return not label or label.startswith("_anonymous_output_")

    @staticmethod
    def is_unlabeled_input(label) -> bool:
        """Predicate determining if supplied label is a synthetic sentinel for an unlabeled input."""
        return isinstance(label, str) and label.startswith(UNLABELED_INPUT_PREFIX)

    @staticmethod
    def is_unlabeled_step(label) -> bool:
        """Predicate determining if supplied label is a synthetic sentinel for an unlabeled tool step."""
        return isinstance(label, str) and label.startswith(UNLABELED_STEP_PREFIX)

    @staticmethod
    def is_unlabeled(label) -> bool:
        """Predicate for any synthetic unlabeled sentinel (input or step)."""
        return Labels.is_unlabeled_input(label) or Labels.is_unlabeled_step(label)
