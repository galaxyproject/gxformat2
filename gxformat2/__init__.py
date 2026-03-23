"""The public interface or entry point for the Format 2 workflow code."""

__version__ = "0.25.0.dev0"

PROJECT_NAME = "gxformat2"
PROJECT_OWNER = "galaxyproject"

from .options import ConversionOptions, ConvertToolStateFn, NativeStateEncoderFn  # NOQA
from .to_format2 import to_format2  # NOQA
from .to_native import to_native  # NOQA

# Backward compat
from .converter import ImportOptions, python_to_workflow  # NOQA
from .export import from_galaxy_native  # NOQA

__all__ = (
    "ConversionOptions",
    "ConvertToolStateFn",
    "from_galaxy_native",
    "ImportOptions",
    "NativeStateEncoderFn",
    "python_to_workflow",
    "to_format2",
    "to_native",
)
