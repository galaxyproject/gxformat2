from gxformat2.converter import yaml_to_workflow
from gxformat2.export import from_galaxy_native
from gxformat2.interface import ImporterGalaxyInterface


def test_import_export():
    as_dict_native = yaml_to_workflow("""
class: GalaxyWorkflow
steps:
  - tool_id: multiple_versions
    tool_version: "0.1"
    state:
      inttest: 0
""", MockGalaxyInterface(), None)
    assert as_dict_native["a_galaxy_workflow"] == "true"
    assert as_dict_native["format-version"] == "0.1"
    assert len(as_dict_native["steps"]) == 1

    as_dict_format2 = from_galaxy_native(as_dict_native, None)
    assert as_dict_format2["class"] == "GalaxyWorkflow"
    assert len(as_dict_format2["steps"]) == 1


class MockGalaxyInterface(ImporterGalaxyInterface):

    def import_workflow(self, workflow, **kwds):
        pass
