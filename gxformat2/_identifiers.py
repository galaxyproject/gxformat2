"""Offline parsing and check-digit validation of creator identifiers (ORCID and ROR iDs)."""

from __future__ import annotations

import re
from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal
from urllib.parse import urlparse

IdentifierScheme = Literal["ORCID", "ROR"]

_ORCID_PATTERN = re.compile(r"\d{4}-\d{4}-\d{4}-\d{3}[\dX]")
_CROCKFORD_BASE32 = "0123456789abcdefghjkmnpqrstvwxyz"
_ROR_PATTERN = re.compile(rf"0[{_CROCKFORD_BASE32}]{{6}}\d{{2}}")


def orcid_checksum_valid(orcid: str) -> bool:
    """Check the ISO 7064 MOD 11-2 check digit of a well-formed ORCID iD."""
    digits = orcid.replace("-", "")
    total = 0
    for digit in digits[:-1]:
        total = (total + int(digit)) * 2
    result = (12 - total % 11) % 11
    return digits[-1] == ("X" if result == 10 else str(result))


def ror_checksum_valid(ror: str) -> bool:
    """Check the ISO 7064 MOD 97-10 check digits of a well-formed ROR iD."""
    number = 0
    for character in ror[:7]:
        number = number * 32 + _CROCKFORD_BASE32.index(character)
    return int(ror[7:]) == 98 - (number * 100) % 97


@dataclass(frozen=True)
class _Scheme:
    name: IdentifierScheme
    host: str
    pattern: re.Pattern[str]
    normalize: Callable[[str], str]
    checksum_valid: Callable[[str], bool]


_SCHEMES = (
    _Scheme("ORCID", "orcid.org", _ORCID_PATTERN, str.upper, orcid_checksum_valid),
    _Scheme("ROR", "ror.org", _ROR_PATTERN, str.lower, ror_checksum_valid),
)


@dataclass(frozen=True)
class ParsedIdentifier:
    """An identifier recognised as an ORCID or ROR iD, bare or as a URI."""

    scheme: IdentifierScheme
    id: str
    """The iD itself, normalised to its canonical case."""
    is_uri: bool
    """Whether the identifier has a URI scheme (``0000-...`` and ``orcid.org/0000-...`` have none)."""
    well_formed: bool
    checksum_valid: bool

    @property
    def canonical(self) -> str:
        """The canonical ``https://`` URI form of the iD."""
        host = next(scheme.host for scheme in _SCHEMES if scheme.name == self.scheme)
        return f"https://{host}/{self.id}"


def parse_identifier(identifier: str) -> ParsedIdentifier | None:
    """Recognise an ORCID or ROR iD; return ``None`` for any other identifier."""
    identifier = identifier.strip()
    for scheme in _SCHEMES:
        bare = scheme.normalize(identifier)
        if scheme.pattern.fullmatch(bare):
            return ParsedIdentifier(scheme.name, bare, False, True, scheme.checksum_valid(bare))
    parsed_url = urlparse(identifier if "://" in identifier else f"https://{identifier}")
    host = parsed_url.netloc.lower().removeprefix("www.")
    for scheme in _SCHEMES:
        if host == scheme.host:
            id_ = scheme.normalize(parsed_url.path.strip("/"))
            well_formed = bool(scheme.pattern.fullmatch(id_))
            checksum_valid = well_formed and scheme.checksum_valid(id_)
            return ParsedIdentifier(scheme.name, id_, "://" in identifier, well_formed, checksum_valid)
    return None
