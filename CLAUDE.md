# gxformat2

Galaxy Workflow Format 2 - library for converting between Format2 (YAML) and native Galaxy (.ga) workflow representations.

## Setup

```bash
uv sync --group test --group lint --group mypy
```

## Running Tests

```bash
uv run --group test pytest tests/ -x -q
```

Set `GXFORMAT2_TEST_IWC_DIRECTORY` to a local clone of the IWC repository to enable additional integration tests that exercise real-world workflows (conversion, linting, round-tripping). If you know of an IWC checkout, set it during test runs.

## Linting

```bash
uv run --group lint ruff check
uv run --group lint flake8
uv run --group lint black --check --diff .
uv run --group mypy mypy gxformat2
```

## Project Structure

- `gxformat2/converter.py` - Format2 → native Galaxy conversion
- `gxformat2/export.py` - native Galaxy → Format2 conversion
- `gxformat2/normalize.py` - Format2 normalization (step outs, anonymous refs)
- `gxformat2/model.py` - Shared utilities (types, source parsing, step helpers)
- `gxformat2/lint.py` - Workflow linting
- `gxformat2/abstract.py` - Abstract CWL export
- `tests/_helpers.py` - Test utilities: `to_native()`, `from_native()`, `round_trip()`, `MockGalaxyInterface`
- `tests/example_wfs.py` - Workflow YAML strings used as test fixtures

## Schema & Pydantic Models

Source YAML schemas (schema-salad format) live in `schema/`:
- `schema/v19_09/workflow.yml` - Format2 schema definition
- `schema/native_v0_1/workflow.yml` - Native Galaxy workflow schema definition
- `schema/common/common.yml` - Shared record definitions (uses `pydantic:` namespace for type overrides)

Generated Python models land in `gxformat2/schema/` — **do not hand-edit**:
- `gxformat2/schema/gxformat2.py` / `gxformat2_strict.py` - Format2 Pydantic v2 models (lax/strict)
- `gxformat2/schema/native.py` / `native_strict.py` - Native workflow Pydantic v2 models (lax/strict)
- `gxformat2/schema/v19_09.py` / `native_v0_1.py` - Legacy schema-salad-tool codegen (large files)

Hand-written Pydantic models that extend the generated ones:
- `gxformat2/normalized/_format2.py` - Normalized Format2 models
- `gxformat2/normalized/_native.py` - Normalized native workflow models
- `gxformat2/normalized/_conversion.py` - Expanded workflow models
- `gxformat2/cytoscape/models.py` - Cytoscape.js visualization models

### Regenerating Schemas

```bash
bash build_schema.sh
```

Uses `schema-salad-plus-pydantic` (Pydantic v2) and `schema-salad-tool` (legacy codegen). Key env vars:
- `SKIP_PYDANTIC=1` - Skip Pydantic model generation
- `GXFORMAT2_SCHEMA_BUILD_DRY_RUN=1` - Write to temp dir (used by `make lint`)
- `SKIP_JAVA=1` / `SKIP_TYPESCRIPT=1` - Skip Java/TS codegen

Generated files are excluded from ruff linting in `pyproject.toml`.

## Key Patterns

- **Round-trip testing**: `round_trip(yaml_string)` converts Format2→native→Format2 and validates
- **Source references**: Format2 uses `step_label/output_name` with `/` as separator. `resolve_source_reference()` in model.py handles labels containing `/`
- Test workflows are defined as string constants in `tests/example_wfs.py`
- `walk_id_list_or_dict()` in normalize.py handles both dict and list step/input representations
