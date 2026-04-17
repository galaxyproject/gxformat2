"""Back-compat shim tests for :mod:`gxformat2.interface`.

Planemo <= 0.75.41 imports ``BioBlendImporterGalaxyInterface`` and
``ImporterGalaxyInterface`` from ``gxformat2.interface``. The module was
removed in PR #161 and restored as a deprecated shim; this guards against
it being silently re-removed.
"""

import abc
import warnings


def test_interface_imports_emit_deprecation_warning():
    import importlib
    import sys

    sys.modules.pop("gxformat2.interface", None)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        importlib.import_module("gxformat2.interface")
    deprecation = [w for w in caught if issubclass(w.category, DeprecationWarning)]
    assert deprecation, "Expected DeprecationWarning from gxformat2.interface"


def test_importer_galaxy_interface_is_abstract():
    from gxformat2.interface import ImporterGalaxyInterface

    assert isinstance(ImporterGalaxyInterface, abc.ABCMeta)
    assert "import_workflow" in ImporterGalaxyInterface.__abstractmethods__


def test_bioblend_importer_class_importable_without_bioblend():
    """Importing the class must not require bioblend; only instantiation does."""
    from gxformat2.interface import BioBlendImporterGalaxyInterface

    assert BioBlendImporterGalaxyInterface.__name__ == "BioBlendImporterGalaxyInterface"
