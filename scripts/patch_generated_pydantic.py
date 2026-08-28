"""Post-codegen patches for schema-salad-plus-pydantic output.

Two patches are applied:

1. Fix invalid ``Field(default="X", "Y", ...)`` emitted for multi-symbol
   ``Literal`` defaults. The generator passes every symbol as a positional
   argument; we keep only the first.
2. Append the legacy ``_INPUT_TYPE_TO_CLASS`` map and ``input_parameter_class``
   helper to the Format2 modules. Older generator versions emitted these and
   ``gxformat2.normalized._format2`` still imports them.
"""

import re
import sys
from pathlib import Path

_FIELD_DEFAULT_FIXUP = re.compile(r'Field\(default=("[^"]+")((?:,\s*"[^"]+")+)(,\s*\w+=)')
_INPUT_DISPATCHER = '''

_INPUT_TYPE_TO_CLASS: dict[str, type[BaseInputParameter]] = {
    "data": WorkflowDataParameter,
    "File": WorkflowDataParameter,
    "data_input": WorkflowDataParameter,
    "collection": WorkflowCollectionParameter,
    "data_collection": WorkflowCollectionParameter,
    "data_collection_input": WorkflowCollectionParameter,
    "integer": WorkflowIntegerParameter,
    "int": WorkflowIntegerParameter,
    "text": WorkflowTextParameter,
    "string": WorkflowTextParameter,
    "float": WorkflowFloatParameter,
    "boolean": WorkflowBooleanParameter,
    "color": WorkflowTextParameter,
}


def input_parameter_class(type_value: str | None) -> type[BaseInputParameter]:
    """Return the specific input parameter class for a Format2 type string.

    Falls back to WorkflowDataParameter for unknown or None types.
    """
    if type_value is None:
        return WorkflowDataParameter
    return _INPUT_TYPE_TO_CLASS.get(type_value, WorkflowDataParameter)
'''


def patch_default_args(text: str) -> str:
    return _FIELD_DEFAULT_FIXUP.sub(r"Field(default=\1\3", text)


def append_dispatcher(text: str) -> str:
    if "_INPUT_TYPE_TO_CLASS" in text:
        return text
    return text.rstrip() + "\n" + _INPUT_DISPATCHER


def main(paths: list[str]) -> None:
    for raw in paths:
        path = Path(raw)
        text = path.read_text()
        new_text = patch_default_args(text)
        if path.name in {"gxformat2.py", "gxformat2_strict.py", "gxformat2_draft.py", "gxformat2_draft_strict.py"}:
            new_text = append_dispatcher(new_text)
        if new_text != text:
            path.write_text(new_text)
            print(f"patched {path}")


if __name__ == "__main__":
    main(sys.argv[1:])
