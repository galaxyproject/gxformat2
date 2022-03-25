import os

from gxformat2.converter import ImportOptions
from gxformat2.export import from_galaxy_native
from gxformat2.yaml import ordered_load
from ._helpers import (
    assert_valid_native,
    copy_without_workflow_output_labels,
    from_native,
    native_workflow_outputs,
    round_trip,
    TEST_PATH,
    to_native,
)
from .example_wfs import OPTIONAL_INPUT, WHEN_EXAMPLE


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


def test_import_default_file():
    as_dict_native = to_native("""
class: GalaxyWorkflow
inputs:
  default_file_input:
    default:
      class: File
      basename: a file
      format: txt
      location: test.txt
steps:
  cat1:
    tool_id: cat1
    in:
      input1: default_file_input
""")
    default_file_input_step = as_dict_native['steps']['0']
    assert default_file_input_step['in']['default'] == {
      'default': {
        'class': 'File',
        'basename': 'a file',
        'format': 'txt',
        'location': 'test.txt',
      }
    }


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


def test_reports_round_trip():
    as_dict = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input:
    type: File
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
report:
  markdown: |
    My cool Markdown!
""")
    assert as_dict["report"]["markdown"] == "My cool Markdown!\n"


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


def test_subworkflow_round_trip():
    as_dict = round_trip("""
class: GalaxyWorkflow
inputs:
  outer_input: data
steps:
  first_cat:
    tool_id: cat1
    in:
      input1: outer_input
  nested_workflow:
    run:
      class: GalaxyWorkflow
      inputs:
        inner_input: data
      steps:
        - tool_id: random_lines1
          state:
            num_lines: 1
            input:
              $link: inner_input
            seed_source:
              seed_source_selector: set_seed
              seed: asdf
    in:
      inner_input: first_cat/out_file1
""")
    assert as_dict["steps"]["nested_workflow"]["run"]["class"] == "GalaxyWorkflow"


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

    graph_with_subworkflow = """
format-version: v2.0
$graph:
- id: subworkflow1
  class: GalaxyWorkflow
  inputs:
    inner_input: data
  steps:
    - tool_id: random_lines1
      state:
        num_lines: 1
        input:
          $link: inner_input
        seed_source:
          seed_source_selector: set_seed
          seed: asdf

- id: main
  class: GalaxyWorkflow
  inputs:
    outer_input: data
  steps:
    first_cat:
      tool_id: cat1
      in:
        input1: outer_input
    nested_workflow:
      run: '#subworkflow1'
      in:
        inner_input: first_cat/out_file1
"""
    as_dict_native = to_native(graph_with_subworkflow)
    assert_valid_native(as_dict_native)
    assert "subworkflows" not in as_dict_native

    as_format_2 = from_native(as_dict_native)
    # no duplicated workflows so we don't expect $graph representation yet...
    assert as_format_2["class"] == "GalaxyWorkflow"
    assert as_format_2["steps"]["nested_workflow"]["run"]["class"] == "GalaxyWorkflow"

    import_options = ImportOptions()
    import_options.deduplicate_subworkflows = True
    as_dict_native = to_native(graph_with_subworkflow, import_options=import_options)
    assert_valid_native(as_dict_native)

    assert "subworkflows" in as_dict_native
    assert len(as_dict_native["subworkflows"]) == 1


def test_step_connections():
    wf_with_step_connections = round_trip("""
class: GalaxyWorkflow
inputs:
  test_input: data
steps:
  first_cat:
    tool_id: cat1
    in:
      input1: test_input
  the_pause:
    type: pause
    in:
      input: first_cat/out_file1
  second_cat:
    tool_id: cat1
    in:
      input1: the_pause
  third_cat:
    tool_id: random_lines1
    in:
      $step: second_cat
    state:
      num_lines: 1
      input:
        $link: test_input
      seed_source:
        seed_source_selector: set_seed
        seed: asdf
""")
    assert wf_with_step_connections["steps"]["third_cat"]["in"]["$step"]["source"] == "second_cat"


def test_round_trip_whens():
    wf_with_when = round_trip(WHEN_EXAMPLE)
    assert len(wf_with_when["steps"]) == 1
    print(wf_with_when)
    assert wf_with_when["steps"]["random_lines"]["when"] == "$(inputs.seed != 'skip')"


def test_export_native_no_labels():
    # Ensure outputs don't get mapped to 'null' key and ensure
    native_unicycler = ordered_load(open(os.path.join(TEST_PATH, "unicycler.ga")).read())
    before_output_count = 0
    for _ in native_workflow_outputs(native_unicycler):
        before_output_count += 1
    before_step_count = len(native_unicycler["steps"])

    unicycler_no_output_labels = copy_without_workflow_output_labels(native_unicycler)
    as_format2 = from_native(unicycler_no_output_labels)
    assert len(as_format2["outputs"]) == before_output_count
    round_trip_unicycler = to_native(as_format2)

    after_output_count = 0
    for _ in native_workflow_outputs(round_trip_unicycler):
        after_output_count += 1
    after_step_count = len(round_trip_unicycler["steps"])

    assert after_step_count == before_step_count
    assert after_output_count == before_output_count, round_trip_unicycler


def test_optional_inputs():
    as_dict = round_trip(OPTIONAL_INPUT)
    print(as_dict["inputs"])
    assert as_dict["inputs"]["the_input"]["optional"]


def test_input_formats_single():
    as_dict = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input:
    type: File
    optional: true
    format: txt
steps:
  cat:
    tool_id: cat_optional
    in:
      input1: the_input
""")
    assert as_dict["inputs"]["the_input"]["format"] == "txt"


def test_input_formats_multi():
    as_dict = round_trip("""
class: GalaxyWorkflow
inputs:
  the_input:
    type: File
    optional: true
    format:
      - txt
      - fasta
steps:
  cat:
    tool_id: cat_optional
    in:
      input1: the_input
""")
    assert as_dict["inputs"]["the_input"]["format"][0] == "txt"
    assert as_dict["inputs"]["the_input"]["format"][1] == "fasta"


def test_input_default():
    as_dict = round_trip("""
class: GalaxyWorkflow
inputs:
  data_input: data
  int_input:
    type: integer
    default: 3
steps:
  random:
    tool_id: random_lines1
    in:
      input: data_input
      num_lines: int_input
    state:
      seed_source:
        seed_source_selector: set_seed
        seed: asdf
""")
    assert as_dict["inputs"]["int_input"]["default"] == 3


def test_simple_restrictions():
    as_dict = round_trip("""
class: GalaxyWorkflow
inputs:
  data_input: data
  text_input:
    type: text
    restrictions:
      - abc
      - def
      - ghi
steps:
  random:
    tool_id: random_lines1
    in:
      input: data_input
      'seed_source|seed': text_input
    state:
      num_lines: 1
      seed_source:
        seed_source_selector: set_seed
""")
    assert as_dict["inputs"]["text_input"]["restrictions"] == ['abc', 'def', 'ghi']


def assert_valid_format2(as_dict_format2):
    assert as_dict_format2["class"] == "GalaxyWorkflow"
    assert "steps" in as_dict_format2
