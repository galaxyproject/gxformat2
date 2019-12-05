"""Utilities for handling unlabelled objects when translating workflow formats."""


class Labels(object):
    """Track labels assigned and generate anonymous ones."""

    def __init__(self):
        self.seen_labels = []
        self.anonymous_labels = 0

    def ensure_new_output_label(self, label):
        if label is None:
            self.anonymous_labels += 1
            label = "_anonymous_output_%d" % self.anonymous_labels
        assert label not in self.seen_labels
        return label

    @staticmethod
    def is_anonymous_output_label(label):
        return label.startswith("_anonymous_output_")
