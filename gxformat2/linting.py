"""Generic utilities for linting.

Largely derived from galaxy.tool_util.lint. ``LintMessage`` is a ``str``
subclass so existing code that treats ``warn_messages`` / ``error_messages``
as lists of strings keeps working; new metadata (``level``, ``linter``,
``json_pointer``) is accessible as attributes.
"""

from __future__ import annotations

import enum
from typing import ClassVar, List, Optional, Tuple, Union


class LintLevel(str, enum.Enum):
    """Lint severity levels."""

    ERROR = "error"
    WARN = "warn"
    ALL = "all"


# Back-compat string constants.
LEVEL_ALL = LintLevel.ALL.value
LEVEL_WARN = LintLevel.WARN.value
LEVEL_ERROR = LintLevel.ERROR.value
DEFAULT_TRAINING_LINT = None


class LintMessage(str):
    """A single lint emission: prose + structured metadata.

    Subclassing ``str`` keeps ``"substring" in message`` and
    ``str(message)`` working for existing callers/tests.
    """

    level: str
    linter: Optional[str]
    json_pointer: str

    def __new__(
        cls,
        message: str,
        *,
        level: str = LEVEL_WARN,
        linter: Optional[str] = None,
        json_pointer: str = "",
    ) -> "LintMessage":
        """Construct a ``LintMessage`` with prose and structured metadata."""
        self = super().__new__(cls, message)
        self.level = level
        self.linter = linter
        self.json_pointer = json_pointer
        return self


class Linter:
    """Metadata-only base class for lint rules.

    Subclasses carry class-level metadata; emission is performed by
    ``LintContext.warn`` / ``LintContext.error`` with ``linter=SubclassName``.
    """

    severity: ClassVar[str] = "warning"
    applies_to: ClassVar[Tuple[str, ...]] = ()
    profile: ClassVar[str] = "structural"


def _escape_pointer_segment(segment) -> str:
    """Escape an RFC 6901 JSON Pointer segment."""
    return str(segment).replace("~", "~0").replace("/", "~1")


class LintContext:
    """Track running status (state) of linting."""

    def __init__(self, level=LEVEL_WARN, training_topic=DEFAULT_TRAINING_LINT, _pointer: str = ""):
        """Create LintContext with specified 'level' (currently unused)."""
        self.level = level
        self.training_topic = training_topic
        self.found_errors = False
        self.found_warns = False
        self._pointer = _pointer

        self.warn_messages: List[LintMessage] = []
        self.error_messages: List[LintMessage] = []

    def child(self, pointer_segment) -> "LintContext":
        """Create child context whose default json_pointer is prefixed."""
        new_pointer = f"{self._pointer}/{_escape_pointer_segment(pointer_segment)}"
        child_ctx = LintContext(
            level=self.level,
            training_topic=self.training_topic,
            _pointer=new_pointer,
        )
        child_ctx.warn_messages = self.warn_messages
        child_ctx.error_messages = self.error_messages
        return child_ctx

    def error(
        self,
        message: str,
        *args,
        linter: Union[type, str, None] = None,
        json_pointer: Optional[str] = None,
        **kwds,
    ) -> None:
        """Track a linting error - a serious problem with the artifact preventing execution."""
        self._emit(self.error_messages, LEVEL_ERROR, message, args, kwds, linter, json_pointer)

    def warn(
        self,
        message: str,
        *args,
        linter: Union[type, str, None] = None,
        json_pointer: Optional[str] = None,
        **kwds,
    ) -> None:
        """Track a linting warning - a deviation from best practices."""
        self._emit(self.warn_messages, LEVEL_WARN, message, args, kwds, linter, json_pointer)

    def _emit(self, message_list, level, message, args, kwds, linter, json_pointer) -> None:
        if args and not kwds:
            try:
                message = message % args
            except (TypeError, ValueError):
                message = message.format(*args)
        elif args or kwds:
            message = message.format(*args, **kwds)
        pointer = json_pointer if json_pointer is not None else self._pointer
        linter_name = linter.__name__ if isinstance(linter, type) else linter
        message_list.append(LintMessage(message, level=level, linter=linter_name, json_pointer=pointer))

    def print_messages(self) -> None:
        """Print error messages and update state at the end of linting."""
        for message in self.error_messages:
            self.found_errors = True
            print(f".. ERROR: {message}")

        if self.level != LEVEL_ERROR:
            for message in self.warn_messages:
                self.found_warns = True
                print(f".. WARNING: {message}")
