Walk me through readying a gxformat2 release. The full process is documented in `docs/developing.rst` — read that first and defer to it for details. This command drives the interactive parts.

## Steps

1. **Confirm target version** — read `__version__` in `gxformat2/__init__.py`, show me the current `.devN`, and ask me to confirm the target release version.

2. **Populate changelog** — run `make add-history`, show me the new `HISTORY.rst` entries for review, pause so I can edit if needed, then commit the result (`make check-release` requires a clean tree).

3. **Pre-release checks** — run `make check-release`. If it fails, stop and report. Do not try to work around failures; fix the underlying issue.

4. **Release** — after I confirm, run `make release`.

Stop after each step and report status before moving to the next.
