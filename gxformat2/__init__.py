"""The public interface or entry point for the Format 2 workflow code."""

__version__ = "0.25.0.dev0"

PROJECT_NAME = "gxformat2"
PROJECT_OWNER = "galaxyproject"

# Backward compat
from .converter import ImportOptions, python_to_workflow  # NOQA
from .export import from_galaxy_native  # NOQA
from .normalized import to_format2, to_native  # NOQA
from .options import (  # NOQA
    ConversionOptions,
    StateEncodeToFormat2Fn,
    StateEncodeToNativeFn,
)

__all__ = (
    "ConversionOptions",
    "from_galaxy_native",
    "ImportOptions",
    "StateEncodeToFormat2Fn",
    "StateEncodeToNativeFn",
    "python_to_workflow",
    "to_format2",
    "to_native",
)
