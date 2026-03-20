"""Unit tests for resolve_source_reference."""

from gxformat2.model import resolve_source_reference


def test_simple_label_no_output():
    assert resolve_source_reference("step1", {"step1"}) == ("step1", "output")


def test_simple_label_with_output():
    assert resolve_source_reference("step1/out1", {"step1"}) == ("step1", "out1")


def test_slash_in_label_no_output():
    labels = {"Host/Contaminant Genome", "cat"}
    assert resolve_source_reference("Host/Contaminant Genome", labels) == ("Host/Contaminant Genome", "output")


def test_slash_in_label_with_output():
    labels = {"Host/Contaminant Filter", "cat"}
    assert resolve_source_reference("Host/Contaminant Filter/out_file1", labels) == (
        "Host/Contaminant Filter",
        "out_file1",
    )


def test_multiple_slashes_in_label():
    labels = {"A/B/C", "A/B", "A"}
    assert resolve_source_reference("A/B/C", labels) == ("A/B/C", "output")
    assert resolve_source_reference("A/B/C/out1", labels) == ("A/B/C", "out1")
    assert resolve_source_reference("A/B/out1", labels) == ("A/B", "out1")


def test_fallback_unknown_label():
    assert resolve_source_reference("unknown/out1", set()) == ("unknown", "out1")


def test_fallback_no_slash():
    assert resolve_source_reference("step1", set()) == ("step1", "output")


def test_numeric_id():
    assert resolve_source_reference("0/output", set()) == ("0", "output")
    assert resolve_source_reference("0", set()) == ("0", "output")
