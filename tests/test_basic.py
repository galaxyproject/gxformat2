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
from .example_wfs import (
    OPTIONAL_INPUT,
    PAIRED_LIST_COLLECTION_INPUT,
    SAMPLE_SHEET_COLLECTION_INPUT,
    SLASH_IN_INPUT_LABEL,
    SLASH_IN_LABEL_CHAINED,
    SLASH_IN_STEP_LABEL_EXPLICIT_OUTPUT,
    TRS_URL_SUBWORKFLOW,
    URL_SUBWORKFLOW,
    USER_DEFINED_TOOL_WORKFLOW,
    WHEN_EXAMPLE,
)


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
    default_file_input_step = as_dict_native["steps"]["0"]
    assert default_file_input_step["in"]["default"] == {
        "default": {
            "class": "File",
            "basename": "a file",
            "format": "txt",
            "location": "test.txt",
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


def test_paired_list_inputs():
    as_dict = round_trip(PAIRED_LIST_COLLECTION_INPUT)
    assert as_dict["inputs"]["input_list"]["collection_type"] == "list:paired"


def test_sample_sheet_inputs():
    as_dict = round_trip(SAMPLE_SHEET_COLLECTION_INPUT)
    assert as_dict["inputs"]["input_sample_sheet"]["collection_type"] == "sample_sheet"
    column_descriptions = as_dict["inputs"]["input_sample_sheet"]["column_definitions"]
    assert column_descriptions
    assert len(column_descriptions) == 1
    assert column_descriptions[0]["name"] == "condition"


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
    assert as_dict["inputs"]["text_input"]["restrictions"] == ["abc", "def", "ghi"]


def test_url_subworkflow_to_native():
    """Test that run: <url> produces a native step with content_id."""
    as_dict_native = to_native(URL_SUBWORKFLOW)
    assert_valid_native(as_dict_native)
    steps = as_dict_native["steps"]
    assert len(steps) == 3  # input + cat + subworkflow
    subworkflow_step = steps["2"]
    assert subworkflow_step["type"] == "subworkflow"
    assert subworkflow_step["content_id"] == "https://example.com/my_subworkflow.gxwf.yml"
    assert "subworkflow" not in subworkflow_step


def test_trs_url_subworkflow_to_native():
    """Test that run: <trs_url> produces a native step with content_id."""
    as_dict_native = to_native(TRS_URL_SUBWORKFLOW)
    assert_valid_native(as_dict_native)
    steps = as_dict_native["steps"]
    subworkflow_step = steps["2"]
    assert subworkflow_step["type"] == "subworkflow"
    assert "dockstore.org" in subworkflow_step["content_id"]
    assert "subworkflow" not in subworkflow_step


def test_native_url_subworkflow_to_format2():
    """Test that native steps with content_source/content_id export as run: <url>."""
    native_workflow = {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "Test URL Export",
        "steps": {
            "0": {
                "id": 0,
                "type": "data_input",
                "label": "outer_input",
                "tool_state": '{"name": "outer_input"}',
                "input_connections": {},
                "workflow_outputs": [],
            },
            "1": {
                "id": 1,
                "type": "subworkflow",
                "label": "nested_workflow",
                "content_source": "url",
                "content_id": "https://example.com/my_subworkflow.gxwf.yml",
                "tool_state": "{}",
                "input_connections": {
                    "inner_input": [{"id": 0, "output_name": "output"}],
                },
                "workflow_outputs": [],
            },
        },
    }
    as_format2 = from_native(native_workflow)
    assert as_format2["class"] == "GalaxyWorkflow"
    assert as_format2["steps"]["nested_workflow"]["run"] == "https://example.com/my_subworkflow.gxwf.yml"


def test_native_trs_url_subworkflow_to_format2():
    """Test that native steps with content_source=trs_url export as run: <url>."""
    trs_url = "https://dockstore.org/api/ga4gh/trs/v2/tools/%23workflow/versions/main/PLAIN-GALAXY/descriptor"
    native_workflow = {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "Test TRS URL Export",
        "steps": {
            "0": {
                "id": 0,
                "type": "data_input",
                "label": "outer_input",
                "tool_state": '{"name": "outer_input"}',
                "input_connections": {},
                "workflow_outputs": [],
            },
            "1": {
                "id": 1,
                "type": "subworkflow",
                "label": "nested_workflow",
                "content_source": "trs_url",
                "content_id": trs_url,
                "tool_state": "{}",
                "input_connections": {
                    "inner_input": [{"id": 0, "output_name": "output"}],
                },
                "workflow_outputs": [],
            },
        },
    }
    as_format2 = from_native(native_workflow)
    assert as_format2["steps"]["nested_workflow"]["run"] == trs_url


def test_slash_in_input_label():
    """Input label containing '/' should round-trip without error."""
    as_native = to_native(SLASH_IN_INPUT_LABEL)
    assert_valid_native(as_native)
    # Input step should be connected to the cat step
    cat_step = as_native["steps"]["1"]
    conn = cat_step["input_connections"]["input1"]
    assert conn[0]["id"] == 0


def test_slash_in_step_label_explicit_output():
    """Step label containing '/' with explicit output should round-trip."""
    as_native = to_native(SLASH_IN_STEP_LABEL_EXPLICIT_OUTPUT)
    assert_valid_native(as_native)
    steps = as_native["steps"]
    assert len(steps) == 2


def test_slash_in_label_chained():
    """Both input and step labels with '/' and chained connections."""
    as_native = to_native(SLASH_IN_LABEL_CHAINED)
    assert_valid_native(as_native)
    steps = as_native["steps"]
    assert len(steps) == 3
    # second_cat connects to Host/Contaminant Filter's out_file1
    second_cat = steps["2"]
    conn = second_cat["input_connections"]["input1"]
    assert conn[0]["id"] == 1
    assert conn[0]["output_name"] == "out_file1"


def test_slash_in_input_label_round_trip():
    """Full round-trip: input label with '/' survives native→format2."""
    as_dict = round_trip(SLASH_IN_INPUT_LABEL)
    assert "Host/Contaminant Genome" in str(as_dict["inputs"])


def test_slash_in_label_chained_round_trip():
    """Full round-trip: chained steps with '/' in labels."""
    as_dict = round_trip(SLASH_IN_LABEL_CHAINED)
    assert "Host/Contaminant Filter" in str(as_dict["steps"])
    assert "Host/Contaminant Genome" in str(as_dict["inputs"])


def test_unlabeled_tool_step_round_trip():
    """Unlabeled tool step referenced by another step survives round-trip."""
    native_workflow = {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "Unlabeled Tool Test",
        "steps": {
            "0": {
                "id": 0,
                "type": "data_input",
                "label": "input_data",
                "tool_state": '{"name": "input_data"}',
                "input_connections": {},
                "workflow_outputs": [],
            },
            "1": {
                "id": 1,
                "type": "tool",
                "label": None,
                "tool_id": "cat1",
                "tool_version": "1.0",
                "tool_state": "{}",
                "input_connections": {
                    "input1": [{"id": 0, "output_name": "output"}],
                },
                "workflow_outputs": [],
            },
            "2": {
                "id": 2,
                "type": "tool",
                "label": "final_cat",
                "tool_id": "cat1",
                "tool_version": "1.0",
                "tool_state": "{}",
                "input_connections": {
                    "input1": [{"id": 1, "output_name": "out_file1"}],
                },
                "workflow_outputs": [{"output_name": "out_file1", "label": "the_output"}],
            },
        },
    }
    as_format2 = from_native(native_workflow)
    # Re-import to native and verify the connection is preserved
    as_native_rt = to_native(as_format2)
    assert_valid_native(as_native_rt)
    # Should have 3 steps: input + 2 tools
    assert len(as_native_rt["steps"]) == 3
    # final_cat should connect to step 1 (the unlabeled tool), not step 0
    final_cat = as_native_rt["steps"]["2"]
    assert final_cat["tool_id"] == "cat1"
    assert final_cat["label"] == "final_cat"
    conn = final_cat["input_connections"]["input1"]
    assert conn[0]["id"] == 1
    assert conn[0]["output_name"] == "out_file1"
    # Step 1 should be a tool, not a parameter input
    step1 = as_native_rt["steps"]["1"]
    assert step1["type"] == "tool"
    assert step1["label"] is None


def test_unlabeled_pause_step_round_trip():
    """Unlabeled pause step referenced by another step survives round-trip."""
    native_workflow = {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "Unlabeled Pause Test",
        "steps": {
            "0": {
                "id": 0,
                "type": "data_input",
                "label": "input_data",
                "tool_state": '{"name": "input_data"}',
                "input_connections": {},
                "workflow_outputs": [],
            },
            "1": {
                "id": 1,
                "type": "pause",
                "label": None,
                "tool_state": "{}",
                "input_connections": {
                    "input": [{"id": 0, "output_name": "output"}],
                },
                "workflow_outputs": [],
            },
            "2": {
                "id": 2,
                "type": "tool",
                "label": "final_cat",
                "tool_id": "cat1",
                "tool_version": "1.0",
                "tool_state": "{}",
                "input_connections": {
                    "input1": [{"id": 1, "output_name": "output"}],
                },
                "workflow_outputs": [{"output_name": "out_file1", "label": "the_output"}],
            },
        },
    }
    as_format2 = from_native(native_workflow)
    as_native_rt = to_native(as_format2)
    assert_valid_native(as_native_rt)
    assert len(as_native_rt["steps"]) == 3
    # final_cat should connect to step 1 (the unlabeled pause)
    final_cat = as_native_rt["steps"]["2"]
    conn = final_cat["input_connections"]["input1"]
    assert conn[0]["id"] == 1
    # Step 1 should be a pause, not reassigned
    assert as_native_rt["steps"]["1"]["type"] == "pause"
    assert as_native_rt["steps"]["1"]["label"] is None


def test_user_defined_tool_to_native():
    """Format2 workflow with GalaxyUserTool converts to native with tool_representation."""
    as_dict_native = to_native(USER_DEFINED_TOOL_WORKFLOW)
    assert_valid_native(as_dict_native)
    steps = as_dict_native["steps"]
    assert len(steps) == 2  # input + tool
    tool_step = steps["1"]
    assert tool_step["type"] == "tool"
    assert "tool_representation" in tool_step
    tool_rep = tool_step["tool_representation"]
    assert tool_rep["class"] == "GalaxyUserTool"
    assert tool_rep["name"] == "cat_user_defined"
    assert tool_rep["container"] == "busybox"
    # tool_id and tool_uuid should be None for user-defined tools
    assert tool_step.get("tool_id") is None
    assert tool_step.get("tool_uuid") is None


def test_user_defined_tool_round_trip():
    """GalaxyUserTool survives Format2 -> native -> Format2 round-trip."""
    as_dict = round_trip(USER_DEFINED_TOOL_WORKFLOW)
    step = as_dict["steps"]["my_tool"]
    assert "run" in step
    run = step["run"]
    assert run["class"] == "GalaxyUserTool"
    assert run["name"] == "cat_user_defined"
    assert run["container"] == "busybox"
    # Should not have tool_id since it's a user-defined tool
    assert "tool_id" not in step


def test_native_user_defined_tool_to_format2():
    """Native workflow with tool_representation exports as run: {class: GalaxyUserTool, ...}."""
    native_workflow = {
        "a_galaxy_workflow": "true",
        "format-version": "0.1",
        "name": "User Tool Test",
        "steps": {
            "0": {
                "id": 0,
                "type": "data_input",
                "label": "the_input",
                "tool_state": '{"name": "the_input"}',
                "input_connections": {},
                "workflow_outputs": [],
            },
            "1": {
                "id": 1,
                "type": "tool",
                "label": "my_tool",
                "tool_id": None,
                "tool_version": None,
                "tool_uuid": None,
                "tool_representation": {
                    "class": "GalaxyUserTool",
                    "id": "cat_user_defined",
                    "version": "0.1",
                    "name": "cat_user_defined",
                    "description": "concatenates a file",
                    "container": "busybox",
                    "shell_command": "cat '$(inputs.input1.path)' > output.txt",
                    "inputs": [{"name": "input1", "type": "data", "format": "txt"}],
                    "outputs": [{"name": "output1", "type": "data", "format": "txt", "from_work_dir": "output.txt"}],
                },
                "tool_state": "{}",
                "input_connections": {
                    "input1": [{"id": 0, "output_name": "output"}],
                },
                "workflow_outputs": [{"output_name": "output1", "label": "the_output"}],
            },
        },
    }
    as_format2 = from_native(native_workflow)
    step = as_format2["steps"]["my_tool"]
    assert "run" in step
    assert step["run"]["class"] == "GalaxyUserTool"
    assert step["run"]["name"] == "cat_user_defined"
    assert step["run"]["container"] == "busybox"
    assert "tool_id" not in step
    assert "tool_version" not in step


def assert_valid_format2(as_dict_format2):
    assert as_dict_format2["class"] == "GalaxyWorkflow"
    assert "steps" in as_dict_format2
