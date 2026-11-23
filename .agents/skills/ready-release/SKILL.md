---
name: ready-release
description: Walk a maintainer through cutting a gxformat2 release (changelog, checks, make release, GitHub release).
---

Walk me through readying a gxformat2 release. The full process is documented in `docs/developing.rst` — read that first and defer to it for details. This command drives the interactive parts.

## Steps

1. **Confirm target version** — read `__version__` in `gxformat2/__init__.py` and list the PRs merged since the last tag (`git log --oneline --merges <last-tag>..<upstream>/main`). Classify each one as patch or minor using "Choosing the version" in `docs/developing.rst`, and quote the change behind any minor call. Show me the current `.devN`, the version the rule gives, and ask me to confirm. Patch is the default, so do not cut a minor release because the `.devN` says so, and do not take a version from a task description without checking it against the rule. If the `.devN` disagrees with the rule, fix `__version__` and the `HISTORY.rst` header in a commit before step 3.

2. **Populate changelog** — run `make add-history`, show me the new `HISTORY.rst` entries for review, pause so I can edit if needed, then commit the result (`make check-release` requires a clean tree).

3. **Pre-release checks** — run `make check-release`. If it fails, stop and report. Do not try to work around failures; fix the underlying issue.

4. **Release** — after I confirm, run `make release`.

5. **GitHub release** — run `make release-notes`, show me the output, and after I confirm create the release with `gh release create` as in `docs/developing.rst`.

Stop after each step and report status before moving to the next.
