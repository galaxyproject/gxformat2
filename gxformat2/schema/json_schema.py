"""JSON Schema export for gxformat2 workflow models.

Provides export functions that generate standard Draft 2020-12 JSON Schema
from gxformat2's Pydantic models. Exported schemas are intended for consumption
by external validators (Python jsonschema, TypeScript ajv, VSCode YAML extension).
"""

import json
from typing import (
    Any,
    Dict,
    Type,
)

from pydantic import BaseModel
from pydantic.json_schema import GenerateJsonSchema
from typing_extensions import Literal

MODE = Literal["validation", "serialization"]


class GxFormat2GenerateJsonSchema(GenerateJsonSchema):
    """Custom JSON Schema generator that injects $schema dialect."""

    def generate(self, schema, mode: MODE = "validation"):
        """Generate JSON Schema with $schema dialect injected."""
        json_schema = super().generate(schema, mode=mode)
        json_schema["$schema"] = self.schema_dialect
        return json_schema


def workflow_json_schema(*, strict: bool = False, mode: MODE = "validation") -> Dict[str, Any]:
    """Export GalaxyWorkflow JSON Schema.

    Args:
        strict: If True, use strict model (extra="forbid" — rejects unknown keys).
        mode: Pydantic schema mode ("validation" or "serialization").
    """
    model_class: Type[BaseModel]
    if strict:
        from .gxformat2_strict import GalaxyWorkflow as model_class
    else:
        from .gxformat2 import GalaxyWorkflow as model_class

    return model_class.model_json_schema(
        schema_generator=GxFormat2GenerateJsonSchema,
        mode=mode,
    )


def workflow_json_schema_string(*, strict: bool = False, mode: MODE = "validation") -> str:
    """Export GalaxyWorkflow JSON Schema as formatted string."""
    return json.dumps(workflow_json_schema(strict=strict, mode=mode), indent=4)
