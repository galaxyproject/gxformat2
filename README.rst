
.. image:: https://readthedocs.org/projects/pip/badge/?version=latest
   :target: https://galaxy-lib.readthedocs.org

.. image:: https://badge.fury.io/py/planemo.svg
   :target: https://pypi.python.org/pypi/galaxy-lib/

.. image:: https://travis-ci.org/galaxyproject/galaxy-lib.png?branch=master
   :target: https://travis-ci.org/galaxyproject/galaxy-lib

.. image:: https://coveralls.io/repos/galaxyproject/galaxy-lib/badge.svg?branch=master
   :target: https://coveralls.io/r/galaxyproject/galaxy-lib?branch=master


This package defines a high-level Galaxy_ workflow description termed "Format
2". At this point, these workflows are defined entirely client side and
transcoded into traditional (or Format 1?) Galaxy workflows.

The traditional Galaxy workflow description is not meant to be concise and is
neither readily human readable or human writable. Format 2 addresses all three
of these limitations.

Format 2 workflow is a highly experimental format and will change rapidly in
potentially backward incompatible ways until the code is merged into the
Galaxy server and enabled by default.

* Free software: Academic Free License version 3.0
* Documentation: https://galaxy-lib.readthedocs.org.
* Code: https://github.com/galaxyproject/galaxy-lib


.. _Galaxy: http://galaxyproject.org/
.. _GitHub: https://github.com/
.. _Travis CI: http://travis-ci.org/
