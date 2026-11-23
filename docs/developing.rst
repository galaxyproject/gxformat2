==========
Developing
==========

This page describes how to set up a development environment for gxformat2
and how to cut a release.

Development Setup
=================

Create a virtualenv with dev dependencies installed::

    make setup-venv

This runs ``uv sync``. The ``test``, ``lint``, ``mypy``, ``pyrefly``, and ``docs``
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
    make lint         # ruff, flake8, black, mypy, pyrefly, schema build dry-run
    make lint-docs    # rebuild Sphinx HTML and check for warnings

Set ``GXFORMAT2_TEST_IWC_DIRECTORY`` to a local clone of the IWC repository
to enable integration tests that exercise real-world workflows.

Releases
========

gxformat2 publishes to PyPI via GitHub Actions trusted publishing — no
``~/.pypirc`` or PyPI credentials are needed on the release machine. Pushing
a version tag to ``galaxyproject/gxformat2`` triggers the publish workflow.

**Agents:** the ``ready-release`` skill
(``.agents/skills/ready-release/SKILL.md``) walks through this whole process
interactively. Pause for maintainer confirmation before ``make release``
(pushes to upstream and publishes to PyPI) and before publishing the GitHub
release (its ``@`` acknowledgements notify contributors).

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

Choosing the version
--------------------

gxformat2 is still ``0.x``, so the minor number does the job a major number
would do under semantic versioning. Galaxy and Planemo pin or bound
gxformat2, so the version tells them whether an upgrade can break them.

* **Patch** (``0.Y.Z`` → ``0.Y.Z+1``) is the default. Use it for bug fixes,
  documentation, CI and dependency updates, and backward-compatible
  additions: new optional schema fields, new lint warnings or infos, new
  functions, commands or options whose defaults keep the old behaviour.
* **Minor** (``0.Y.Z`` → ``0.Y+1.0``) when a downstream consumer may have to
  change code or data to upgrade:

  * a public module, function, class, constant, CLI option or declarative
    operation is removed or renamed, or its signature or return shape
    changes incompatibly;
  * the schema or strict validation rejects workflows it used to accept;
  * conversion, normalization or export output changes for existing
    workflows, other than fixing a bug;
  * a supported Python version is dropped or a dependency's minimum is
    raised past what Galaxy pins.

  One such change makes the whole release minor.
* **Major** (``1.0.0``) is not a per-release decision. It marks declaring the
  format and API stable, which the maintainers decide separately.

Bugs fixed by a behaviour change still count as patch, but name the change in
``HISTORY.rst`` so downstream projects can find it.

Whoever merges a minor-level change bumps ``__version__`` on ``main`` to the
next minor ``.dev0`` (e.g. ``0.30.1.dev0`` → ``0.31.0.dev0``) in the same PR
or straight after, so the dev version on ``main`` always names the release it
will become. After each release ``make release`` starts the next **patch**
``.dev0``. Before cutting a release, read the unreleased PRs against the
list above and confirm the ``.devN`` version. If it is wrong, fix
``__version__`` and the ``.devN`` header in ``HISTORY.rst`` in a commit
before ``make check-release``. When in doubt, ask the other maintainers
rather than defaulting either way.

Cutting the release
-------------------

1. Populate the changelog from merged PRs::

       make add-history

   Review the diff to ``HISTORY.rst``, adjust as needed, and commit it
   (``make check-release`` in the next step requires a clean working tree).

2. Confirm the target version in ``gxformat2/__init__.py`` against
   `Choosing the version`_ (``__version__`` is the ``.devN`` variant of the
   release you intend to cut). Fix it in a commit if it is wrong.

3. ``make check-release``.

4. ``make release`` — this runs ``commit-version``, ``new-version``, and
   ``push-release``, which commits the version bump, tags the release,
   bumps ``__version__`` to the next patch ``.dev0``, and pushes ``main`` plus
   the tag to ``UPSTREAM``. The pushed tag triggers the PyPI publish
   workflow on GitHub.

5. Create the GitHub release for the tag. ``make release`` only pushes the
   tag; the release page is a separate step. Its body is the version's
   ``HISTORY.rst`` entries as Markdown, printed by::

       make release-notes               # latest tag
       make release-notes RELEASE_TAG=X.Y.Z

   * **GitHub UI** — on the repository's *Releases* page choose *Draft a new
     release*, pick the existing ``X.Y.Z`` tag, title it ``X.Y.Z``, paste the
     ``make release-notes`` output, and publish.
   * **CLI** — with `gh <https://cli.github.com/>`__::

         make release-notes > notes.md
         gh release create X.Y.Z --repo galaxyproject/gxformat2 \
             --title X.Y.Z --verify-tag --notes-file notes.md

If you need finer control the release can be broken into its pieces:
``make release-local`` (commit, tag, next-dev) followed by
``make push-release`` (push main and tags).
