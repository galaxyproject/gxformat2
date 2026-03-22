"""Workflow linting entry point - main script."""

import argparse
import json
import os
import re
import sys
from collections import OrderedDict
from pathlib import Path
from urllib.parse import urlparse

from gxformat2._scripts import ensure_format2
from gxformat2.linting import LintContext
from gxformat2.markdown_parse import validate_galaxy_markdown
from gxformat2.normalize import Inputs, walk_id_list_or_dict
from gxformat2.yaml import ordered_load, ordered_load_path

EXIT_CODE_SUCCESS = 0
EXIT_CODE_LINT_FAILED = 1
EXIT_CODE_FORMAT_ERROR = 2
EXIT_CODE_FILE_PARSE_FAILED = 3

LINT_FAILED_NO_OUTPUTS = "Workflow contained no outputs"
LINT_FAILED_OUTPUT_NO_LABEL = "Workflow contained output without a label"


def ensure_key(lint_context, has_keys, key, has_class=None, has_value=None):
    if key not in has_keys:
        lint_context.error("expected to find key [{key}] but absent", key=key)
        return None

    value = has_keys[key]
    return ensure_key_has_value(lint_context, has_keys, key, value, has_class=has_class, has_value=has_value)


def ensure_key_if_present(lint_context, has_keys, key, default=None, has_class=None):
    if key not in has_keys:
        return default

    value = has_keys[key]
    return ensure_key_has_value(lint_context, has_keys, key, value, has_class=has_class, has_value=None)


def ensure_key_has_value(lint_context, has_keys, key, value, has_class=None, has_value=None):
    if has_class is not None and not isinstance(value, has_class):
        lint_context.error(f"expected value [{value}] with key [{key}] to be of class {has_class}")
    if has_value is not None and value != has_value:
        lint_context.error(f"expected value [{value}] with key [{key}] to be {has_value}")
    return value


def _lint_step_errors(lint_context, step):
    step_errors = step.get("errors")
    if step_errors is not None:
        lint_context.warn(f"tool step contains error indicated during Galaxy export - {step_errors}")


def lint_ga_path(lint_context, path):
    """Apply linting of native workflows to specified path."""
    workflow_dict = ordered_load_path(path)
    return lint_ga(lint_context, workflow_dict, path=path)


def lint_ga(lint_context, workflow_dict, path=None):
    """Lint a native/legacy style Galaxy workflow and populate the corresponding LintContext."""
    ensure_key(lint_context, workflow_dict, "format-version", has_value="0.1")
    ensure_key(lint_context, workflow_dict, "a_galaxy_workflow", has_value="true")

    native_steps = ensure_key(lint_context, workflow_dict, "steps", has_class=dict) or {}

    found_outputs = False
    found_output_without_label = False
    for order_index_str, step in native_steps.items():
        if not order_index_str.isdigit():
            lint_context.error("expected step_key to be integer not [{value}]", value=order_index_str)

        workflow_outputs = ensure_key_if_present(lint_context, step, "workflow_outputs", default=[], has_class=list)
        for workflow_output in workflow_outputs:
            found_outputs = True

            if not workflow_output.get("label"):
                found_output_without_label = True

        step_type = step.get("type")
        if step_type == "subworkflow":
            subworkflow = ensure_key(lint_context, step, "subworkflow", has_class=dict)
            lint_ga(lint_context, subworkflow)

        _lint_step_errors(lint_context, step)
        _lint_tool_if_present(lint_context, step)

    _validate_report(lint_context, workflow_dict)
    if not found_outputs:
        lint_context.warn(LINT_FAILED_NO_OUTPUTS)

    if found_output_without_label:
        lint_context.warn(LINT_FAILED_OUTPUT_NO_LABEL)

    _lint_training(lint_context, workflow_dict)


def lint_format2(lint_context, workflow_dict, path=None):
    """Lint a Format 2 Galaxy workflow and populate the corresponding LintContext."""
    from gxformat2.schema.v19_09 import load_document
    from schema_salad.exceptions import SchemaSaladException  # type: ignore

    file_uri = Path(os.path.abspath(path)).as_uri()
    try:
        load_document(file_uri)
    except SchemaSaladException as e:
        lint_context.error("Validation failed " + str(e))

    steps = ensure_key_if_present(lint_context, workflow_dict, "steps", default={}, has_class=(dict, list))
    steps = steps.values() if isinstance(steps, dict) else steps
    for step in steps:
        _lint_step_errors(lint_context, step)
        _lint_tool_if_present(lint_context, step)

    _validate_input_types(lint_context, workflow_dict)
    _validate_report(lint_context, workflow_dict)
    _lint_training(lint_context, workflow_dict)


def _validate_input_types(lint_context: LintContext, workflow_dict: dict):
    try:
        inputs = Inputs(workflow_dict)
    except Exception:
        # bad document, can't process inputs...
        return
    for input_def in inputs._inputs:
        input_type = input_def.get("type")
        if "default" in input_def:
            input_default = input_def["default"]
            if input_type == "int":
                if not isinstance(input_default, int):
                    lint_context.error("Input default is of invalid type")
            elif input_type == "float":
                if not isinstance(input_default, (int, float)):
                    lint_context.error("Input default is of invalid type")
            elif input_type == "string":
                if not isinstance(input_default, str):
                    lint_context.error("Input default is of invalid type")


def _lint_tool_if_present(lint_context, step_dict):
    tool_id = step_dict.get("tool_id")
    if tool_id and "testtoolshed" in tool_id:
        lint_context.warn(
            "Step references a tool from the test tool shed, this should be replaced with a production tool"
        )


def _validate_report(lint_context, workflow_dict):
    report_dict = ensure_key_if_present(lint_context, workflow_dict, "report", default=None, has_class=dict)
    if report_dict is not None:
        markdown = ensure_key(lint_context, report_dict, "markdown", has_class=str)
        if isinstance(markdown, str):
            try:
                validate_galaxy_markdown(markdown)
            except ValueError as e:
                lint_context.error(f"Report markdown validation failed [{e}]")


def _lint_training(lint_context, workflow_dict):
    if lint_context.training_topic is None:
        return

    if "tags" not in workflow_dict:
        lint_context.warn("Missing tag(s).")
    else:
        tags = workflow_dict["tags"]
        if lint_context.training_topic not in tags:
            lint_context.warn(f"Missing expected training topic ({lint_context.training_topic}) as workflow tag.")
    # Move up into individual lints - all workflows should have docs.
    format2_dict = ensure_format2(workflow_dict)
    if "doc" not in format2_dict:
        lint_context.warn("Missing workflow documentation (annotation or doc element)")
    elif not format2_dict["doc"]:
        lint_context.warn("Empty workflow documentation (annotation or doc element)")


def lint_pydantic_validation(lint_context, workflow_dict, format2=False):
    """Validate workflow dict against pydantic schema models.

    Tries strict model (extra=forbid) first. If strict fails, falls back to
    the lax model (extra=allow) to distinguish fundamental type errors from
    merely having extra/unknown fields.
    """
    from pydantic import ValidationError

    if format2:
        from gxformat2.schema.gxformat2_strict import GalaxyWorkflow as StrictModel
        from gxformat2.schema.gxformat2 import GalaxyWorkflow as LaxModel
    else:
        from gxformat2.schema.native_strict import NativeGalaxyWorkflow as StrictModel
        from gxformat2.schema.native import NativeGalaxyWorkflow as LaxModel

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


SKIP_DISCONNECTED_CHECK_TYPES = {"data_input", "data_collection_input", "parameter_input", "pause"}


def lint_best_practices_ga(lint_context, workflow_dict):
    """Lint best practices for a native Galaxy workflow."""
    _lint_best_practices(lint_context, workflow_dict, format2=False)
    steps = workflow_dict.get("steps", {})
    for step in steps.values():
        _lint_step_best_practices_ga(lint_context, step)


def lint_best_practices_format2(lint_context, workflow_dict):
    """Lint best practices for a Format2 Galaxy workflow."""
    _lint_best_practices(lint_context, workflow_dict, format2=True)
    steps = workflow_dict.get("steps", {})
    is_dict = isinstance(steps, dict)
    for step_key, step in walk_id_list_or_dict(steps):
        # For dict steps, the key serves as the implicit label
        _lint_step_best_practices_format2(lint_context, step, dict_key=step_key if is_dict else None)


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


def _lint_best_practices(lint_context, workflow_dict, format2=False):
    """Lint best practices shared across both native and Format2 workflows."""
    # annotation / doc
    if format2:
        doc = workflow_dict.get("doc")
        if not doc or (isinstance(doc, list) and not any(doc)):
            lint_context.warn("Workflow is not annotated.")
    else:
        if not workflow_dict.get("annotation"):
            lint_context.warn("Workflow is not annotated.")

    # creator
    creators = workflow_dict.get("creator", [])
    if not creators:
        lint_context.warn("Workflow does not specify a creator.")
    else:
        if not isinstance(creators, list):
            creators = [creators]
        for creator in creators:
            if creator.get("class", "").lower() == "person" and "identifier" in creator:
                identifier = creator["identifier"]
                parsed_url = urlparse(identifier)
                if not parsed_url.scheme:
                    lint_context.warn(
                        f'Creator identifier "{identifier}" should be a fully qualified URI, '
                        f'for example "https://orcid.org/0000-0002-1825-0097".'
                    )

    # license
    if not workflow_dict.get("license"):
        lint_context.warn("Workflow does not specify a license.")


def _lint_step_best_practices_ga(lint_context, step):
    """Lint best practices for a native Galaxy workflow step."""
    step_id = step.get("id")
    step_type = step.get("type")

    # disconnected inputs
    if step_type not in SKIP_DISCONNECTED_CHECK_TYPES:
        input_connections = step.get("input_connections") or {}
        for input_def in step.get("inputs", []):
            input_name = input_def.get("name")
            if input_name and input_name not in input_connections:
                lint_context.warn(
                    f"Input {input_name} of workflow step {step.get('annotation') or step_id} is disconnected."
                )

    # missing metadata
    if not step.get("annotation"):
        lint_context.warn(f"Workflow step with ID {step_id} has no annotation.")
    if not step.get("label"):
        lint_context.warn(f"Workflow step with ID {step_id} has no label.")

    # untyped parameters
    raw_tool_state = step.get("tool_state", {})
    if isinstance(raw_tool_state, str):
        try:
            tool_state = json.loads(raw_tool_state)
        except (json.JSONDecodeError, TypeError):
            tool_state = {}
    else:
        tool_state = raw_tool_state or {}

    if _check_json_for_untyped_params(tool_state):
        lint_context.warn(f"Workflow step with ID {step_id} specifies an untyped parameter as an input.")

    pjas = step.get("post_job_actions", {}) or {}
    if _check_json_for_untyped_params(pjas):
        lint_context.warn(f"Workflow step with ID {step_id} specifies an untyped parameter in the post-job actions.")


def _lint_step_best_practices_format2(lint_context, step, dict_key=None):
    """Lint best practices for a Format2 workflow step."""
    step_label = step.get("label") or dict_key
    step_id = step.get("id", step_label)

    # disconnected inputs — check declared inputs with no source or default
    step_type = step.get("type")
    if step_type not in SKIP_DISCONNECTED_CHECK_TYPES:
        step_in = step.get("in") or {}
        if isinstance(step_in, dict):
            for key, value in step_in.items():
                if isinstance(value, str):
                    continue  # string shorthand = always connected
                if isinstance(value, dict):
                    if not value.get("source") and "default" not in value:
                        lint_context.warn(f"Input {key} of workflow step {step_label or step_id} is disconnected.")
        elif isinstance(step_in, list):
            for key, value in walk_id_list_or_dict(step_in):
                if not value.get("source") and "default" not in value:
                    lint_context.warn(f"Input {key} of workflow step {step_label or step_id} is disconnected.")

    # missing metadata
    doc = step.get("doc")
    if not doc or (isinstance(doc, list) and not any(doc)):
        lint_context.warn(f"Workflow step {step_id} has no annotation.")
    if not step_label:
        lint_context.warn(f"Workflow step {step_id} has no label.")

    # untyped parameters
    tool_state = step.get("tool_state", {}) or {}
    if _check_json_for_untyped_params(tool_state):
        lint_context.warn(f"Workflow step {step_id} specifies an untyped parameter as an input.")

    out = step.get("out", {}) or {}
    if _check_json_for_untyped_params(out):
        lint_context.warn(f"Workflow step {step_id} specifies an untyped parameter in the post-job actions.")


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
    lint_func = lint_format2 if is_format2 else lint_ga
    lint_context = LintContext(training_topic=args.training_topic)
    lint_func(lint_context, workflow_dict, path=path)
    lint_pydantic_validation(lint_context, workflow_dict, format2=is_format2)
    if not args.skip_best_practices:
        best_practices_func = lint_best_practices_format2 if is_format2 else lint_best_practices_ga
        best_practices_func(lint_context, workflow_dict)
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
    "lint_best_practices_format2",
    "lint_best_practices_ga",
    "lint_pydantic_validation",
)
