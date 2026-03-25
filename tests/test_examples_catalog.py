"""Validate that catalog.yml stays in sync with actual example files."""

import glob
import os

from gxformat2.examples import EXAMPLES_DIR, FORMAT2_DIR, load_catalog, NATIVE_DIR


def _all_example_files():
    """Return set of relative paths for all .ga and .yml workflow files."""
    files = set()
    for pattern, subdir in [("*.gxwf.yml", FORMAT2_DIR), ("*.ga", NATIVE_DIR)]:
        for path in glob.glob(os.path.join(subdir, pattern)):
            files.add(os.path.relpath(path, EXAMPLES_DIR))
    return files


def test_catalog_validates_as_pydantic():
    """load_catalog() parses every entry through the CatalogEntry pydantic model."""
    catalog = load_catalog()
    assert len(catalog) > 0


def test_catalog_entries_point_to_existing_files():
    for entry in load_catalog():
        assert os.path.exists(entry.path), f"Catalog entry {entry.file} points to missing file"


def test_all_example_files_in_catalog():
    cataloged = {entry.file for entry in load_catalog()}
    uncataloged = _all_example_files() - cataloged
    assert not uncataloged, f"Example files not in catalog.yml: {uncataloged}"


def test_no_orphan_catalog_entries():
    cataloged = {entry.file for entry in load_catalog()}
    orphaned = cataloged - _all_example_files()
    assert not orphaned, f"Catalog entries with no file on disk: {orphaned}"


def test_catalog_test_files_exist():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    for entry in load_catalog():
        for test_file in entry.tests:
            path = os.path.join(project_root, test_file)
            assert os.path.exists(path), f"Catalog entry {entry.file} references missing test file {test_file}"
