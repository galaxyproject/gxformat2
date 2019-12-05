"""Utilities for handling unlabelled objects when translating workflow formats."""


class Labels(object):
    """Track labels assigned and generate anonymous ones."""

    def __init__(self):
        """Initialize labels that have been encountered or generated."""
        self.seen_labels = []
        self.anonymous_labels = 0

    def ensure_new_output_label(self, label):
        """Ensure supplied label has value or generate an anonymous one."""
        if label is None:
            self.anonymous_labels += 1
            label = "_anonymous_output_%d" % self.anonymous_labels
        assert label not in self.seen_labels
        return label

    @staticmethod
    def is_anonymous_output_label(label):
        """Predicate determining if supplied label was generated for anonymous output."""
        return label.startswith("_anonymous_output_")
