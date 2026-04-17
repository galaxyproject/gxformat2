"""Compatibility shim for :mod:`gxformat2.interface`.

.. deprecated:: 0.26.0
    This module was removed in gxformat2 0.23 (PR #161) and has been restored
    solely as a compatibility shim for downstream consumers (notably Planemo).
    It may be removed again in a future release. New code should implement
    its own Galaxy importer interface or depend on Galaxy / BioBlend directly.

``bioblend`` is no longer a hard dependency of gxformat2. Install the
``bioblend`` extra (``pip install gxformat2[bioblend]``) or install
``bioblend`` separately to use :class:`BioBlendImporterGalaxyInterface`.
"""

from __future__ import annotations

import abc
import warnings

warnings.warn(
    "gxformat2.interface is deprecated and only provided for backward "
    "compatibility with Planemo. It may be removed in a future release.",
    DeprecationWarning,
    stacklevel=2,
)


class ImporterGalaxyInterface(metaclass=abc.ABCMeta):
    """An abstract interface describing Galaxy operations used by gxformat2.

    Specifically containing definitions of operations required to load
    workflows into Galaxy.
    """

    @abc.abstractmethod
    def import_workflow(self, workflow, **kwds):
        """Import a workflow via POST /api/workflows or comparable interface into Galaxy."""


class BioBlendImporterGalaxyInterface:
    """Implementation of :class:`ImporterGalaxyInterface` using bioblend.

    ``bioblend`` is imported lazily so importing :mod:`gxformat2.interface`
    does not require it to be installed.
    """

    def __init__(self, **kwds):
        """Build a :class:`bioblend.GalaxyInstance` from supplied arguments."""
        import bioblend  # type: ignore[import-not-found]

        url = None

        admin_key = None
        admin_gi = None
        if "admin_gi" in kwds:
            admin_gi = kwds["admin_gi"]
        elif "gi" in kwds:
            admin_gi = kwds["gi"]
        elif "url" in kwds and "admin_key" in kwds:
            url = kwds["url"]
            admin_key = kwds["admin_key"]

        if admin_gi is None:
            assert url is not None
            assert admin_key is not None
            admin_gi = bioblend.GalaxyInstance(url=url, key=admin_key)

        user_key = None
        user_gi = None
        if "user_gi" in kwds:
            user_gi = kwds["user_gi"]
        elif "gi" in kwds:
            user_gi = kwds["gi"]
        elif "url" in kwds and "user_key" in kwds:
            url = kwds["url"]
            user_key = kwds["user_key"]

        if user_gi is None:
            assert url is not None
            assert user_key is not None
            user_gi = bioblend.GalaxyInstance(url=url, key=user_key)

        self._admin_gi = admin_gi
        self._user_gi = user_gi

    def import_workflow(self, workflow, **kwds):
        """Import Galaxy workflow using instance :class:`bioblend.GalaxyInstance` object."""
        return self._user_gi.workflows.import_workflow_json(workflow, **kwds)


__all__ = ("ImporterGalaxyInterface", "BioBlendImporterGalaxyInterface")
