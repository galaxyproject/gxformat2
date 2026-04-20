==========
Developing
==========

This page describes how to set up a development environment for gxformat2
and how to cut a release.

Development Setup
=================

Create a virtualenv with dev dependencies installed::

    make setup-venv

This runs ``uv sync``. The ``test``, ``lint``, ``mypy``, and ``docs``
dependency groups are marked as ``default-groups`` in ``pyproject.toml``
so they install automatically.

Optional pre-commit hooks are configured via `pre-commit
<https://pre-commit.com/>`_. A sample configuration ships as
``.pre-commit-config.yaml.sample``. Install the hook with::

    make setup-pre-commit

This uses ``.pre-commit-config.yaml`` if you have one (copy the sample and
customize), and otherwise falls back to the committed
``.pre-commit-config.yaml.sample``.

Running Tests and Linters
=========================

::

    make test         # pytest
    make lint         # ruff, flake8, black, mypy, schema build dry-run
    make lint-docs    # rebuild Sphinx HTML and check for warnings

Set ``GXFORMAT2_TEST_IWC_DIRECTORY`` to a local clone of the IWC repository
to enable integration tests that exercise real-world workflows.

Releases
========

gxformat2 publishes to PyPI via GitHub Actions trusted publishing — no
``~/.pypirc`` or PyPI credentials are needed on the release machine. Pushing
a version tag to ``galaxyproject/gxformat2`` triggers the publish workflow.

Pre-release checklist
---------------------

Run::

    make check-release

This verifies:

* ``.venv`` exists (or ``uv`` is available).
* Working tree is clean (no uncommitted or untracked files).
* The ``UPSTREAM`` git remote exists and points to ``UPSTREAM_REPO``
  (defaults: ``galaxyproject`` / ``galaxyproject/gxformat2``).
* ``HISTORY.rst`` has entries under the current ``.devN`` section.
* ``make clean``, ``make lint``, and ``make lint-docs`` all pass.

Fork maintainers can override the defaults::

    make check-release UPSTREAM=myfork UPSTREAM_REPO=me/gxformat2

Cutting the release
-------------------

1. Populate the changelog from merged PRs::

       make add-history

   Review the diff to ``HISTORY.rst``, adjust as needed, and commit it
   (``make check-release`` in the next step requires a clean working tree).

2. Confirm the target version in ``gxformat2/__init__.py`` (``__version__``
   is the ``.devN`` variant of the release you intend to cut).

3. ``make check-release``.

4. ``make release`` — this runs ``commit-version``, ``new-version``, and
   ``push-release``, which commits the version bump, tags the release,
   bumps ``__version__`` to the next ``.dev0``, and pushes ``main`` plus
   the tag to ``UPSTREAM``. The pushed tag triggers the PyPI publish
   workflow on GitHub.

If you need finer control the release can be broken into its pieces:
``make release-local`` (commit, tag, next-dev) followed by
``make push-release`` (push main and tags).
