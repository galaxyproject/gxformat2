from gxformat2.converter import yaml_to_workflow
from gxformat2.interface import ImporterGalaxyInterface


TEST_GOOD_WORKFLOW = """
"""


def to_native(has_yaml, **kwds):
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
        assert value["type"] in ["data_input", "data_collection_input", "tool", "subworkflow"]


class MockGalaxyInterface(ImporterGalaxyInterface):

    def import_workflow(self, workflow, **kwds):
        pass
