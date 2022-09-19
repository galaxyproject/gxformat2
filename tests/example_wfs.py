"""Example workflows used by testing infrastructure."""

BASIC_WORKFLOW = """
class: GalaxyWorkflow
label: Simple workflow
doc: |
  Simple workflow that no-op cats a file and then selects 10 random lines.
inputs:
  the_input:
    type: File
    doc: input doc
outputs:
  the_output:
    outputSource: cat/out_file1
steps:
  cat:
    tool_id: cat1
    doc: cat doc
    in:
      input1: the_input
"""

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

NESTED_WORKFLOW = """
class: GalaxyWorkflow
inputs:
  outer_input: data
outputs:
  outer_output:
    outputSource: second_cat/out_file1
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
      outputs:
        workflow_output:
          outputSource: random_lines/out_file1
      steps:
        random_lines:
          tool_id: random_lines1
          state:
            num_lines: 2
            input:
              $link: inner_input
            seed_source:
              seed_source_selector: set_seed
              seed: asdf
    in:
      inner_input: first_cat/out_file1
  split:
    tool_id: split
    in:
      input1: nested_workflow/workflow_output
  second_cat:
    tool_id: cat_list
    in:
      input1: split/output
"""

RULES_TOOL = """
class: GalaxyWorkflow
inputs:
  input_c: collection
outputs:
  out1:
    outputSource: random_lines/out_file1
steps:
  apply:
    tool_id: __APPLY_RULES__
    state:
      input:
        $link: input_c
      rules:
        rules:
          - type: add_column_metadata
            value: identifier0
          - type: add_column_metadata
            value: identifier0
        mapping:
          - type: list_identifiers
            columns: [0, 1]
  random_lines:
    tool_id: random_lines1
    state:
      num_lines: 1
      input:
        $link: apply/output
      seed_source:
        seed_source_selector: set_seed
        seed: asdf
"""

RUNTIME_INPUTS = """
class: GalaxyWorkflow
inputs:
  input1: data
outputs:
  out1:
    outputSource: random/out_file1
steps:
  the_pause:
    type: pause
    in:
      input: input1
  random:
    tool_id: random_lines1
    runtime_inputs:
      - num_lines
    state:
      input:
        $link: the_pause
      seed_source:
        seed_source_selector: set_seed
        seed: asdf
"""

PJA_1 = """
class: GalaxyWorkflow
inputs:
  input1: data
outputs:
  out1:
    outputSource: second_cat/out_file1
steps:
  first_cat:
    tool_id: cat1
    in:
      input1: input1
    out:
       out_file1:
         hide: true
         rename: "the new value"
  second_cat:
    tool_id: cat1
    in:
      input1: first_cat/out_file1
"""

OPTIONAL_INPUT = """
class: GalaxyWorkflow
inputs:
  the_input:
    type: File
    optional: true
steps:
  cat:
    tool_id: cat_optional
    in:
      input1: the_input
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


# not valid according to the schema, but the native format calls them
# integers and some old examples used this syntax. Make illegal post v19.09?
INTEGER_INPUT = """
class: GalaxyWorkflow
inputs:
  input_d:
    type: data
  num_lines:
    type: integer
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


FLOAT_INPUT_DEFAULT = """
class: GalaxyWorkflow
inputs:
  input_d: File
  num_lines:
    type: float
    default: 6.0
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


STRING_INPUT = """
class: GalaxyWorkflow
inputs:
  input_d:
    type: data
  seed:
    type: string
    default: mycooldefault
outputs:
  out1:
    outputSource: random_lines/out_file1
steps:
  random_lines:
    tool_id: random_lines1
    in:
      'seed_source|seed': seed
      input: input_d
    state:
      num_lines: 5
      seed_source:
        seed_source_selector: set_seed
"""


WHEN_EXAMPLE = """
class: GalaxyWorkflow
inputs:
  input_d:
    type: data
  seed:
    type: string
    default: mycooldefault
outputs:
  out1:
    outputSource: random_lines/out_file1
steps:
  random_lines:
    tool_id: random_lines1
    in:
      'seed_source|seed': seed
      input: input_d
    state:
      num_lines: 5
      seed_source:
        seed_source_selector: set_seed
    when: $(inputs.seed != 'skip')
"""

MULTI_DATA_INPUT_WORKFLOW = """
class: GalaxyWorkflow
label: Multi-data input
inputs:
  optional:
    optional: true
    type: data
  required:
    optional: false
    type: data
steps:
  count_multi_file:
    tool_id: count_multi_file
    in:
      input1:
        source:
        - required
        - optional
"""
