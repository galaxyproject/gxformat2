"""Workflow linting entry point - main script."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import OrderedDict
from urllib.parse import urlparse

from pydantic import ValidationError

from gxformat2.linting import LintContext
from gxformat2.markdown_parse import validate_galaxy_markdown
from gxformat2.normalized import (
    ensure_format2,
    ensure_native,
    NormalizedFormat2,
    NormalizedWorkflowStep,
)
from gxformat2.normalized._native import (
    NativeStepType,
    NormalizedNativeStep,
    NormalizedNativeWorkflow,
)
from gxformat2.schema.gxformat2 import CreatorPerson, GalaxyType
from gxformat2.schema.gxformat2 import GalaxyWorkflow as Format2LaxModel
from gxformat2.schema.gxformat2_strict import GalaxyWorkflow as Format2StrictModel
from gxformat2.schema.native import NativeGalaxyWorkflow as NativeLaxModel
from gxformat2.schema.native_strict import NativeGalaxyWorkflow as NativeStrictModel
from gxformat2.yaml import ordered_load, ordered_load_path

EXIT_CODE_SUCCESS = 0
EXIT_CODE_LINT_FAILED = 1
EXIT_CODE_FORMAT_ERROR = 2
EXIT_CODE_FILE_PARSE_FAILED = 3

LINT_FAILED_NO_OUTPUTS = "Workflow contained no outputs"
LINT_FAILED_OUTPUT_NO_LABEL = "Workflow contained output without a label"


def lint_ga(lint_context, nnw: NormalizedNativeWorkflow, raw_dict: dict | None = None):
    """Lint a native Galaxy workflow and populate the corresponding LintContext."""
    # Check fields that the model defaults mask
    if raw_dict is not None:
        if "a_galaxy_workflow" not in raw_dict:
            lint_context.error("expected to find key [a_galaxy_workflow] but absent")
        elif raw_dict.get("a_galaxy_workflow") != "true":
            lint_context.error(
                f"expected value [{raw_dict.get('a_galaxy_workflow')}] with key [a_galaxy_workflow] to be true"
            )
        if "format-version" not in raw_dict:
            lint_context.error("expected to find key [format-version] but absent")
        elif raw_dict.get("format-version") != "0.1":
            lint_context.error(f"expected value [{raw_dict.get('format-version')}] with key [format-version] to be 0.1")
        if "steps" not in raw_dict:
            lint_context.error("expected to find key [steps] but absent")
            return

    found_outputs = False
    found_output_without_label = False

    for order_index_str, step in nnw.steps.items():
        if not order_index_str.isdigit():
            lint_context.error("expected step_key to be integer not [{value}]", value=order_index_str)

        for workflow_output in step.workflow_outputs:
            found_outputs = True
            if not workflow_output.label:
                found_output_without_label = True

        if step.type_ == NativeStepType.subworkflow and step.subworkflow is not None:
            if not step.subworkflow.steps:
                lint_context.error("expected to find key [steps] but absent")
            else:
                lint_ga(lint_context, step.subworkflow)

        _lint_step_errors(lint_context, step.errors)
        _lint_tool_if_present(lint_context, step.tool_id)

    _validate_report(lint_context, nnw.report)

    if not found_outputs:
        lint_context.warn(LINT_FAILED_NO_OUTPUTS)
    if found_output_without_label:
        lint_context.warn(LINT_FAILED_OUTPUT_NO_LABEL)

    _lint_training(lint_context, nnw.tags, nnw.annotation)


def lint_ga_path(lint_context, path):
    """Apply linting of native workflows to specified path."""
    workflow_dict = ordered_load_path(path)
    nnw = ensure_native(workflow_dict)
    return lint_ga(lint_context, nnw, raw_dict=workflow_dict)


def lint_format2_path(lint_context, path):
    """Apply linting of Format2 workflows to specified path."""
    workflow_dict = ordered_load_path(path)
    nf2 = ensure_format2(workflow_dict, expand=True)
    return lint_format2(lint_context, nf2, raw_dict=workflow_dict)


def lint_format2(lint_context, nf2: NormalizedFormat2, raw_dict: dict | None = None):
    """Lint a Format 2 Galaxy workflow and populate the corresponding LintContext."""
    if raw_dict is not None:
        if "steps" not in raw_dict:
            lint_context.error("expected to find key [steps] but absent")
        if "class" not in raw_dict:
            lint_context.error("expected to find key [class] but absent")

    for step in nf2.steps:
        _lint_step_errors(lint_context, step.errors)
        _lint_tool_if_present(lint_context, step.tool_id)
        if isinstance(step.run, NormalizedFormat2):
            if not step.run.steps:
                lint_context.error("expected to find key [steps] but absent")
            else:
                lint_format2(lint_context, step.run)

    _validate_output_sources(lint_context, nf2)
    _validate_input_types(lint_context, nf2)
    _validate_report(lint_context, nf2.report)
    _lint_training(lint_context, nf2.tags, nf2.doc)


def _validate_output_sources(lint_context, nf2: NormalizedFormat2):
    """Check that outputSource references point to existing step/input labels."""
    if not nf2.outputs:
        return
    for output in nf2.outputs:
        output_source = output.outputSource
        if not output_source or not isinstance(output_source, str):
            continue
        step_ref = nf2.resolve_source(output_source).step_label
        if step_ref not in nf2.known_labels:
            output_id = output.id or "?"
            lint_context.error(
                f"Output '{output_id}' references step '{step_ref}' via outputSource "
                f"'{output_source}', but no step or input with that label exists"
            )


def _lint_step_errors(lint_context, step_errors):
    if step_errors is not None:
        lint_context.warn(f"tool step contains error indicated during Galaxy export - {step_errors}")


def _lint_tool_if_present(lint_context, tool_id):
    if tool_id and "testtoolshed" in tool_id:
        lint_context.warn(
            "Step references a tool from the test tool shed, this should be replaced with a production tool"
        )


def _validate_input_types(lint_context: LintContext, nf2: NormalizedFormat2):
    for inp in nf2.inputs:
        if inp.default is None:
            continue
        # type_ lives on concrete subclasses, not BaseInputParameter
        input_type = getattr(inp, "type_", None)
        if isinstance(input_type, list):
            # Array type like [string] — skip default validation for now
            continue
        if input_type == GalaxyType.int or input_type == GalaxyType.integer:
            if not isinstance(inp.default, int):
                lint_context.error("Input default is of invalid type")
        elif input_type == GalaxyType.float or input_type == GalaxyType.double:
            if not isinstance(inp.default, (int, float)):
                lint_context.error("Input default is of invalid type")
        elif input_type == GalaxyType.string or input_type == GalaxyType.text:
            if not isinstance(inp.default, str):
                lint_context.error("Input default is of invalid type")


def _validate_report(lint_context, report):
    """Validate workflow report if present."""
    if report is None:
        return
    markdown = report.markdown
    if not isinstance(markdown, str):
        lint_context.error(f"expected value [{markdown}] with key [markdown] to be of class {str}")
        return
    try:
        validate_galaxy_markdown(markdown)
    except ValueError as e:
        lint_context.error(f"Report markdown validation failed [{e}]")


def _lint_training(lint_context, tags, doc_or_annotation):
    """Lint training-related metadata. Works with either doc (format2) or annotation (native)."""
    if lint_context.training_topic is None:
        return

    if not tags:
        lint_context.warn("Missing tag(s).")
    elif lint_context.training_topic not in tags:
        lint_context.warn(f"Missing expected training topic ({lint_context.training_topic}) as workflow tag.")

    if not doc_or_annotation:
        lint_context.warn("Missing workflow documentation (annotation or doc element)")
    elif isinstance(doc_or_annotation, str) and not doc_or_annotation.strip():
        lint_context.warn("Empty workflow documentation (annotation or doc element)")


def lint_pydantic_validation(lint_context, workflow_dict, format2=False):
    """Validate workflow dict against pydantic schema models.

    Tries strict model (extra=forbid) first. If strict fails, falls back to
    the lax model (extra=allow) to distinguish fundamental type errors from
    merely having extra/unknown fields.
    """
    StrictModel = Format2StrictModel if format2 else NativeStrictModel
    LaxModel = Format2LaxModel if format2 else NativeLaxModel
    strict_errors = None
    try:
        StrictModel.model_validate(workflow_dict)
        return  # strict passes — nothing to report
    except ValidationError as e:
        strict_errors = e.errors()

    # Strict failed — try lax to see if the core schema is valid
    try:
        LaxModel.model_validate(workflow_dict)
        # Lax passes: only extra/unknown fields caused strict failure
        for error in strict_errors:
            loc = " -> ".join(str(p) for p in error["loc"])
            lint_context.warn(f"Schema validation (strict): {error['msg']} at {loc}")
    except ValidationError as e:
        # Lax also fails: fundamental schema errors
        for error in e.errors():
            loc = " -> ".join(str(p) for p in error["loc"])
            lint_context.error(f"Schema validation: {error['msg']} at {loc}")


def lint_best_practices(lint_context, nf2: NormalizedFormat2):
    """Lint best practices for a Galaxy workflow (works for both native and Format2 input)."""
    # annotation / doc
    doc = nf2.doc
    if not doc or not doc.strip():
        lint_context.warn("Workflow is not annotated.")

    # creator
    creators = nf2.creator or []
    if not creators:
        lint_context.warn("Workflow does not specify a creator.")
    else:
        for creator in creators:
            if isinstance(creator, CreatorPerson) and creator.identifier:
                parsed_url = urlparse(creator.identifier)
                if not parsed_url.scheme:
                    lint_context.warn(
                        f'Creator identifier "{creator.identifier}" should be a fully qualified URI, '
                        f'for example "https://orcid.org/0000-0002-1825-0097".'
                    )

    # license
    if not nf2.license:
        lint_context.warn("Workflow does not specify a license.")

    # step-level best practices
    for step in nf2.steps:
        _lint_step_best_practices(lint_context, step)


def _lint_step_best_practices(lint_context, step: NormalizedWorkflowStep):
    """Lint best practices for a single workflow step."""
    step_id = step.label or step.id

    # disconnected inputs
    for step_input in step.in_:
        if step_input.source is None and step_input.default is None:
            lint_context.warn(f"Input {step_input.id} of workflow step {step_id} is disconnected.")

    # missing metadata
    if not step.doc:
        lint_context.warn(f"Workflow step {step_id} has no annotation.")
    if not step.label:
        lint_context.warn(f"Workflow step {step_id} has no label.")

    # untyped parameters
    tool_state = step.state or step.tool_state
    if tool_state:
        if isinstance(tool_state, str):
            try:
                tool_state = json.loads(tool_state)
            except (json.JSONDecodeError, TypeError):
                tool_state = {}
        if isinstance(tool_state, dict) and _check_json_for_untyped_params(tool_state):
            lint_context.warn(f"Workflow step {step_id} specifies an untyped parameter as an input.")

    # untyped parameters in outputs (PJA equivalents in format2)
    if step.out:
        out_data = [o.model_dump(by_alias=True) for o in step.out]
        if _check_json_for_untyped_params(out_data):
            lint_context.warn(f"Workflow step {step_id} specifies an untyped parameter in the post-job actions.")


SKIP_DISCONNECTED_CHECK_TYPES_NATIVE = {
    NativeStepType.data_input,
    NativeStepType.data_collection_input,
    NativeStepType.parameter_input,
    NativeStepType.pause,
}


def _lint_native_step_best_practices(lint_context, step: NormalizedNativeStep):
    """Native-specific step best practice checks that don't survive format2 conversion."""
    step_id = step.label or step.annotation or step.id

    # disconnected inputs — compare declared inputs against input_connections
    if step.type_ not in SKIP_DISCONNECTED_CHECK_TYPES_NATIVE:
        input_connections = step.input_connections
        for input_def in step.inputs:
            if input_def.name and input_def.name not in input_connections:
                lint_context.warn(f"Input {input_def.name} of workflow step {step_id} is disconnected.")

    # untyped parameters in post_job_actions
    if step.post_job_actions:
        pjas = {k: v.model_dump(by_alias=True) for k, v in step.post_job_actions.items()}
        if _check_json_for_untyped_params(pjas):
            lint_context.warn(
                f"Workflow step with ID {step.id} specifies an untyped parameter in the post-job actions."
            )


def _try_build_nf2(lint_context, workflow_dict) -> NormalizedFormat2 | None:
    """Build ExpandedFormat2 from a workflow dict, emitting lint errors on failure."""
    try:
        return ensure_format2(workflow_dict, expand=True)
    except ValidationError as e:
        for error in e.errors():
            loc = " -> ".join(str(p) for p in error["loc"])
            lint_context.error(f"Schema validation: {error['msg']} at {loc}")
        return None
    except (ValueError, json.JSONDecodeError) as e:
        lint_context.error(f"Failed to parse workflow: {e}")
        return None


def _try_build_nnw(lint_context, workflow_dict) -> NormalizedNativeWorkflow | None:
    """Build NormalizedNativeWorkflow from a workflow dict, emitting lint errors on failure."""
    try:
        return ensure_native(workflow_dict)
    except ValidationError as e:
        for error in e.errors():
            loc = " -> ".join(str(p) for p in error["loc"])
            lint_context.error(f"Schema validation: {error['msg']} at {loc}")
        return None
    except (ValueError, json.JSONDecodeError) as e:
        lint_context.error(f"Failed to parse workflow: {e}")
        return None


def lint_best_practices_ga(lint_context, workflow_dict):
    """Lint best practices for a native Galaxy workflow.

    Runs shared best practices on NormalizedFormat2 plus native-specific
    checks (disconnected inputs, PJA untyped params) on NormalizedNativeWorkflow.
    """
    nf2 = _try_build_nf2(lint_context, workflow_dict)
    if nf2 is not None:
        lint_best_practices(lint_context, nf2)
    # Native-specific checks that don't survive format2 conversion
    nnw = _try_build_nnw(lint_context, workflow_dict)
    if nnw is not None:
        for step in nnw.steps.values():
            _lint_native_step_best_practices(lint_context, step)


def lint_best_practices_format2(lint_context, workflow_dict):
    """Lint best practices for a Format2 Galaxy workflow."""
    nf2 = _try_build_nf2(lint_context, workflow_dict)
    if nf2 is not None:
        lint_best_practices(lint_context, nf2)


def _check_json_for_untyped_params(j):
    """Check for untyped workflow parameters (``${...}``) in a JSON-like structure."""
    values = j.values() if isinstance(j, dict) else j
    for value in values:
        if type(value) in [list, dict, OrderedDict]:
            if _check_json_for_untyped_params(value):
                return True
        elif isinstance(value, str):
            if re.match(r"\$\{.+?\}", value):
                return True
    return False


def main(argv=None):
    """Script entry point for linting workflows."""
    if argv is None:
        argv = sys.argv
    args = _parser().parse_args(argv[1:])
    path = args.path
    with open(path) as f:
        try:
            workflow_dict = ordered_load(f)
        except Exception:
            return EXIT_CODE_FILE_PARSE_FAILED

    workflow_class = workflow_dict.get("class")
    is_format2 = workflow_class == "GalaxyWorkflow"
    lint_context = LintContext(training_topic=args.training_topic)

    # Build normalized models — fail fast if invalid
    nf2 = None
    nnw = None

    if is_format2:
        nf2 = _try_build_nf2(lint_context, workflow_dict)
    else:
        nnw = _try_build_nnw(lint_context, workflow_dict)
        # Also build ExpandedFormat2 for best practices (independent)
        nf2 = _try_build_nf2(lint_context, workflow_dict)

    # Structural lint (format-specific, needs valid model)
    if is_format2 and nf2 is not None:
        lint_format2(lint_context, nf2, raw_dict=workflow_dict)
    elif not is_format2 and nnw is not None:
        lint_ga(lint_context, nnw, raw_dict=workflow_dict)

    # Pydantic strict/lax validation (always runs on raw dict)
    lint_pydantic_validation(lint_context, workflow_dict, format2=is_format2)

    # Best practices (merged, runs on NormalizedFormat2)
    if not args.skip_best_practices and nf2 is not None:
        lint_best_practices(lint_context, nf2)
        # Native-specific best practice checks
        if not is_format2 and nnw is not None:
            for step in nnw.steps.values():
                _lint_native_step_best_practices(lint_context, step)

    lint_context.print_messages()
    if lint_context.found_errors:
        return EXIT_CODE_FORMAT_ERROR
    elif lint_context.found_warns:
        return EXIT_CODE_LINT_FAILED
    else:
        return EXIT_CODE_SUCCESS


SCRIPT_DESCRIPTION = """
Lint Galaxy workflows (Format 2 or native .ga) for common issues.
Best-practice user-facing workflows should also be linted with Planemo.
"""


def _parser():
    parser = argparse.ArgumentParser(description=SCRIPT_DESCRIPTION)
    parser.add_argument(
        "--training-topic", required=False, help="If this is a training workflow, specify a training topic."
    )
    parser.add_argument(
        "--skip-best-practices",
        action="store_true",
        default=False,
        help="Skip best practice checks (annotation, creator, license, step metadata).",
    )
    parser.add_argument("path", metavar="PATH", type=str, help="workflow path")
    return parser


if __name__ == "__main__":
    sys.exit(main())


__all__ = (
    "main",
    "lint_format2",
    "lint_ga",
    "lint_best_practices",
    "lint_best_practices_format2",
    "lint_best_practices_ga",
    "lint_pydantic_validation",
)
