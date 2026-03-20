Augment the Galaxy Format2 workflow schema definition in `schema/v19_09/workflow.yml` based on the user's request below.

## Background

The schema salad file `schema/v19_09/workflow.yml` defines the Galaxy Workflow Format 2 schema. It gets compiled by `build_schema.sh` into:
- Generated Python code (`gxformat2/schema/v19_09.py`) via `schema-salad-tool --codegen python`
- Published HTML docs (deployed to GitHub Pages at `https://galaxyproject.github.io/gxformat2/v19_09.html`) via `schema-salad-doc`

The schema uses **Schema Salad v1.1** syntax. Related schema files:
- `schema/common/common.yml` — shared abstract record types (`HasUUID`, `HasStepErrors`, `HasStepPosition`, `ReferencesTool`, `StepPosition`, `ToolShedRepository`)
- `schema/v19_09/Process.yml` — trimmed CWL Process subset
- `schema/common/metaschema/` — metaschema definitions

## Current Schema Structure (workflow.yml)

The file defines these types in its `$graph` array:
- **WorkflowDoc** (documentation) — top-level doc block
- **GalaxyType** (enum) — `integer`, `text`, `File`, `data`, `collection`
- **WorkflowStepType** (enum) — currently `tool`, `subworkflow`, `pause`
- **WorkflowInputParameter** (record) — extends `cwl:InputParameter` + `HasStepPosition`
- **WorkflowOutputParameter** (record) — extends `cwl:OutputParameter`
- **WorkflowStep** (record) — extends `Identified`, `Labeled`, `Documented`, `HasStepPosition`, `ReferencesTool`, `HasStepErrors`, `HasUUID`
- **Sink** (abstract record) — defines `source` field
- **WorkflowStepInput** (record) — extends `Identified`, `Sink`, `Labeled`
- **Report** (record) — has `markdown` field
- **WorkflowStepOutput** (record) — extends `Identified`, has PJA fields (`rename`, `hide`, `delete_intermediate_datasets`, `change_datatype`, `set_columns`, `add_tags`, `remove_tags`)
- **GalaxyWorkflow** (record, documentRoot) — extends `cwl:Process` + `HasUUID`, has `class`, `steps`, `report`, `tags`, `creator`, `license`, `release`

## Schema Salad Syntax Quick Reference

Enum example:
```yaml
- name: MyEnum
  type: enum
  symbols:
    - value1
    - value2
  doc:
    - "Description of the enum."
    - "value1: description"
    - "value2: description"
```

Record example:
```yaml
- name: MyRecord
  type: record
  doc: |
    Description of this record.
  fields:
    - name: field_name
      type: string?    # ? means optional
      doc: |
        Field description.
```

Abstract record (mixin) example:
```yaml
- name: MyMixin
  type: record
  abstract: true
  fields:
    - name: some_field
      type: string?
```

Array type: `type: array` with `items: SomeType`
Optional: append `?` or use `- "null"` in type union
Any type: `Any?` for unstructured data
Extends: `extends: [TypeA, TypeB]` or `extends: TypeA`

## Known Gaps (Features Implemented in Code but Missing from Schema)

### 1. `pick_value` step type (commit 6f61e055)
The `WorkflowStepType` enum needs `pick_value` added. In Galaxy, pick_value modules select one non-null value from multiple inputs. The converter (`gxformat2/converter.py`) handles `transform_pick_value()` which sets up input connections, default inputs, tool state with a name field, and computes num_inputs from connection count.

### 2. Post Job Actions on pick_value (commit 76432f5c)
PJA support for pick_value was added in the converter/exporter. The schema already defines PJA-related fields on `WorkflowStepOutput` (`rename`, `hide`, etc.), so this may not require schema changes — the PJA fields already exist. But verify if any new fields are needed.

### 3. Workflow comments (commit 36e70956)
Four comment types exist in Galaxy: `text`, `markdown`, `frame`, `freehand`. In Format2 representation (as defined in `gxformat2/model.py`):

**Common fields** (all comment types): `type`, `position`, `size`, `color`, `label` (optional)

**Type-specific fields** (flattened from native `data` dict):
- **text**: `text` (string), `bold` (bool), `italic` (bool), `text_size` (number)
- **markdown**: `text` (string)
- **frame**: `title` (string), `contains_steps` (array of step labels/indices), `contains_comments` (array of comment labels/indices)
- **freehand**: `thickness` (number), `line` (array of coordinate pairs)

Position is `[x, y]` (array of 2 numbers). Size is `[width, height]` (array of 2 numbers).

The `GalaxyWorkflow` record needs a `comments` field that accepts an array of comment records.

## Instructions

1. Read the current `schema/v19_09/workflow.yml` and `schema/common/common.yml` before making changes.
2. Apply the requested schema changes following Schema Salad v1.1 conventions.
3. Match the style and formatting of the existing schema definitions.
4. Add clear `doc` fields for all new types and fields.
5. After editing, verify the schema builds by running: `cd schema/v19_09 && schema-salad-tool --print-avro workflow.yml`
6. If the build fails, diagnose and fix the issue.

## User's Request

$ARGUMENTS
