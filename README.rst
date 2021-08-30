
.. image:: https://readthedocs.org/projects/gxformat2/badge/?version=latest
   :target: https://gxformat2.readthedocs.io/en/latest/

.. image:: https://badge.fury.io/py/gxformat2.svg
   :target: https://pypi.python.org/pypi/gxformat2/

.. image:: https://github.com/galaxyproject/gxformat2/workflows/Python%20CI/badge.svg
   :target: https://github.com/galaxyproject/gxformat2/actions?query=workflow%3A%22Python+CI%22

.. image:: https://github.com/galaxyproject/gxformat2/workflows/Java%20CI/badge.svg
   :target: https://github.com/galaxyproject/gxformat2/actions?query=workflow%3A%22Java+CI%22

.. image:: https://img.shields.io/badge/latest%20schema-v19.09-blue
   :target: https://galaxyproject.github.io/gxformat2/v19_09.html

Format 2
--------

This package defines a high-level Galaxy_ workflow description termed "Format
2". The current schema version is v19_09 and the schema can be found
`here <https://galaxyproject.github.io/gxformat2/v19_09.html>`__. This version of
workflow format can be consumed by Galaxy since version 19.09.

The Format 2 workflow description is still somewhat experimental and may
yet change in small potentially backward incompatible ways until the format is
exported by Galaxy by default.

The traditional Galaxy workflow description (files ending in ``.ga`` extension,
sometimes called native workflows in this project) was not designed to be
concise and is neither readily human readable or human writable. Galaxy
workflow Format 2 is being designed to address these limitations,
while also moving Galaxy's workflow description language toward standards such
as the Common Workflow Language.

gxformat2
---------

This Python project can be installed from PyPI using ``pip``.

::

    $ pip install gxformat2

Checkout the project tests or how it used in projects such as Planemo and
Galaxy to see how to use the gxformat2 library. Reference documentation for
the `modules <https://gxformat2.readthedocs.io/en/latest/py-modindex.html>`__
can be found as part of the project's documentation.

This project also includes various scripts for working with Galaxy workflows.
Checkout their help for more information.

::

    $ gxwf-lint --help
    $ gxwf-viz --help
    $ gxwf-abstract-export --help

This library and associated scripts are licensed under the MIT License.

.. _Galaxy: https://galaxyproject.org/
