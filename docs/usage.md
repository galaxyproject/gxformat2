# Working with Galaxy Workflow Models

This guide describes the typed model layers available for programmatically
working with Galaxy workflows. The layers are organized from highest
convenience (top) to lowest level (bottom):

```
  ┌─────────────────────────────────────────────────────┐
  │  ensure_format2() / ensure_native()                 │
  │  "Give me any workflow, I'll give you typed models"  │
  │  Auto-detects format, converts, normalizes, expands │
  │  ↳ from gxformat2.to_format2 / gxformat2.to_native │
  ├─────────────────────────────────────────────────────┤
  │  Expanded Models                                    │
  │  ExpandedFormat2 / ExpandedNativeWorkflow            │
  │  All subworkflow refs resolved to inline models     │
  │  ↳ from gxformat2.normalized                        │
  ├─────────────────────────────────────────────────────┤
  │  Normalized Models                                  │
  │  NormalizedFormat2 / NormalizedNativeWorkflow         │
  │  Structural guarantees: lists, ids, parsed state    │
  │  ↳ from gxformat2.normalized                        │
  ├─────────────────────────────────────────────────────┤
  │  Schema Models (lax / strict)                       │
  │  GalaxyWorkflow / NativeGalaxyWorkflow               │
  │  Direct pydantic parse — no normalization           │
  │  ↳ from gxformat2.schema.gxformat2                  │
  │  ↳ from gxformat2.schema.native                     │
  ├─────────────────────────────────────────────────────┤
  │  Raw dicts                                          │
  │  yaml.ordered_load() / json.load()                  │
  │  No validation, no types                            │
  └─────────────────────────────────────────────────────┘
```

## The `ensure_` Layer — Recommended Entry Point

The {py:func}`~gxformat2.to_format2.ensure_format2` and
{py:func}`~gxformat2.to_native.ensure_native` functions are the primary way to
get typed workflow models. They accept **any** workflow representation and
return normalized (or expanded) models in the target format, handling
format detection and conversion automatically.

### ensure_format2

```python
from gxformat2.to_format2 import ensure_format2

# From a file path (native .ga or Format2 .gxwf.yml)
nf2 = ensure_format2("workflow.ga")
nf2 = ensure_format2("workflow.gxwf.yml")

# From a raw dict (auto-detects native vs Format2)
nf2 = ensure_format2(workflow_dict)

# From any typed model — passes through or converts
nf2 = ensure_format2(native_galaxy_workflow)
nf2 = ensure_format2(normalized_native_workflow)
nf2 = ensure_format2(galaxy_workflow_schema_model)

# With expansion (resolves @import, URLs, subworkflow refs)
from gxformat2.options import ConversionOptions
expanded = ensure_format2(workflow, options=ConversionOptions(), expand=True)
```

**Returns:** {py:class}`~gxformat2.normalized.NormalizedFormat2` by default,
{py:class}`~gxformat2.normalized.ExpandedFormat2` when `expand=True`.
Overloads provide correct static types based on the `expand` literal.

### ensure_native

```python
from gxformat2.to_native import ensure_native

# Same flexibility — any input format
nnw = ensure_native("workflow.gxwf.yml")
nnw = ensure_native(native_dict)
nnw = ensure_native(normalized_format2_model)

# With expansion
expanded = ensure_native(workflow, options=ConversionOptions(), expand=True)
```

**Returns:** {py:class}`~gxformat2.normalized.NormalizedNativeWorkflow` by
default, {py:class}`~gxformat2.normalized.ExpandedNativeWorkflow` when
`expand=True`.

### Format Detection

For raw dicts, the functions detect the format by inspecting keys:

- `a_galaxy_workflow == "true"` → native Galaxy format
- `class == "GalaxyWorkflow"` → Format2

For file paths (`str` or `Path`), the file is loaded and then inspected.
Typed model inputs ({py:class}`~gxformat2.normalized.NormalizedFormat2`,
{py:class}`~gxformat2.schema.native.NativeGalaxyWorkflow`, etc.) are
routed by `isinstance` checks — already-normalized models pass through
without re-processing.

### Access Patterns for Applications

Once you have a {py:class}`~gxformat2.normalized.NormalizedFormat2`, the
model provides structured typed access to all workflow components:

```python
nf2 = ensure_format2(workflow)

# Workflow metadata
nf2.label          # str | None
nf2.doc            # str | None (joined if originally a list)
nf2.tags           # list[str] | None
nf2.creator        # list[CreatorPerson | CreatorOrganization] | None
nf2.license        # str | None

# Inputs — always a list, shorthands expanded
for inp in nf2.inputs:
    inp.id           # str — always populated
    inp.type_        # GalaxyType | list[GalaxyType] | None
    inp.optional     # bool | None
    inp.default      # Any
    inp.doc          # str | None
    inp.position     # StepPosition | None

# Steps — always a list, ids populated
for step in nf2.steps:
    step.id          # str — always populated
    step.label       # str | None
    step.tool_id     # str | None
    step.type_       # WorkflowStepType | None
    step.doc         # str | None (joined if originally a list)
    step.position    # StepPosition | None
    step.run         # NormalizedFormat2 | str | dict | None
    step.in_         # list[WorkflowStepInput] — always a list
    step.out         # list[WorkflowStepOutput] — always a list
    step.connected_paths  # frozenset[str] — input ids with a source connection

# Outputs — always a list
for out in nf2.outputs:
    out.id           # str | None
    out.outputSource # str | None
    out.type_        # GalaxyType | list[GalaxyType] | None
```

### Source Reference Resolution

Format2 workflows reference step outputs using strings like
`"step_label/output_name"`. When step labels themselves contain `/`,
parsing is ambiguous. The normalized layer provides helpers:

```python
# Resolve a source reference against this workflow's steps
ref = nf2.resolve_source("filter_step/output1")
ref.step_label   # "filter_step"
ref.output_name  # "output1"

# known_labels is a cached set of all step labels/ids + input ids
nf2.known_labels  # {"filter_step", "input1", "map_step", ...}

# Works with ambiguous labels containing "/"
# e.g. step labeled "Mass Spec Runs (MS/MS)"
ref = nf2.resolve_source("Mass Spec Runs (MS/MS)/spectra")
ref.step_label   # "Mass Spec Runs (MS/MS)"
ref.output_name  # "spectra"
```

The resolver tries known labels longest-first, then falls back to splitting
on the first `/`. Bare references (no `/`) default to `output_name="output"`.

The standalone function {py:func}`~gxformat2.normalized.resolve_source_reference`
is also available:

```python
from gxformat2.normalized import resolve_source_reference, SourceReference

ref: SourceReference = resolve_source_reference("step/out", known_labels)
```

### ConversionOptions

Both `ensure_` functions and the underlying
{py:func}`~gxformat2.to_format2.to_format2` /
{py:func}`~gxformat2.to_native.to_native` converters accept an optional
{py:class}`~gxformat2.options.ConversionOptions`:

```python
from gxformat2.options import ConversionOptions

options = ConversionOptions(
    workflow_directory="/path/to/dir",  # For resolving @import paths
    url_resolver=my_resolver,          # Custom fetcher for URL refs
)
expanded = ensure_format2(workflow, options=options, expand=True)
```

Key options:
- `workflow_directory` — base path for `@import` resolution
- `url_resolver` — callable for fetching URL / TRS references
- `encode_tool_state_json` — JSON-encode tool_state in native output (default True)
- `state_encode_to_native` — Galaxy-provided callback to encode Format2 state
  back to native `tool_state` (accepts `(step_dict, state_dict)`, returns
  encoded dict or `None` for default)
- `state_encode_to_format2` — Galaxy-provided callback to decode native
  `tool_state` to Format2 `state` (accepts step dict, returns state dict
  or `None` for default)

See {py:class}`~gxformat2.options.ConversionOptions` for the full parameter list.

### Real-World Usage

The application modules in this project all use the `ensure_` layer:

```python
# abstract.py — CWL export
nf2 = ensure_format2(workflow_dict)
for step in nf2.steps:
    if isinstance(step.run, NormalizedFormat2):
        # Recurse into subworkflow
        ...

# cytoscape.py — visualization
nf2 = ensure_format2(workflow_path)
for step in nf2.steps:
    for step_input in step.in_:
        ref = nf2.resolve_source(step_input.source)
        # Build edge from ref.step_label → current step

# lint.py — validation
nf2 = ensure_format2(workflow_dict, expand=True)  # ExpandedFormat2
nnw = ensure_native(workflow_dict)                 # For native-specific checks
```

## Normalized and Expanded Models

For cases where you know the input format and don't need auto-detection,
the {py:mod}`gxformat2.normalized` package provides direct constructors.
For cross-format conversion, {py:func}`~gxformat2.to_format2.to_format2`
and {py:func}`~gxformat2.to_native.to_native` convert between formats and
return normalized (or expanded) models.

### Cross-Format Conversion

{py:func}`~gxformat2.to_format2.to_format2` converts native workflows to
Format2, and {py:func}`~gxformat2.to_native.to_native` converts Format2
workflows to native. Both accept the source format as a raw dict, file
path, or typed model, and return normalized models in the target format:

```python
from gxformat2.to_format2 import to_format2
from gxformat2.to_native import to_native

# Native → Format2
nf2 = to_format2(native_dict)
nf2 = to_format2(normalized_native_workflow)

# Format2 → Native
nnw = to_native(format2_dict)
nnw = to_native(normalized_format2_model)

# With expansion (resolves subworkflow refs in the result)
ef2 = to_format2(native_dict, options=options, expand=True)
enw = to_native(format2_dict, options=options, expand=True)
```

Unlike the `ensure_` functions, these only accept the *other* format as
input — {py:func}`~gxformat2.to_format2.to_format2` expects native input,
{py:func}`~gxformat2.to_native.to_native` expects Format2 input. Use
`ensure_` when you don't know (or don't care about) the input format.

### Normalized Models

{py:class}`~gxformat2.normalized.NormalizedFormat2` guarantees:
- `steps`, `inputs`, `outputs` are always `list` (never dict)
- Step and input `id` fields are always populated
- Input type shorthands expanded (`"File"` → `"data"`, etc.)
- `doc` fields joined from list to string
- `$graph` multi-workflow documents resolved
- `$link` entries in step `state` resolved — replaced with
  `{"__class__": "ConnectedValue"}` in state, connection source
  added to `step.in_`. After normalization, `step.in_` contains
  ALL connections and `step.state` is clean
- Step `type_` always populated — inferred from context when not
  explicit in the YAML (`run` present → `subworkflow`, otherwise →
  `tool`). Convenience properties `is_tool_step`,
  `is_subworkflow_step`, `is_pause_step`, `is_pick_value_step`,
  and `connected_paths` (frozenset of input ids with a source)
  are also available

{py:class}`~gxformat2.normalized.NormalizedNativeWorkflow` guarantees:
- `tool_state` always a parsed `dict` (JSON strings auto-decoded)
- Optional containers default to empty (never `None`)
- `input_connections` values always `list[NativeInputConnection]`
  (single connections wrapped during construction — no `isinstance`
  checks needed)
- `connected_paths` property returns `frozenset[str]` of
  `input_connections` keys — O(1) membership test for checking
  whether a state path has an incoming connection
- Tags normalized (empty string → empty list)
- Subworkflows recursively normalized

All normalized models provide a `to_dict()` method that serializes to
a JSON/YAML-compatible dict with aliases resolved and `None` values
stripped:

```python
nf2 = ensure_format2(workflow)
workflow_dict = nf2.to_dict()  # ready for json.dump() or yaml.dump()

nnw = ensure_native(workflow)
native_dict = nnw.to_dict()   # includes "a_galaxy_workflow", "format-version", etc.
```

```python
from gxformat2.normalized import normalized_format2, normalized_native

# From same-format input
nf2 = normalized_format2(format2_dict)
nf2 = normalized_format2("/path/to/workflow.gxwf.yml")
nf2 = normalized_format2(galaxy_workflow_model)

nnw = normalized_native(native_dict)
nnw = normalized_native("/path/to/workflow.ga")
nnw = normalized_native(native_galaxy_workflow_model)

# normalized_format2 also auto-detects native dicts:
nf2 = normalized_format2(native_dict)  # converts via from_galaxy_native
```

### Expanded Models

{py:class}`~gxformat2.normalized.ExpandedFormat2` and
{py:class}`~gxformat2.normalized.ExpandedNativeWorkflow` inherit from their
normalized counterparts and additionally guarantee all external references
are resolved to inline model instances:

- {py:class}`~gxformat2.normalized.ExpandedFormat2`: every `step.run` is
  `ExpandedFormat2 | None` (no URL strings, no `@import` dicts)
- {py:class}`~gxformat2.normalized.ExpandedNativeWorkflow`: every
  `step.subworkflow` is `ExpandedNativeWorkflow | None` (no `content_id`
  URL refs)

```python
from gxformat2.normalized import expanded_format2, expanded_native
from gxformat2.options import ConversionOptions

options = ConversionOptions(workflow_directory="/path/to/dir")

ef2 = expanded_format2(format2_dict, options)
enw = expanded_native(native_dict, options)

# Also accepts already-normalized models
ef2 = expanded_format2(nf2, options)
```

Expansion fetches `@import` paths, HTTP/TRS URLs, and `$graph` references.
Circular references raise `ValueError`. Max depth is 10.

Use expanded models when you need to traverse into subworkflows (linting,
full-tree analysis). Use normalized models when you only need the top-level
structure (visualization, simple metadata extraction).

## Schema Models — Direct Pydantic Validation

The schema models are auto-generated from schema-salad YAML definitions
using `schema-salad-plus-pydantic`. They provide direct pydantic parsing
with no normalization — fields appear exactly as in the source document.

### Lax Models (extra="allow")

Accept unknown fields. Use for real-world workflows that may contain
Galaxy-version-specific or undocumented fields:

```python
from gxformat2.schema.gxformat2 import GalaxyWorkflow
from gxformat2.schema.native import NativeGalaxyWorkflow

gw = GalaxyWorkflow.model_validate(format2_dict)
ngw = NativeGalaxyWorkflow.model_validate(native_dict)
```

### Strict Models (extra="forbid")

Reject unknown fields. Use for schema compliance checking:

```python
from gxformat2.schema.gxformat2_strict import GalaxyWorkflow as StrictFormat2
from gxformat2.schema.native_strict import NativeGalaxyWorkflow as StrictNative

StrictFormat2.model_validate(format2_dict)   # raises on extra fields
StrictNative.model_validate(native_dict)     # raises on extra fields
```

The linter uses both: strict failure with lax success means only extra
fields are present (warning), while lax failure indicates fundamental
schema errors (error).

### Key Types from the Schema

These types are used throughout the model hierarchy:

```python
from gxformat2.schema.gxformat2 import (
    GalaxyType,              # Enum: data, collection, string, int, float, ...
    WorkflowStepType,        # Enum: tool, subworkflow, pause, pick_value
    WorkflowInputParameter,  # Input definition
    WorkflowOutputParameter, # Output definition
    WorkflowStepInput,       # Step input (source, default)
    WorkflowStepOutput,      # Step output (id)
    CreatorPerson,           # Creator with name, identifier, ...
    CreatorOrganization,     # Organization creator
    Report,                  # Invocation report template
)

from gxformat2.schema.native import (
    NativeStepType,          # Enum: data_input, data_collection_input, ...
    NativeInputConnection,   # Step input connection (id, output_name)
    NativePostJobAction,     # Post-job action definition
)
```

## Raw Dict Access

If you need to work with workflow dicts without typed models (e.g., for
forward-compatibility with fields not yet in the schema), load them
directly:

```python
from gxformat2.yaml import ordered_load, ordered_load_path

# From file
workflow_dict = ordered_load_path("workflow.ga")

# From stream
with open("workflow.gxwf.yml") as f:
    workflow_dict = ordered_load(f)

# Format detection
is_native = workflow_dict.get("a_galaxy_workflow") == "true"
is_format2 = workflow_dict.get("class") == "GalaxyWorkflow"
```

The schema models document what fields to expect — refer to
{py:mod}`gxformat2.schema.gxformat2` and {py:mod}`gxformat2.schema.native`
for field names, types, and aliases.

## Slicing into Workflow Components

Sometimes you don't need the full workflow model — you just want the
inputs, the outputs, or the steps. The {py:mod}`gxformat2.normalize`
module provides focused accessors that extract individual pieces from
any workflow representation, handling format detection, conversion, and
normalization behind the scenes.

```python
from gxformat2.normalize import inputs, outputs, steps

# From a file path, a raw dict, or any typed model
workflow_inputs = inputs("workflow.ga")
workflow_outputs = outputs(format2_dict)
all_steps = steps(normalized_native_workflow)
```

{py:func}`~gxformat2.normalize.inputs` returns a list of
{py:class}`~gxformat2.schema.gxformat2.WorkflowInputParameter` models,
{py:func}`~gxformat2.normalize.outputs` returns
{py:class}`~gxformat2.schema.gxformat2.WorkflowOutputParameter` models,
and {py:func}`~gxformat2.normalize.steps` returns input parameters
followed by {py:class}`~gxformat2.normalized.NormalizedWorkflowStep`
models — the same objects you'd get from the full
{py:class}`~gxformat2.normalized.NormalizedFormat2` model, just without
needing to build one yourself.

All three accept the same arguments:

```python
from gxformat2.options import ConversionOptions

# With conversion options and expansion
opts = ConversionOptions(workflow_directory="/path/to/dir")
expanded_inputs = inputs(workflow_dict=wf, options=opts, expand=True)
```

### Dict-returning variants (deprecated)

The older {py:func}`~gxformat2.normalize.inputs_normalized`,
{py:func}`~gxformat2.normalize.outputs_normalized`, and
{py:func}`~gxformat2.normalize.steps_normalized` functions return the
same data as plain dicts instead of typed models. These are retained for
backward compatibility with tools like Planemo:

```python
from gxformat2.normalize import inputs_normalized

# Returns list[dict] — each dict has "id", "type", "default", etc.
input_dicts = inputs_normalized(workflow_path="workflow.gxwf.yml")
```

New code should prefer the typed accessors above.
