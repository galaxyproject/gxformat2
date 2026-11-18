"""Tests for offline ORCID and ROR iD parsing and check-digit validation."""

import pytest

from gxformat2._identifiers import (
    orcid_checksum_valid,
    parse_identifier,
    ror_checksum_valid,
)


@pytest.mark.parametrize(
    "orcid, valid",
    [
        ("0000-0002-1825-0097", True),
        ("0000-0002-1694-233X", True),
        ("0000-0002-1825-0098", False),
    ],
)
def test_orcid_checksum(orcid, valid):
    assert orcid_checksum_valid(orcid) is valid


@pytest.mark.parametrize(
    "ror, valid",
    [
        ("05gq02987", True),
        ("05gq02988", False),
    ],
)
def test_ror_checksum(ror, valid):
    assert ror_checksum_valid(ror) is valid


@pytest.mark.parametrize(
    "identifier, scheme, id_, is_uri, canonical",
    [
        ("0000-0002-1825-0097", "ORCID", "0000-0002-1825-0097", False, "https://orcid.org/0000-0002-1825-0097"),
        ("0000-0002-1694-233x", "ORCID", "0000-0002-1694-233X", False, "https://orcid.org/0000-0002-1694-233X"),
        (
            "orcid.org/0000-0002-1825-0097",
            "ORCID",
            "0000-0002-1825-0097",
            False,
            "https://orcid.org/0000-0002-1825-0097",
        ),
        (
            "http://www.orcid.org/0000-0002-1825-0097/",
            "ORCID",
            "0000-0002-1825-0097",
            True,
            "https://orcid.org/0000-0002-1825-0097",
        ),
        ("https://ror.org/05gq02987", "ROR", "05gq02987", True, "https://ror.org/05gq02987"),
        ("05GQ02987", "ROR", "05gq02987", False, "https://ror.org/05gq02987"),
    ],
)
def test_parse_recognised(identifier, scheme, id_, is_uri, canonical):
    parsed = parse_identifier(identifier)
    assert parsed is not None
    assert (parsed.scheme, parsed.id, parsed.is_uri, parsed.canonical) == (scheme, id_, is_uri, canonical)
    assert parsed.well_formed and parsed.checksum_valid


@pytest.mark.parametrize(
    "identifier",
    [
        "https://orcid.org/0000-0002-1825",
        # Non-ASCII digits
        "https://orcid.org/\u0660\u0660\u0660\u0660-\u0660\u0660\u0660\u0662-\u0661\u0668\u0662\u0665-\u0660\u0660\u0669\u0667",
        "https://ror.org/not-a-ror",
    ],
)
def test_parse_malformed(identifier):
    parsed = parse_identifier(identifier)
    assert parsed is not None
    assert not parsed.well_formed
    assert not parsed.checksum_valid


@pytest.mark.parametrize(
    "identifier",
    [
        "https://example.org/people/42",
        "josiah",
        "mailto:josiah@example.org",
        # Bare ORCID iD in non-ASCII digits
        "\u0660\u0660\u0660\u0660-\u0660\u0660\u0660\u0662-\u0661\u0668\u0662\u0665-\u0660\u0660\u0669\u0667",
        # A bare ROR iD is only recognised if its check digits match.
        "012345678",
        # Malformed URL, which urlparse() rejects
        "https://[orcid.org/x",
    ],
)
def test_parse_other(identifier):
    assert parse_identifier(identifier) is None


def test_parse_ror_uri_with_wrong_check_digits():
    parsed = parse_identifier("https://ror.org/012345678")
    assert parsed is not None
    assert parsed.scheme == "ROR"
    assert parsed.well_formed
    assert not parsed.checksum_valid


def test_parse_bare_orcid_with_wrong_check_digit():
    # Unlike a bare ROR iD, a bare ORCID iD is recognised even if its check digit does not match.
    parsed = parse_identifier("0000-0002-1825-0098")
    assert parsed is not None
    assert parsed.scheme == "ORCID"
    assert not parsed.is_uri
    assert parsed.well_formed
    assert not parsed.checksum_valid
