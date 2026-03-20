# gxformat2

Galaxy Workflow Format 2 - library for converting between Format2 (YAML) and native Galaxy (.ga) workflow representations.

## Setup

```bash
uv venv --clear && uv pip install -e . && uv pip install pytest
```

For full dev deps: `uv pip install -r dev-requirements.txt`

## Running Tests

```bash
.venv/bin/pytest tests/ -x -q --ignore=tests/test_export_abstract.py
```

`test_export_abstract.py` requires `cwltool` (optional heavy dep). Skip it for normal dev work.

For CI-style runs: `tox -e py313-unit`

## Project Structure

- `gxformat2/converter.py` - Format2 → native Galaxy conversion
- `gxformat2/export.py` - native Galaxy → Format2 conversion
- `gxformat2/normalize.py` - Format2 normalization (step outs, anonymous refs)
- `gxformat2/model.py` - Shared utilities (types, source parsing, step helpers)
- `gxformat2/lint.py` - Workflow linting
- `gxformat2/abstract.py` - Abstract CWL export
- `tests/_helpers.py` - Test utilities: `to_native()`, `from_native()`, `round_trip()`, `MockGalaxyInterface`
- `tests/example_wfs.py` - Workflow YAML strings used as test fixtures

## Key Patterns

- **Round-trip testing**: `round_trip(yaml_string)` converts Format2→native→Format2 and validates
- **Source references**: Format2 uses `step_label/output_name` with `/` as separator. `resolve_source_reference()` in model.py handles labels containing `/`
- Test workflows are defined as string constants in `tests/example_wfs.py`
- `walk_id_list_or_dict()` in normalize.py handles both dict and list step/input representations
