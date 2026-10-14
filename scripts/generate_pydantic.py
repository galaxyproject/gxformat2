"""Generate pydantic models with optional document-root selection."""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any, cast
from urllib.parse import urlparse

from schema_salad.ref_resolver import Loader, file_uri
from schema_salad.schema import get_metaschema, shortname
from schema_salad_plus_pydantic.orchestrate import generate


def _load_schema(schema_path: str) -> tuple[list[dict[str, Any]], Loader]:
    schema_uri = schema_path
    if not (urlparse(schema_uri)[0] and urlparse(schema_uri)[0] in ["http", "https", "file"]):
        schema_uri = file_uri(os.path.abspath(schema_uri))

    _, _, metaschema_loader = get_metaschema()
    schema_raw_doc = metaschema_loader.fetch(schema_uri)
    schema_doc, schema_metadata = metaschema_loader.resolve_all(schema_raw_doc, schema_uri)
    schema_ctx = schema_metadata.get("@context", {})
    salad_version = schema_metadata.get("saladVersion", "v1.1")
    return cast(list[dict[str, Any]], schema_doc), Loader(schema_ctx, salad_version=salad_version)


def _select_document_roots(schema_doc: list[dict[str, Any]], roots: set[str]) -> None:
    for item in schema_doc:
        if item.get("type") != "record":
            continue
        if shortname(item["name"]) in roots:
            item["documentRoot"] = True
        else:
            item.pop("documentRoot", None)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("schema")
    parser.add_argument("-o", "--output", required=True)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument(
        "--document-root",
        action="append",
        default=[],
        help="Record shortname to treat as a document root for this generated module.",
    )
    args = parser.parse_args()

    schema_doc, loader = _load_schema(args.schema)
    if args.document_root:
        _select_document_roots(schema_doc, set(args.document_root))

    output = Path(args.output)
    with output.open("w") as out:
        generate(schema_doc, loader, out, strict=args.strict)


if __name__ == "__main__":
    main()
