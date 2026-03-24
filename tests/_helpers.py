import copy
import glob
import os

from gxformat2.converter import python_to_workflow, yaml_to_workflow
from gxformat2.examples import get_path as example_path  # noqa: F401 (re-exported)
from gxformat2.export import from_galaxy_native
from gxformat2.schema.native import NativeStepType

TEST_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_INTEROP_EXAMPLES = os.environ.get("GXFORMAT2_INTEROP_EXAMPLES", os.path.join(TEST_PATH, "examples"))

IWC_DIR = os.environ.get("GXFORMAT2_TEST_IWC_DIRECTORY")

# TODO: remove after https://github.com/galaxyproject/iwc/pull/1167 is merged
IWC_SKIP = {
    "hic-fastq-to-cool-hicup-cooler.ga",
    "chic-fastq-to-cool-hicup-cooler.ga",
}


def find_iwc_ga_files(skip=None):
    """Find .ga workflow files in the IWC checkout, optionally skipping some by basename."""
    if not IWC_DIR:
        return []
    skip = skip or IWC_SKIP
    return sorted(
        p
        for p in glob.glob(os.path.join(IWC_DIR, "workflows", "**", "*.ga"), recursive=True)
        if os.path.basename(p) not in skip
    )


def iwc_fixture_ids(paths):
    """Generate pytest fixture IDs relative to IWC_DIR."""
    return [os.path.relpath(p, IWC_DIR) if IWC_DIR else p for p in paths]


def to_native(has_yaml, **kwds):
    if isinstance(has_yaml, dict):
        return python_to_workflow(has_yaml, **kwds)
    else:
        return yaml_to_workflow(has_yaml, **kwds)


def assert_valid_native(as_dict_native):
    assert as_dict_native["a_galaxy_workflow"] == "true"
    assert as_dict_native["format-version"] == "0.1"
    assert "steps" in as_dict_native
    step_count = 0
    for key, value in as_dict_native["steps"].items():
        assert key == str(step_count)
        step_count += 1
        assert "type" in value
        assert value["type"] in NativeStepType.__members__


def copy_without_workflow_output_labels(native_as_dict):
    native_without_labels = copy.deepcopy(native_as_dict)
    for workflow_output in native_workflow_outputs(native_without_labels):
        workflow_output["label"] = None
    return native_without_labels


def native_workflow_outputs(native_as_dict):
    steps = native_as_dict.get("steps")
    for step in steps.values():
        yield from step.get("workflow_outputs", [])


def round_trip(has_yaml):
    as_native = to_native(has_yaml)
    assert_valid_native(as_native)
    return from_native(as_native)


def from_native(native_as_dict):
    return from_galaxy_native(native_as_dict, None)


def to_example_path(input_path: str, examples_dir: str, extension: str):
    if not os.path.isabs(examples_dir):
        examples_dir = os.path.join(TEST_INTEROP_EXAMPLES, examples_dir)
    if not os.path.exists(examples_dir):
        os.makedirs(examples_dir)
    rel_path = os.path.join(examples_dir, os.path.basename(input_path))
    root, ext = os.path.splitext(rel_path)
    # split again for something like .gxwf.yml
    if root.endswith(".gxwf"):
        root, ext = os.path.splitext(root)
    return root + "." + extension
