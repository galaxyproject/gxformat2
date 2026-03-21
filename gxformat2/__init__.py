"""The public interface or entry point for the Format 2 workflow code."""

__version__ = "0.24.0"

PROJECT_NAME = "gxformat2"
PROJECT_OWNER = "galaxyproject"

from .converter import ImportOptions, python_to_workflow  # NOQA
from .export import from_galaxy_native  # NOQA
from .interface import ImporterGalaxyInterface  # NOQA
from .main import convert_and_import_workflow  # NOQA

__all__ = (
    "convert_and_import_workflow",
    "from_galaxy_native",
    "ImporterGalaxyInterface",
    "ImportOptions",
    "python_to_workflow",
)
