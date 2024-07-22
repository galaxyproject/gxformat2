import copy
import os

from gxformat2.converter import python_to_workflow, yaml_to_workflow
from gxformat2.export import from_galaxy_native
from gxformat2.interface import ImporterGalaxyInterface
from gxformat2.model import STEP_TYPES

TEST_PATH = os.path.abspath(os.path.dirname(__file__))
TEST_INTEROP_EXAMPLES = os.environ.get("GXFORMAT2_INTEROP_EXAMPLES", os.path.join(TEST_PATH, "examples"))


def to_native(has_yaml, **kwds):
    if isinstance(has_yaml, dict):
        return python_to_workflow(has_yaml, MockGalaxyInterface(), None, **kwds)
    else:
        return yaml_to_workflow(has_yaml, MockGalaxyInterface(), None, **kwds)


def assert_valid_native(as_dict_native):
    assert as_dict_native["a_galaxy_workflow"] == "true"
    assert as_dict_native["format-version"] == "0.1"
    assert "steps" in as_dict_native
    step_count = 0
    for key, value in as_dict_native["steps"].items():
        assert key == str(step_count)
        step_count += 1
        assert "type" in value
        assert value["type"] in STEP_TYPES


class MockGalaxyInterface(ImporterGalaxyInterface):

    def import_workflow(self, workflow, **kwds):
        pass


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
