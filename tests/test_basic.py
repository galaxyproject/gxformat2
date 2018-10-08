from gxformat2.converter import yaml_to_workflow
from gxformat2.export import from_galaxy_native
from gxformat2.interface import ImporterGalaxyInterface


def test_import_export():
    as_dict_native = to_native("""
class: GalaxyWorkflow
steps:
  - tool_id: multiple_versions
    tool_version: "0.1"
    state:
      inttest: 0
""")
    assert_valid_native(as_dict_native)
    assert len(as_dict_native["steps"]) == 1

    as_dict_format2 = from_galaxy_native(as_dict_native)
    assert_valid_format2(as_dict_format2)
    steps = as_dict_format2["steps"]
    # Step doesn't have a label - so it is serialized as a list.
    assert isinstance(steps, list)
    assert len(steps) == 1


def test_import_step_id_map():
    as_dict_native = to_native("""
class: GalaxyWorkflow
inputs:
  text_input1:
    type: collection
    collection_type: "list:paired"
steps:
  type_source:
    tool_id: collection_type_source
    in:
      input_collect: text_input1
""")
    assert_valid_native(as_dict_native)
    assert len(as_dict_native["steps"]) == 2
    native_steps = as_dict_native["steps"]
    input_step = native_steps["0"]
    assert input_step["type"] == "data_collection_input"
    assert input_step["label"] == "text_input1"
    tool_step = native_steps["1"]
    assert tool_step["label"] == "type_source"

    as_dict_format2 = from_native(as_dict_native)
    assert_valid_format2(as_dict_format2)
    steps = as_dict_format2["steps"]
    assert isinstance(steps, dict)


def test_docs_round_trip():
    as_dict = round_trip("""
class: GalaxyWorkflow
doc: |
  Simple workflow that no-op cats a file and then selects 10 random lines.
inputs:
  the_input:
    type: File
    doc: input doc
steps:
  cat:
    tool_id: cat1
    doc: cat doc
    in:
      input1: the_input
""")
    assert as_dict["doc"] == "Simple workflow that no-op cats a file and then selects 10 random lines.\n"
    assert as_dict["inputs"]["the_input"]["doc"] == "input doc"
    assert as_dict["steps"]["cat"]["doc"] == "cat doc"


def test_position_round_trip():
    as_dict = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input:
    type: data
    position:
      left: 30
      top: 70
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
    position:
      left: 130
      top: 370
""")
    assert as_dict["inputs"]["the_input"]["position"]["left"] == 30
    assert as_dict["inputs"]["the_input"]["position"]["top"] == 70
    assert as_dict["steps"]["cat"]["position"]["left"] == 130
    assert as_dict["steps"]["cat"]["position"]["top"] == 370


def test_dollar_graph_handling():
    as_dict_native = to_native("""
format-version: v2.0
$graph:
- id: main
  class: GalaxyWorkflow
  steps:
    - tool_id: multiple_versions
      tool_version: "0.1"
      state:
        inttest: 0
""")
    assert_valid_native(as_dict_native)


def round_trip(has_yaml):
    return from_native(to_native(has_yaml))


def from_native(native_as_dict):
    return from_galaxy_native(native_as_dict, None)


def to_native(has_yaml):
    return yaml_to_workflow(has_yaml, MockGalaxyInterface(), None)


def assert_valid_format2(as_dict_format2):
    assert as_dict_format2["class"] == "GalaxyWorkflow"
    assert "steps" in as_dict_format2


def assert_valid_native(as_dict_native):
    assert as_dict_native["a_galaxy_workflow"] == "true"
    assert as_dict_native["format-version"] == "0.1"
    assert "steps" in as_dict_native
    step_count = 0
    for key, value in as_dict_native["steps"].items():
        assert key == str(step_count)
        step_count += 1
        assert "type" in value
        assert value["type"] in ["data_input", "data_collection_input", "tool"]


class MockGalaxyInterface(ImporterGalaxyInterface):

    def import_workflow(self, workflow, **kwds):
        pass
