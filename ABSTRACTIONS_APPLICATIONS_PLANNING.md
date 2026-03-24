# Beyond Conversion: Applications of the Layered Architecture

Assumes the conversion+expansion plan (GXFORMAT2_CONVERSION_AND_EXPANSION.md) is complete. This captures design decisions and next steps discussed during the architecture session.

## The Full Layer Stack

```
Layer 0: Raw dicts
Layer 1: Pydantic models (auto-generated schema validation)
Layer 2: Normalized models (structural resolution, single-format)
Layer 3: Expanded models (conversion + reference resolution, cross-format)
Layer 4: Applications (linting, abstract CWL, visualization, etc.)
```

## Key Design Decisions Made

### ConversionContext is internal

Callers never see it. Public interface is `ConversionOptions` — a plain options object carrying `workflow_directory`, encoding prefs, callbacks, and `expand` flag. The context (labels, graph_ids, subworkflow nesting, cycle detection) is built and managed inside conversion functions.

### galaxy_interface removed from conversion

`import_tool` dropped — `GalaxyUserTool` is pure source conversion via `tool_representation`. `import_workflow` was never a conversion concern — it was Galaxy test infrastructure (`convert_and_import_workflow`). Galaxy PR planned to drop that dependency (SIMPLIFY_GXFORMAT2_CONTRACT_IN_GALAXY_PLAN.md).

### URL resolution owned by gxformat2

CLI tooling (Planemo, IWC CI, linting) needs to resolve URL and TRS URL references without a Galaxy server. gxformat2 provides a default `url_resolver` (HTTP fetch + YAML parse + TRS descriptor extraction). Galaxy plugs in its own resolver with allowlists/policy via `ConversionOptions.url_resolver` callback.

No TRS server registry needed — TRS URLs are self-contained (base URL is in the URL). Galaxy's split-form TRS ID (`trs_server` + `trs_tool_id` + `trs_version_id`) dropped from serialized format per galaxyproject/galaxy#21887.

### Normalized vs Expanded is about what run/subworkflow can be

- **Normalized**: `run: Any` (inline workflow, URL string, `@import` dict — whatever the source had). Good for visualization, linting, structural analysis.
- **Expanded**: `run: ExpandedFormat2 | None` (all references resolved). Required for deep validation, conversion, anything that needs the full picture.

No artificial fields (`run_ref`) — two model tiers, each with clean types.

### WorkflowStep.run schema needs widening

Currently `run: GalaxyWorkflow | None` in the auto-generated schema — rejects URL strings at `model_validate` time. Needs to become `run: Any` (or `GalaxyWorkflow | str | dict | None`) so `normalized_format2()` can handle workflows with URL run references without crashing. This is a schema definition fix in `schema/v19_09/workflow.yml`, prerequisite for the expanded layer.

## What normalize.py Becomes

The existing dict-based normalization helpers (`NormalizedWorkflow`, `Inputs`, `steps_normalized`, `inputs_normalized`, `walk_id_list_or_dict`) predate the normalized models. Once applications migrate to using `NormalizedFormat2` / `NormalizedNativeWorkflow`:

- `Inputs` → `NormalizedFormat2.inputs` (already a list with ids)
- `steps_normalized()` → `NormalizedFormat2.steps` (already a list with ids)
- `inputs_normalized()` → `NormalizedFormat2.inputs`
- `outputs_normalized()` → `NormalizedFormat2.outputs`
- `walk_id_list_or_dict` → unnecessary on normalized models (still available for raw dicts)
- `_collect_known_labels` → trivial: `{s.id for s in wf.steps} | {i.id for i in wf.inputs}`
- `NormalizedWorkflow` → thin wrapper around `normalized_format2()` or deprecated

The anonymous output reference rewriting (`_replace_anonymous_output_references`) and implicit step-out insertion (`_ensure_implicit_step_outs`) are content transforms, not structural normalization. They stay separate — possibly as methods on `NormalizedFormat2` or standalone functions that return new model instances.

## Application Migration Path

### Linting (lint.py)

Currently operates on raw dicts. Migration path:

1. `lint_ga` → use `NormalizedNativeWorkflow` for typed step access, eliminate `ensure_key` checks that pydantic validation already covers
2. `lint_format2` → use `NormalizedFormat2` for typed access
3. `lint_pydantic_validation` → already uses pydantic models, no change
4. `lint_best_practices_ga/format2` → use normalized models, eliminate `.get()` chains

Being worked on in a separate branch already.

### Abstract CWL Export (abstract.py)

Currently operates on Format2 dicts via `NormalizedWorkflow`. Migration:

- `from_dict()` → accept `NormalizedFormat2` directly
- Anonymous output rewriting and implicit step-outs already handled by `NormalizedWorkflow` — these move to `NormalizedFormat2` methods or pre-processing
- Step iteration simplified — no `walk_id_list_or_dict`, just iterate `.steps`

### Cytoscape Visualization (cytoscape.py)

Currently loads from path, normalizes steps. Would benefit from `NormalizedFormat2` — steps always a list with ids, no dict-or-list handling.

For workflows with unresolved `run` references (URL subworkflows), the normalized model is sufficient — visualization just shows the reference, doesn't need the full subworkflow. The expanded model is needed only if you want to visualize nested subworkflow contents.

### CLI Tools

`gxwf-to-native` and `gxwf-to-format2` entry points currently use `python_to_workflow` / `from_galaxy_native`. Migration:

```python
# gxwf-to-native
options = ConversionOptions(workflow_directory=..., expand=args.expand)
result = to_native(workflow, options)

# gxwf-to-format2
options = ConversionOptions(compact=args.compact)
result = to_format2(workflow, options)
```

With `--expand` flag, CLI tools resolve `@import` and URL references automatically via the built-in default resolver.

## Galaxy-side Follow-ups

### SIMPLIFY_GXFORMAT2_CONTRACT_IN_GALAXY_PLAN.md

- Remove `convert_and_import_workflow` usage from Galaxy test infrastructure
- Remove `ImporterGalaxyInterface` from test populator class hierarchies
- Remove `Format2ConverterGalaxyInterface` (pass `None` to `python_to_workflow`)
- Drop `import_tool` from test populators

### Galaxy callback migration

- `native_state_encoder` — currently receives `(step_dict, state_dict)`. New API receives `(NormalizedWorkflowStep, state_dict)`. Galaxy is the only consumer and it was recently added, so updating the signature is fine.
- `convert_tool_state` — currently receives a step dict via `model_dump()`. Could receive `NormalizedNativeStep` model directly, or keep dict for backward compat.

### Galaxy URL resolver

Galaxy provides its own `url_resolver` via `ConversionOptions` that wraps `stream_url_to_str` with allowlist validation, TRS proxy, and admin checks. The default gxformat2 resolver handles CLI use cases.

## Open Design Questions

1. **`requests` as runtime dep** — gxformat2's default URL resolver needs it. Currently transitive via `bioblend` but we just dropped `bioblend`. Add as explicit dep, or make it optional with clear import error?

2. **Backward compat duration** — how long do `python_to_workflow`, `from_galaxy_native`, `ImportOptions` stay as deprecated wrappers? Until next major version?

3. **normalize.py deprecation** — the dict-based helpers are used by abstract.py, lint.py, and potentially external consumers. Deprecate once applications migrate, or keep indefinitely as the "raw dict" layer?

4. **Extra fields passthrough** — both Format2 and native models use `extra="allow"`. When converting between formats, which extra fields transfer? Need audit of what Galaxy puts in extra fields.

5. **`NormalizedFormat2.steps` includes inputs?** — `steps_normalized()` returns inputs + steps in one list. `NormalizedFormat2` keeps them separate. Some consumers want a unified list. Add a property `all_steps` that concatenates, or keep separate and let consumers combine?

6. **Anonymous output rewriting** — incorporate into `normalized_format2()` or keep as opt-in transform? It changes content (adds labels), not just structure. Leaning toward opt-in method on the model.

7. **base64:// URLs** — Galaxy tests use these for inline workflow content. Support in default resolver? Trivial to implement (base64 decode + parse).
