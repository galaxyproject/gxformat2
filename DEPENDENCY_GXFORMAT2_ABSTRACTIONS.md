# gxformat2 Abstractions

Abstractions available to downstream consumers (Galaxy, Planemo, etc.) for working with workflows and workflow components.

## Pydantic Models

### Format 2 Workflow (`gxformat2.schema.gxformat2`)

Auto-generated from `schema/v19_09/workflow.yml` via `schema-salad-plus-pydantic`.

| Model | Purpose |
|---|---|
| `GalaxyWorkflow` | Root Format 2 workflow document — steps, inputs, outputs, metadata |
| `WorkflowStep` | Individual step — tool_id, state, in/out, run, when |
| `WorkflowInputParameter` | Workflow input — type, default, optional, format |
| `WorkflowOutputParameter` | Workflow output — outputSource |
| `WorkflowStepInput` | Step input mapping — source, default |
| `WorkflowStepOutput` | Step output with post-job actions — rename, hide, change_datatype, tags |
| `WorkflowComment` | Visual annotation — text, markdown, frame, freehand |
| `Report` | Invocation report template — markdown |
| `WorkflowStepType` | Enum: tool, subworkflow, pause, pick_value |
| `GalaxyType` | Enum: null, boolean, int, float, string, File, data, collection, etc. |

### Native Workflow (`gxformat2.schema.native`)

Auto-generated from `schema/native_v0_1/workflow.yml` via `schema-salad-plus-pydantic`.

| Model | Purpose |
|---|---|
| `NativeGalaxyWorkflow` | Native .ga document — steps dict keyed by string ints, format-version |
| `NativeStep` | Native step — tool_state (str or dict), input_connections, post_job_actions |
| `NativeInputConnection` | Connection wiring — source step id + output_name |
| `NativePostJobAction` | Post-job action — action_type, output_name, action_arguments |
| `NativeWorkflowOutput` | Workflow-level output — label, output_name |
| `NativeStepInput` | Step input metadata — name, description |
| `NativeStepOutput` | Step output declaration — name, type |
| `NativeTextComment`, `NativeMarkdownComment`, `NativeFrameComment`, `NativeFreehandComment` | Comment types with discriminated union on `type` |
| `NativeCreatorPerson`, `NativeCreatorOrganization` | Creator metadata with discriminated union on `class` |
| `NativeSourceMetadata` | Provenance — url, trs_tool_id, trs_version_id |
| `NativeReport` | Report template — markdown |
| `StepPosition` | Canvas position — left, top |
| `ToolShedRepository` | Tool Shed coordinates — name, owner, changeset_revision, tool_shed |
| `NativeStepType` | Enum: data_input, data_collection_input, parameter_input, tool, subworkflow, pause, pick_value |

Strict variants (`gxformat2.schema.gxformat2_strict`, `gxformat2.schema.native_strict`) use `extra="forbid"` instead of `extra="allow"`.

### Schema-Salad Loaders (`gxformat2.schema.v19_09`, `gxformat2.schema.native_v0_1`)

Auto-generated from schema-salad definitions via `schema-salad-tool --codegen=python`. These are *not* pydantic models — they use schema-salad's own loading/validation machinery. Used by `lint_format2` for schema-salad validation.

Key functions in `gxformat2.schema.v19_09`:

```python
load_document(doc, baseuri=None, loadingOptions=None) -> Any
load_document_by_string(string, uri, loadingOptions=None) -> Any
load_document_by_yaml(yaml, uri, loadingOptions=None) -> Any
load_document_with_metadata(doc, baseuri=None, loadingOptions=None, addl_metadata_fields=None) -> Any
```

`gxformat2.schema.native_v0_1` has the same interface for native workflows.

## Loading

### `gxformat2.native`

```python
load_native(data: dict, *, strict: bool = True) -> NativeGalaxyWorkflow
```

Parse a native workflow dict into a typed pydantic model. `strict=False` normalizes known Galaxy serialization quirks before validation:
- `tags: ""` or `tags: "a,b"` → `tags: ["a", "b"]`
- Scalar `action_arguments` → `None`
- Recurses into embedded subworkflows

### `gxformat2.schema.native` / `gxformat2.schema.gxformat2`

```python
load_document(path: str | Path) -> NativeGalaxyWorkflow | list[NativeGalaxyWorkflow]
load_document(path: str | Path) -> GalaxyWorkflow | list[GalaxyWorkflow]
```

Load and validate from a **JSON** file path (uses `json.load` internally). Each schema module has its own `load_document`.

### `gxformat2.yaml`

```python
ordered_load(stream, Loader=yaml.SafeLoader, **kwds) -> OrderedDict  # YAML stream → ordered dict
ordered_load_path(path: str, **kwds) -> OrderedDict                  # File path → ordered dict
ordered_dump(data, stream=None, Dumper=yaml.SafeDumper, **kwds) -> str  # Dict → YAML string
ordered_dump_to_path(as_dict: dict, path: str)                       # Dict → YAML file
```

### `gxformat2._scripts`

```python
ensure_format2(workflow_dict: dict, ensure_labels: bool = False) -> dict  # Convert to Format2 if native
ensure_format2_from_path(path: str) -> dict                               # Load + ensure Format2
```

## Conversion

### Format 2 → Native (`gxformat2.converter`)

```python
python_to_workflow(as_python: dict, galaxy_interface, workflow_directory=None, import_options=None) -> dict
yaml_to_workflow(has_yaml, galaxy_interface, workflow_directory, import_options=None) -> dict
```

Core conversion from Format2 representation to native Galaxy .ga dict. Uses `ConversionContext` to track labels, step ids, and subworkflow relationships. Individual step types handled by `transform_*` functions:

| Function | Step type |
|---|---|
| `transform_data_input` | `data_input` |
| `transform_data_collection_input` | `data_collection_input` |
| `transform_parameter_input` | `parameter_input` |
| `transform_tool` | `tool` |
| `transform_subworkflow` | `subworkflow` |
| `transform_pause` | `pause` |
| `transform_pick_value` | `pick_value` |

### Native → Format 2 (`gxformat2.export`)

```python
from_galaxy_native(
    native_workflow_dict: dict | NativeGalaxyWorkflow,
    tool_interface=None,
    json_wrapper: bool = False,
    compact: bool = False,
    convert_tool_state: ConvertToolStateFn = None,
) -> dict
```

Converts native .ga to Format2 dict. Accepts raw dicts or pre-validated `NativeGalaxyWorkflow` models. Uses typed `NativeStep` access internally. `compact=True` strips position information.

### Abstract CWL Export (`gxformat2.abstract`)

```python
from_dict(workflow_dict: dict, subworkflow=False) -> dict
```

Convert a Format2 workflow dict to abstract CWL (Operation-class steps).

### Convert and Import (`gxformat2.main`)

```python
convert_and_import_workflow(has_workflow, **kwds) -> dict
```

High-level convenience: convert a Format2 workflow and import it into a Galaxy instance via bioblend. Accepts either a dict or a file path (when `source_type="path"`). Notable keyword arguments:
- `galaxy_interface` — an `ImporterGalaxyInterface`; defaults to `BioBlendImporterGalaxyInterface(**kwds)`
- `source_type` — `"path"` to load from a file path
- `workflow_directory` — base directory for resolving `@import` references
- `convert` — `True` (default) to run Format2→native conversion; `False` to import as-is
- `name` — override the workflow name
- `publish`, `exact_tools`, `fill_defaults` — forwarded to `import_workflow`

### Cytoscape Visualization (`gxformat2.cytoscape`)

```python
to_cytoscape(workflow_path: str, output_path=None) -> None
```

Build a Cytoscape visualization from a Galaxy workflow (Format2 or native). Output is HTML (using cytoscape.js) when `output_path` ends with `.html`, otherwise JSON elements for Cytoscape desktop. Also has a `main()` CLI entry point.

## Callback Protocols

### `ConvertToolStateFn` (export.py)

```python
ConvertToolStateFn = Optional[Callable[[dict], Optional[Dict[str, Any]]]]
```

Receives a native step dict, returns a Format2 `state` dict or `None` to fall back to raw `tool_state` passthrough. Used by `from_galaxy_native` for tool steps — allows Galaxy to inject tool-definition-aware value conversion.

### `NativeStateEncoderFn` (converter.py)

```python
NativeStateEncoderFn = Optional[Callable[[dict, Dict[str, Any]], Optional[Dict[str, Any]]]]
```

Receives `(step_dict, state_dict)`, returns encoded native `tool_state` or `None` for default encoding. Used by `python_to_workflow` via `ImportOptions.native_state_encoder` — allows Galaxy to encode Format2 state back to native double-encoded JSON.

### `ImportOptions` (converter.py)

```python
class ImportOptions:
    def __init__(self):
        self.deduplicate_subworkflows: bool = False
        self.encode_tool_state_json: bool = True
        self.native_state_encoder: NativeStateEncoderFn = None
```

Note: this is a plain class, not a dataclass.

## Normalization (`gxformat2.normalize`)

```python
class Inputs:
    """Workflow input abstraction."""
    def __init__(self, workflow_dict: dict)
    def is_an_input(self, target_label: str) -> bool
    count: int  # property

class NormalizedWorkflow:
    """Normalized view of a Format2 workflow."""
    def __init__(self, input_workflow: dict)
    input_workflow: dict
    normalized_workflow_dict: dict
```

`NormalizedWorkflow` normalizes anonymous output references and ensures implicit step `out` declarations (needed for abstract CWL export).

### Convenience functions

```python
steps_normalized(workflow_dict=None, workflow_path=None) -> list
inputs_normalized(**kwd) -> list
outputs_normalized(**kwd) -> list
walk_id_list_or_dict(dict_or_list) -> Iterator[tuple[str, dict]]
```

`walk_id_list_or_dict` yields `(key, item)` pairs from either dict (`{key: {...}}`) or list (`[{"id": key, ...}]`) representations — the two step/input formats Format2 supports.

## Linting (`gxformat2.lint`)

### `LintContext` (`gxformat2.linting`)

Collects errors and warnings during linting:
- `error(message, *args, **kwds)` / `warn(message, *args, **kwds)`
- `found_errors`, `found_warns` — booleans
- `print_messages()` — output results

### Lint functions

| Function | Target |
|---|---|
| `lint_ga(lint_context, workflow_dict, path=None)` | Native .ga structural validation |
| `lint_ga_path(lint_context, path)` | Convenience: load from path + `lint_ga` |
| `lint_format2(lint_context, workflow_dict, path=None)` | Format2 schema-salad + structural validation. Note: `path` must be non-None for schema-salad validation (converted to file URI internally, uses `gxformat2.schema.v19_09.load_document`) |
| `lint_pydantic_validation(lint_context, workflow_dict, format2=False)` | Strict then lax pydantic validation |
| `lint_best_practices_ga(lint_context, workflow_dict)` | Native best practices (annotation, creator, license, disconnected inputs, labels) |
| `lint_best_practices_format2(lint_context, workflow_dict)` | Format2 best practices |

## Markdown Parsing (`gxformat2.markdown_parse`)

```python
validate_galaxy_markdown(galaxy_markdown, internal=True) -> None  # raises ValueError if invalid
GALAXY_MARKDOWN_FUNCTION_CALL_LINE  # compiled regex for matching Galaxy directives
```

Parses and validates "Galaxy Flavored Markdown" (used in workflow reports). Self-contained module — no Galaxy dependencies. Used by `lint.py` to validate report markdown.

## Model Utilities (`gxformat2.model`)

### Source reference parsing

```python
resolve_source_reference(value: str, known_labels: set | dict) -> tuple[str, str]
```

Parse `step_label/output_name` references. Handles labels that contain `/` by matching against known labels.

### Type conversion

```python
get_native_step_type(gxformat2_step_dict: dict) -> NativeGalaxyStepType
native_input_to_format2_type(step: dict, tool_state: dict) -> str | list[str]
```

### Type aliases

```python
NativeGalaxyStepType = Literal["subworkflow", "data_input", "data_collection_input", "tool", "pause", "pick_value", "parameter_input"]
GxFormat2StepTypeAlias = Literal["input", "input_collection", "parameter"]
STEP_TYPE_ALIASES: dict[GxFormat2StepTypeAlias, NativeGalaxyStepType]  # maps aliases to native types
```

### Step/input helpers

```python
steps_as_list(format2_workflow, add_ids=False, inputs_offset=0, mutate=False) -> list
inputs_as_native_steps(workflow_dict) -> list
inputs_as_normalized_steps(workflow_dict) -> list
outputs_as_list(as_python) -> list
with_step_ids(steps, inputs_offset=0) -> list
append_step_id_to_step_list_elements(steps, inputs_offset=0) -> None  # mutates in-place
convert_dict_to_id_list_if_needed(dict_or_list, add_label=False, mutate=False) -> list
pop_connect_from_step_dict(step) -> ConnectDict
setup_connected_values(value, key="", append_to=None) -> Any
ensure_step_position(step, order_index) -> None  # mutates step dict
prune_position(step) -> dict  # returns only left/top from position
clean_connection(value) -> str  # converts legacy # connections to /
```

### Comment conversion

```python
flatten_comment_data(native_comment: dict) -> dict   # Native nested data → flat Format2
unflatten_comment_data(format2_comment: dict) -> dict # Flat Format2 → native nested data
```

## Labels (`gxformat2._labels`)

```python
UNLABELED_INPUT_PREFIX = "_unlabeled_input_"
UNLABELED_STEP_PREFIX = "_unlabeled_step_"

class Labels:
    def ensure_new_output_label(self, label: str) -> str
    @staticmethod
    def is_anonymous_output_label(label: str) -> bool
    @staticmethod
    def is_unlabeled_input(label) -> bool
    @staticmethod
    def is_unlabeled_step(label) -> bool
    @staticmethod
    def is_unlabeled(label) -> bool
```

Sentinel labels for steps/inputs that lack user-provided labels. Used during native/Format2 conversion to maintain referential integrity. Note: `is_anonymous_output_label`, `is_unlabeled_input`, `is_unlabeled_step`, and `is_unlabeled` are all `@staticmethod`.

## Galaxy Interface (`gxformat2.interface`)

```python
class ImporterGalaxyInterface(abc.ABCMeta):  # abstract
    def import_workflow(self, workflow, **kwds) -> dict  # abstract
    def import_tool(self, tool) -> dict                  # raises NotImplementedError

class BioBlendImporterGalaxyInterface:  # does NOT inherit ImporterGalaxyInterface
    def __init__(self, **kwds)  # wraps bioblend GalaxyInstance
    def import_workflow(self, workflow, **kwds)
    def import_tool(self, tool_representation)  # raises NotImplementedError
```

Note: `BioBlendImporterGalaxyInterface` is a standalone class that duck-types the same interface but does not formally inherit from `ImporterGalaxyInterface`.

## Public API (`gxformat2.__init__`)

Exported names: `convert_and_import_workflow`, `ConvertToolStateFn`, `from_galaxy_native`, `ImporterGalaxyInterface`, `ImportOptions`, `NativeStateEncoderFn`, `python_to_workflow`.

Also exports `__version__`, `PROJECT_NAME`, `PROJECT_OWNER`.
