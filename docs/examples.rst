Workflow Fixtures
=================

.. warning::

   These workflows are **test fixtures**, not examples of best-practice Galaxy workflows.
   They are designed to exercise specific code paths, edge cases, and linting checks.
   Many deliberately omit metadata, contain invalid references, or trigger warnings.
   Projects like Planemo can depend on these fixtures for shared test data.

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

The authoritative catalog is
`gxformat2/examples/catalog.yml <https://github.com/galaxyproject/gxformat2/blob/main/gxformat2/examples/catalog.yml>`_.
Workflow metadata (label, annotation) is read from the workflow files themselves.
A test validates that all catalog entries point to existing files and all example files appear in the catalog.

Each fixture's test coverage is split into two categories:

- **Python Tests** — conventional pytest modules (``tests/test_*.py``)
- **Interoperable Tests** — YAML-driven declarative expectations
  (``gxformat2/examples/expectations/*.yml``) that are language-agnostic
  and can be reused from TypeScript or other implementations

.. examples-catalog::

Interoperable (Declarative) Tests
-----------------------------------

Interoperable tests are YAML-driven expectation files in
``gxformat2/examples/expectations/``. Unlike conventional Python tests,
these are language-agnostic — the same expectation files drive both the
Python test suite (via pytest) and can be consumed by TypeScript or other
implementations. Each file contains named test cases specifying a fixture,
an operation, and a list of path-based assertions against the result.

.. code-block:: yaml

    test_to_native_basic_structure:
      fixture: synthetic-basic.gxwf.yml
      operation: to_native
      assertions:
        - path: [a_galaxy_workflow]
          value: "true"
        - path: [steps, "1", tool_id]
          value: cat1
        - path: [steps, "1", workflow_outputs, $length]
          value: 1

**Path elements:**

.. list-table::
   :header-rows: 1

   * - Element
     - Meaning
   * - ``str``
     - Dict key lookup (falls back to attribute access)
   * - ``int``
     - List index
   * - ``$length``
     - Terminal — returns ``len(current)``
   * - ``{field: value}``
     - Find first list item where ``item.field == value``

**Assertion modes:**

.. list-table::
   :header-rows: 1

   * - Key
     - Check
   * - ``value``
     - Exact equality (``None``, str, int, list, dict)
   * - ``value_contains``
     - Substring containment
   * - ``value_set``
     - Unordered set comparison (for ``frozenset`` properties like ``unique_tools``)

**Available operations:**

- Normalization: ``normalized_format2``, ``normalized_native``, ``expanded_format2``, ``expanded_native``
- Conversion: ``to_format2``, ``to_native``, ``ensure_format2``, ``ensure_native``
- Validation: ``validate_format2``, ``validate_format2_strict``, ``validate_native``, ``validate_native_strict``
- Linting: ``lint_format2``, ``lint_native`` — return ``{errors, warnings, error_count, warn_count}``

**Special keys:**

- ``assertions`` may be omitted or empty — the operation succeeding is the test
- ``expect_error: true`` — the operation must raise; test passes on error, fails on success

.. code-block:: yaml

    # Positive: operation succeeds, no assertions needed
    test_basic_valid_format2:
      fixture: synthetic-basic.gxwf.yml
      operation: validate_format2_strict

    # Negative: operation must fail
    test_extra_field_rejected:
      fixture: synthetic-extra-field.gxwf.yml
      operation: validate_format2_strict
      expect_error: true

The Python test runner (``tests/test_interop_tests.py``) parametrizes
all cases and runs them via pytest.

Expectation Files
~~~~~~~~~~~~~~~~~

.. expectations-catalog::
