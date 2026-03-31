"""Example workflows used by testing infrastructure.

Workflows are migrating to gxformat2/examples/ as files.
Constants here load from those files where available, with remaining
constants defined inline until migrated.
"""

from gxformat2.examples import load_contents

BASIC_WORKFLOW = load_contents("synthetic-basic.gxwf.yml")
NESTED_WORKFLOW = load_contents("synthetic-nested-subworkflow.gxwf.yml")
OPTIONAL_INPUT = load_contents("synthetic-optional-input.gxwf.yml")
WHEN_EXAMPLE = load_contents("synthetic-when-step.gxwf.yml")
PJA_1 = load_contents("synthetic-pja-hide-rename.gxwf.yml")
PAIRED_LIST_COLLECTION_INPUT = load_contents("synthetic-paired-list-input.gxwf.yml")
FLOAT_INPUT_DEFAULT = load_contents("synthetic-float-input-default.gxwf.yml")
STRING_INPUT = load_contents("synthetic-string-input.gxwf.yml")
INTEGER_INPUT = load_contents("synthetic-integer-type-alias.gxwf.yml")
MULTI_DATA_INPUT_WORKFLOW = load_contents("synthetic-multi-data-input.gxwf.yml")
MULTI_STRING_INPUT_WORKFLOW = load_contents("synthetic-multi-string-input.gxwf.yml")
RULES_TOOL = load_contents("synthetic-rules-tool.gxwf.yml")
RUNTIME_INPUTS = load_contents("synthetic-runtime-inputs.gxwf.yml")
SLASH_IN_INPUT_LABEL = load_contents("synthetic-slash-in-input-label.gxwf.yml")
SLASH_IN_STEP_LABEL_EXPLICIT_OUTPUT = load_contents("synthetic-slash-in-step-label.gxwf.yml")
SLASH_IN_LABEL_CHAINED = load_contents("synthetic-slash-in-label-chained.gxwf.yml")
SAMPLE_SHEET_COLLECTION_INPUT = load_contents("synthetic-sample-sheet-input.gxwf.yml")
WORKFLOW_WITH_COMMENTS_DICT = load_contents("synthetic-comments-dict.gxwf.yml")
USER_DEFINED_TOOL_WORKFLOW = load_contents("synthetic-user-defined-tool.gxwf.yml")

WORKFLOW_WITH_REPEAT = """
class: GalaxyWorkflow
inputs:
  input1: data
outputs:
  out1:
    outputSource: first_cat/out_file1
steps:
  first_cat:
    tool_id: cat
    in:
      input1: input1
      queries_0|input2: input1
      queries_1|input2: input1
"""

INT_INPUT = """
class: GalaxyWorkflow
inputs:
  input_d: File
  num_lines:
    type: int
outputs:
  out1:
    outputSource: random_lines/out_file1
steps:
  random_lines:
    tool_id: random_lines1
    in:
      num_lines: num_lines
      input: input_d
    state:
      seed_source:
        seed_source_selector: set_seed
        seed: asdf
"""

URL_SUBWORKFLOW = """
class: GalaxyWorkflow
inputs:
  outer_input: data
steps:
  first_cat:
    tool_id: cat1
    in:
      input1: outer_input
  nested_workflow:
    run: https://example.com/my_subworkflow.gxwf.yml
    in:
      inner_input: first_cat/out_file1
"""

TRS_URL_SUBWORKFLOW = """
class: GalaxyWorkflow
inputs:
  outer_input: data
steps:
  first_cat:
    tool_id: cat1
    in:
      input1: outer_input
  nested_workflow:
    run: https://dockstore.org/api/ga4gh/trs/v2/tools/%23workflow%2Fgithub.com%2Fexample/versions/main/PLAIN-GALAXY/descriptor
    in:
      inner_input: first_cat/out_file1
"""

WORKFLOW_WITH_COMMENTS_LIST = """
class: GalaxyWorkflow
inputs:
  the_input: data
outputs:
  the_output:
    outputSource: cat/out_file1
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  - type: text
    position: [100, 200]
    size: [200, 50]
    color: blue
    text: "Check adapters"
    text_size: 2
    bold: true

  - type: markdown
    position: [300, 50]
    size: [400, 300]
    text: |
      # Preprocessing Pipeline
      Quality filtering and adapter trimming.

  - type: freehand
    position: [200, 300]
    size: [100, 80]
    color: red
    thickness: 3
    line: [[210, 310], [220, 330], [250, 360]]
"""

WORKFLOW_WITH_FRAME_MIXED_REFS = """
class: GalaxyWorkflow
inputs:
  the_input: data
outputs:
  the_output:
    outputSource: cat/out_file1
steps:
  cat:
    tool_id: cat1
    in:
      input1: the_input
comments:
  - label: my_note
    type: text
    position: [100, 200]
    size: [200, 50]
    color: none
    text: "A note"
    text_size: 1

  - type: text
    position: [150, 250]
    size: [200, 50]
    color: none
    text: "Unlabeled note"
    text_size: 1

  - label: my_frame
    type: frame
    position: [50, 50]
    size: [600, 400]
    color: none
    title: My Frame
    contains_steps:
      - cat
    contains_comments:
      - my_note
      - 1
"""
