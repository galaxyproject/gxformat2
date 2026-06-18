"""Draft workflow schema metadata.

The schema-salad metaschema cannot currently express a named regex-constrained
string subtype that survives the pydantic and Effect Schema code generators.
Keep the sentinel contract here so downstream tooling has one upstream-owned
definition to mirror.
"""

from __future__ import annotations

import re
from typing import Final

TODO_SENTINEL_PATTERN: Final[str] = r"^TODO(_[a-zA-Z0-9_]+)?$"
TODO_SENTINEL_RE: Final[re.Pattern[str]] = re.compile(TODO_SENTINEL_PATTERN)

PLAN_FIELDS: Final[tuple[str, ...]] = (
    "_plan_state",
    "_plan_context",
    "_plan_in",
    "_plan_out",
)


def is_todo_sentinel(value: object) -> bool:
    """Return true if *value* is a draft TODO sentinel string."""
    return isinstance(value, str) and TODO_SENTINEL_RE.fullmatch(value) is not None
