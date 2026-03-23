"""Galaxy workflow examples shipped with gxformat2 for testing and downstream use."""

import os
from enum import Enum
from typing import List, Optional

import yaml
from pydantic import BaseModel

from gxformat2.yaml import ordered_load

EXAMPLES_DIR = os.path.dirname(__file__)
FORMAT2_DIR = os.path.join(EXAMPLES_DIR, "format2")
NATIVE_DIR = os.path.join(EXAMPLES_DIR, "native")


class ExampleOrigin(str, Enum):
    """How the workflow was produced."""

    real = "real"
    real_hacked = "real-hacked"
    synthetic = "synthetic"
    converted = "converted"


class ExampleFormat(str, Enum):
    """Galaxy workflow serialization format."""

    format2 = "format2"
    native = "native"


class CatalogEntry(BaseModel):
    """Metadata for an example workflow in the catalog."""

    file: str
    origin: ExampleOrigin
    format: ExampleFormat
    tests: List[str]

    @property
    def name(self) -> str:
        """Filename without directory prefix."""
        return os.path.basename(self.file)

    @property
    def path(self) -> str:
        """Absolute path to the workflow file."""
        return os.path.join(EXAMPLES_DIR, self.file)

    def load(self) -> dict:
        """Load and parse the workflow file."""
        with open(self.path) as f:
            return ordered_load(f)

    def load_contents(self) -> str:
        """Return raw file contents."""
        with open(self.path) as f:
            return f.read()

    @property
    def workflow_label(self) -> Optional[str]:
        """Workflow label or name extracted from the file."""
        wf = self.load()
        return wf.get("label") or wf.get("name")

    @property
    def workflow_annotation(self) -> Optional[str]:
        """Workflow doc or annotation extracted from the file."""
        wf = self.load()
        doc = wf.get("doc") or wf.get("annotation") or ""
        if isinstance(doc, list):
            doc = "\n".join(doc)
        return doc.strip() or None


def load_catalog() -> List[CatalogEntry]:
    """Load and validate the example workflow catalog."""
    with open(os.path.join(EXAMPLES_DIR, "catalog.yml")) as f:
        raw = yaml.safe_load(f)
    return [CatalogEntry.model_validate(entry) for entry in raw]


def get_path(name: str) -> str:
    """Return absolute path to an example workflow file by name (with extension)."""
    for subdir in [FORMAT2_DIR, NATIVE_DIR]:
        path = os.path.join(subdir, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"Example workflow not found: {name}")


def load(name: str) -> dict:
    """Load and parse an example workflow by name."""
    with open(get_path(name)) as f:
        return ordered_load(f)


def load_contents(name: str) -> str:
    """Return raw file contents of an example workflow by name."""
    with open(get_path(name)) as f:
        return f.read()
