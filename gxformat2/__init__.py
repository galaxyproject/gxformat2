"""The public interface or entry point for the Format 2 workflow code."""

__version__ = '0.1.1'

PROJECT_NAME = "gxformat2"
PROJECT_OWNER = PROJECT_USERAME = "jmchilton"
PROJECT_AUTHOR = 'Galaxy Project and Community'
PROJECT_EMAIL = 'jmchilton@gmail.com'
PROJECT_URL = "https://github.com/jmchilton/gxformat2"

from .main import convert_and_import_workflow  # NOQA
from .interface import ImporterGalaxyInterface  # NOQA


__all__ = [
    'convert_and_import_workflow',
    'ImporterGalaxyInterface',
]
