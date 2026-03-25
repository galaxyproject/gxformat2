"""Module for exporting Galaxy workflows to CWL abstract interface."""

import argparse
import sys
from typing import Any

from gxformat2.normalized import NormalizedFormat2, NormalizedWorkflowStep
from gxformat2.schema.gxformat2 import GalaxyType, WorkflowInputParameter, WorkflowOutputParameter, WorkflowStepOutput
from gxformat2.to_format2 import ensure_format2
from gxformat2.yaml import ordered_dump_to_path, ordered_load

CWL_VERSION = "v1.2"

SCRIPT_DESCRIPTION = """
This script converts an executable Galaxy workflow (in either format - Format 2
or native .ga) into an abstract CWL representation.

In order to represent Galaxy tool executions in the Common Workflow Language
workflow language, they are serialized as v1.2+ abstract 'Operation' classes.
Because abstract 'Operation' classes are used, the resulting CWL workflow is
not executable - either in Galaxy or by CWL implementations. The resulting CWL
file should be thought of more as a common metadata specification describing
the workflow structure.
"""


def from_dict(workflow_dict, subworkflow=False):
    """Convert Galaxy workflow into abstract CWL representation.

    Accepts any workflow representation (raw dict, path, or typed model).
    """
    nf2 = ensure_format2(workflow_dict)

    _ensure_implicit_step_outs(nf2)

    requirements: dict[str, Any] = {}
    abstract_dict: dict[str, Any] = {
        "class": "Workflow",
    }
    if nf2.label:
        abstract_dict["label"] = nf2.label
    if nf2.doc:
        abstract_dict["doc"] = nf2.doc
    if not subworkflow:
        abstract_dict["cwlVersion"] = CWL_VERSION

    abstract_dict["inputs"] = _inputs_to_abstract(nf2.inputs)
    abstract_dict["outputs"] = _outputs_to_abstract(nf2.outputs)

    steps = {}
    for step in nf2.steps:
        label = step.label or step.id
        steps[label] = _step_to_abstract(step, requirements=requirements)

    abstract_dict["steps"] = steps
    if requirements:
        abstract_dict["requirements"] = requirements
    return abstract_dict


def _step_to_abstract(step: NormalizedWorkflowStep, requirements: dict):
    """Convert NormalizedWorkflowStep to CWL 1.2+ abstract operation."""
    abstract_step: dict[str, Any] = {}
    if step.doc:
        abstract_step["doc"] = step.doc

    if isinstance(step.run, NormalizedFormat2):
        requirements["SubworkflowFeatureRequirement"] = {}
        abstract_step["run"] = from_dict(step.run, subworkflow=True)
    elif isinstance(step.run, dict) and step.run.get("class") == "GalaxyWorkflow":
        # Unresolved dict subworkflow — normalize and recurse
        requirements["SubworkflowFeatureRequirement"] = {}
        abstract_step["run"] = from_dict(step.run, subworkflow=True)
    else:
        abstract_step["run"] = {
            "class": "Operation",
            "doc": step.doc or "",
            "inputs": {},  # TODO
            "outputs": {},  # TODO
        }

    abstract_step["in"] = _step_inputs_to_abstract(step)
    abstract_step["out"] = _step_outputs_to_abstract(step)
    return abstract_step


def _step_inputs_to_abstract(step: NormalizedWorkflowStep):
    """Convert step inputs to CWL abstract 'in' dict."""
    result = {}
    for step_input in step.in_:
        if step_input.id is None:
            continue
        entry: dict[str, Any] = {}
        if step_input.source is not None:
            entry["source"] = step_input.source
        if step_input.default is not None:
            entry["default"] = step_input.default
        result[step_input.id] = entry
    return result


def _step_outputs_to_abstract(step: NormalizedWorkflowStep):
    """Convert step outputs to CWL abstract 'out' list."""
    return [out.id for out in step.out if out.id is not None]


def _inputs_to_abstract(inputs: list[WorkflowInputParameter]):
    """Convert Format2 inputs to abstract CWL inputs."""
    abstract_inputs: dict[str, Any] = {}
    for inp in inputs:
        input_id = inp.id
        if input_id is None:
            continue
        input_def: dict[str, Any] = {}

        # Convert type
        cwl_type = _galaxy_type_to_cwl(inp.type_)
        if inp.optional:
            cwl_type += "?"
        input_def["type"] = cwl_type

        if inp.default is not None:
            input_def["default"] = inp.default
        if inp.doc:
            doc = inp.doc
            if isinstance(doc, list):
                doc = "\n".join(doc)
            input_def["doc"] = doc
        if inp.label:
            input_def["label"] = inp.label

        abstract_inputs[input_id] = input_def
    return abstract_inputs


def _galaxy_type_to_cwl(galaxy_type: GalaxyType | list[GalaxyType] | None) -> str:
    """Map a Galaxy/Format2 type to a CWL type string."""
    if galaxy_type is None:
        return "File"
    if isinstance(galaxy_type, list):
        # Array type e.g. [string] means "multiple values" → string[]
        for t in galaxy_type:
            if t != GalaxyType.null:
                return _galaxy_type_to_cwl(t) + "[]"
        return "File"
    if galaxy_type == GalaxyType.data:
        return "File"
    if galaxy_type == GalaxyType.collection:
        # TODO: handle nested collections, pairs, etc...
        return "File[]"
    return galaxy_type.value


def _outputs_to_abstract(outputs: list[WorkflowOutputParameter]):
    """Convert Format2 outputs to abstract CWL outputs."""
    abstract_outputs: dict[str, Any] = {}
    for out in outputs:
        output_id = out.id
        if output_id is None:
            continue
        output_def: dict[str, Any] = {}
        cwl_type = _galaxy_type_to_cwl(out.type_)
        if not cwl_type or cwl_type == "None":
            cwl_type = "File"
        output_def["type"] = cwl_type
        if out.outputSource:
            output_def["outputSource"] = out.outputSource
        if out.doc:
            doc = out.doc
            if isinstance(doc, list):
                doc = "\n".join(doc)
            output_def["doc"] = doc
        abstract_outputs[output_id] = output_def
    return abstract_outputs


def _ensure_implicit_step_outs(nf2: NormalizedFormat2):
    """Ensure steps have explicit 'out' for all referenced outputs.

    CWL requires explicit step output declarations. In Format2, these
    can be implicit — referenced in workflow outputs or step inputs
    without being declared in the step's 'out'.

    Mutates step.out lists in place.
    """
    outputs_by_label: dict[str, set[str]] = {}

    def register(step_label: str, output_name: str):
        outputs_by_label.setdefault(step_label, set()).add(output_name)

    def register_source(source: str):
        if "/" in source:
            ref = nf2.resolve_source(source)
            register(ref.step_label, ref.output_name)

    # From workflow outputs
    for out in nf2.outputs:
        if out.outputSource:
            register_source(out.outputSource)

    # From step inputs
    for step in nf2.steps:
        for step_in in step.in_:
            if step_in.source is None:
                continue
            sources = step_in.source if isinstance(step_in.source, list) else [step_in.source]
            for src in sources:
                register_source(src)

    # Ensure each step has the referenced outputs declared
    for step in nf2.steps:
        label = step.label or step.id
        needed = outputs_by_label.get(label, set())
        existing = {o.id for o in step.out if o.id}
        for out_name in needed - existing:
            step.out.append(WorkflowStepOutput(id=out_name))


def main(argv=None):
    """Entry point for script to export abstract interface."""
    if argv is None:
        argv = sys.argv[1:]

    args = _parser().parse_args(argv)

    workflow_path = args.input_path
    output_path = args.output_path or (workflow_path + ".abstract.cwl")

    if workflow_path == "-":
        workflow_dict = ordered_load(sys.stdin)
    else:
        workflow_dict = ordered_load(workflow_path)

    abstract_dict = from_dict(workflow_dict)
    ordered_dump_to_path(abstract_dict, output_path)
    return 0


def _parser():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument("input_path", metavar="INPUT", type=str, help="input workflow path (.ga/gxwf.yml)")
    parser.add_argument("output_path", metavar="OUTPUT", type=str, nargs="?", help="output workflow path (.cwl)")
    return parser


if __name__ == "__main__":
    sys.exit(main())


__all__ = ("main", "from_dict")
