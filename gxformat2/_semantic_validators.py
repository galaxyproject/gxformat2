"""Cross-field semantic checks for Format2 input parameters.

The schema-salad-plus-pydantic codegen produces structural pydantic models
but cannot express cross-field rules (e.g. "column_definitions only on
sample_sheet collection inputs"). These checks are run after structural
validation and raise ``ValueError`` on violation - callers wrap them in
``pydantic.ValidationError`` where useful.

Mirrors the constraints enforced by Galaxy's runtime
``galaxy.model.dataset_collections.types.sample_sheet_util.SampleSheetColumnDefinitionModel``.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Mapping

_COLUMN_NAME_RE = re.compile(r"^[\w\-_ \?]*$")
_RECORD_RANK_RE = re.compile(r"(?:^|:)record(?::|$)")

_TEXT_TYPE_VALUES = {"text", "string"}
_COLLECTION_TYPE_VALUES = {"collection", "data_collection", "data_collection_input"}


def _as_dict(model_or_dict: Any) -> Mapping[str, Any]:
    if hasattr(model_or_dict, "model_dump"):
        return model_or_dict.model_dump(by_alias=True)
    return model_or_dict


def _column_default_matches_type(column_type: Any, default_value: Any) -> bool:
    if default_value is None:
        return True
    if column_type == "string" or column_type == "element_identifier":
        return isinstance(default_value, str)
    if column_type == "int":
        return isinstance(default_value, int) and not isinstance(default_value, bool)
    if column_type == "float":
        return isinstance(default_value, (int, float)) and not isinstance(default_value, bool)
    if column_type == "boolean":
        return isinstance(default_value, bool)
    return True


def _column_value_matches_type(column_type: Any, value: Any) -> bool:
    return _column_default_matches_type(column_type, value)


def validate_column_definition(column: Any) -> None:
    """Validate a SampleSheetColumnDefinition instance or dict."""
    column_dict = _as_dict(column)
    name = column_dict.get("name")
    if isinstance(name, str) and not _COLUMN_NAME_RE.match(name):
        raise ValueError(f"Sample sheet column name {name!r} contains disallowed characters")

    column_type = column_dict.get("type")
    default_value = column_dict.get("default_value")
    if not _column_default_matches_type(column_type, default_value):
        raise ValueError(
            f"Sample sheet column {name!r} default_value {default_value!r} does not match column type {column_type!r}"
        )

    for field in ("restrictions", "suggestions"):
        values = column_dict.get(field)
        if not values:
            continue
        for v in values:
            if not _column_value_matches_type(column_type, v):
                raise ValueError(
                    f"Sample sheet column {name!r} {field} entry {v!r} does not match column type {column_type!r}"
                )


def validate_input_parameter(input_param: Any) -> None:
    """Validate cross-field rules on a workflow input parameter.

    Enforces:
    - column_definitions only on collection inputs whose collection_type
      starts with 'sample_sheet'.
    - restrictions/suggestions/restrictOnConnections only on text/string
      inputs (or catch-all WorkflowInputParameter in text mode).
    - Each SampleSheetColumnDefinition is internally consistent.
    """
    data = _as_dict(input_param)
    type_value = data.get("type")
    type_values: Iterable[str]
    if isinstance(type_value, list):
        type_values = [str(t) for t in type_value]
    elif type_value is None:
        type_values = []
    else:
        type_values = [str(type_value)]
    is_text_only = bool(type_values) and all(t in _TEXT_TYPE_VALUES for t in type_values)
    is_collection_only = bool(type_values) and all(t in _COLLECTION_TYPE_VALUES for t in type_values)

    column_definitions = data.get("column_definitions")
    if column_definitions:
        if not is_collection_only and type_values:
            raise ValueError(f"column_definitions is only valid on collection inputs, got type={type_value!r}")
        collection_type = data.get("collection_type") or ""
        if not collection_type.startswith("sample_sheet"):
            raise ValueError(
                f"column_definitions requires collection_type starting with 'sample_sheet', got {collection_type!r}"
            )
        for column in column_definitions:
            validate_column_definition(column)

    fields = data.get("fields")
    if fields:
        if not is_collection_only and type_values:
            raise ValueError(f"fields is only valid on collection inputs, got type={type_value!r}")
        collection_type = data.get("collection_type") or ""
        if not _RECORD_RANK_RE.search(collection_type):
            raise ValueError(f"fields requires collection_type containing 'record', got {collection_type!r}")

    text_only_fields = ("restrictions", "suggestions", "restrictOnConnections")
    for field in text_only_fields:
        if data.get(field) in (None, [], False):
            # restrictOnConnections=False is the schema default and harmless;
            # only flag when the field is set on a non-text input.
            continue
        if data.get(field) is None:
            continue
        if type_values and not is_text_only:
            raise ValueError(f"{field} is only valid on text/string inputs, got type={type_value!r}")


def validate_workflow(workflow: Any) -> None:
    """Walk a (lax or strict) GalaxyWorkflow model and validate cross-field rules.

    Handles both list and dict input forms.
    """
    data = _as_dict(workflow)
    inputs = data.get("inputs") or []
    iter_inputs: Iterable[Any]
    if isinstance(inputs, dict):
        iter_inputs = inputs.values()
    else:
        iter_inputs = inputs
    for inp in iter_inputs:
        if isinstance(inp, str):
            continue
        validate_input_parameter(inp)

    # Recurse into subworkflows (run blocks under steps).
    steps = data.get("steps") or []
    iter_steps: Iterable[Any]
    if isinstance(steps, dict):
        iter_steps = steps.values()
    else:
        iter_steps = steps
    for step in iter_steps:
        if not isinstance(step, Mapping):
            continue
        run = step.get("run")
        if isinstance(run, Mapping) and run.get("class") == "GalaxyWorkflow":
            validate_workflow(run)
