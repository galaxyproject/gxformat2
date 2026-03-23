Example Workflows
=================

Galaxy workflow examples shipped with gxformat2 for testing and downstream use (e.g. Planemo).

Usage
-----

.. code-block:: python

    from gxformat2.examples import get_path, load, load_contents, load_catalog

    # Get file path
    path = get_path("real-unicycler-assembly.ga")

    # Load as parsed dict
    workflow_dict = load("synthetic-basic.gxwf.yml")

    # Load as raw string
    yaml_str = load_contents("synthetic-basic.gxwf.yml")

    # Load full catalog with pydantic models
    for entry in load_catalog():
        print(entry.name, entry.origin, entry.workflow_label)

Naming Convention
-----------------

Pattern: ``{origin}-{description}[-{variant}].{ext}``

**Origin prefix** (required):

.. list-table::
   :header-rows: 1

   * - Prefix
     - Meaning
   * - ``real``
     - Exported from a real Galaxy instance, unmodified
   * - ``real-hacked``
     - Real workflow with manual edits (removed tools, added tags, etc.)
   * - ``synthetic``
     - Hand-written for testing purposes
   * - ``converted``
     - Machine-generated from another format

**Description**: kebab-case, descriptive. E.g. ``basic``, ``nested-subworkflow``, ``unicycler-assembly``.

**Variant** (optional): appended with ``-`` for variations. E.g. ``-dict-tool-state``, ``-bad-identifier``.

**Extension**: ``.gxwf.yml`` for Format2 YAML, ``.ga`` for native Galaxy JSON.

Catalog
-------

The authoritative catalog is ``gxformat2/examples/catalog.yml``. Workflow metadata
(label, annotation) is read from the workflow files themselves. A test validates
that all catalog entries point to existing files and all example files appear in the catalog.

.. examples-catalog::
