"""Hand-written helper for resolving Format2 input ``type`` strings to the
corresponding pydantic model class.

The discriminator map mirrors ``pydantic:discriminator_map`` on
``Process.inputs`` in ``schema/v19_09/Process.yml``. Keep the two in sync.

Lives outside the generated modules in this package so ``build_schema.sh``
regeneration does not clobber it.
"""

from .gxformat2 import (
    BaseInputParameter,
    WorkflowBooleanParameter,
    WorkflowCollectionParameter,
    WorkflowDataParameter,
    WorkflowFloatParameter,
    WorkflowIntegerParameter,
    WorkflowTextParameter,
)

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
