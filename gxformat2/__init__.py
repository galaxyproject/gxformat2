"""The public interface or entry point for the Format 2 workflow code."""

# Backward compat
from .converter import ImportOptions, python_to_workflow
from .export import from_galaxy_native
from .normalized import to_format2, to_native
from .options import (
    ConversionOptions,
    StateEncodeToFormat2Fn,
    StateEncodeToNativeFn,
)

__version__ = "0.28.0.dev0"

PROJECT_NAME = "gxformat2"
PROJECT_OWNER = "galaxyproject"

__all__ = (
    "ConversionOptions",
    "ImportOptions",
    "StateEncodeToFormat2Fn",
    "StateEncodeToNativeFn",
    "from_galaxy_native",
    "python_to_workflow",
    "to_format2",
    "to_native",
)
