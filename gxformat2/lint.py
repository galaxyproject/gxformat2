"""Workflow linting entry point - main script."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections.abc import Callable, Iterable
from typing import Any, NamedTuple
from urllib.parse import urlparse

from pydantic import ValidationError

from gxformat2.lint_rules import NativeStepKeyNotInteger, StepLabelNotUnique
from gxformat2.linting import LintContext
from gxformat2.markdown_parse import validate_galaxy_markdown
from gxformat2.normalized import (
    ensure_format2,
    ensure_native,
    NormalizedFormat2,
    NormalizedWorkflowStep,
    resolve_source_reference,
)
from gxformat2.normalized._conversion import (
    format2_input_step_type,
    native_input_label,
    native_input_to_format2_type,
    native_step_label,
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
# Galaxy's informal replacement parameter syntax (``WorkflowModule.get_informal_replacement_parameters``).
UNTYPED_PARAMETER_PATTERN = re.compile(r"\$\{(.+?)\}")
RENAME_ACTION = "RenameDatasetAction"
DATA_INPUT_STEP_TYPES = {NativeStepType.data_input, NativeStepType.data_collection_input}


class _ReplacementScope(NamedTuple):
    """What a step's ``${name}`` references can resolve against."""

    parameter_labels: set[str]
    data_labels: set[str]
    # source input label -> ``#{...}`` reference to the step input it connects to
    connected_inputs: dict[str, str]


def lint_ga(lint_context, nnw, raw_dict: dict | None = None, path=None):
    """Lint a native Galaxy workflow and populate the corresponding LintContext.

    Backward-compat: ``nnw`` may be a raw dict (legacy Planemo signature), in
    which case it is expanded to ``NormalizedNativeWorkflow`` internally.
    ``path`` is accepted for Planemo compatibility and currently ignored.
    """
    if isinstance(nnw, dict):
        if raw_dict is None:
            raw_dict = nnw
        nnw = ensure_native(nnw)
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

    _lint_duplicate_step_labels(
        lint_context,
        [
            (step.label, f"step {key}", _native_step_context(lint_context, key).child("label"))
            for key, step in nnw.steps.items()
        ],
    )

    for order_index_str, step in nnw.steps.items():
        step_context = _native_step_context(lint_context, order_index_str)
        if not order_index_str.isdigit():
            step_context.error(
                f"expected step_key to be integer not [{order_index_str}]",
                linter=NativeStepKeyNotInteger,
            )

        for workflow_output in step.workflow_outputs:
            found_outputs = True
            if not workflow_output.label:
                found_output_without_label = True

        if step.type_ == NativeStepType.subworkflow and step.subworkflow is not None:
            if not step.subworkflow.steps:
                lint_context.error("subworkflow is missing steps or steps are empty")
            else:
                lint_ga(step_context.child("subworkflow"), step.subworkflow)

        _lint_step_errors(lint_context, step.errors)
        _lint_tool_if_present(lint_context, step.tool_id)

    _lint_native_input_defaults(lint_context, nnw)
    _validate_report(lint_context, nnw.report)

    if not found_outputs:
        lint_context.warn(LINT_FAILED_NO_OUTPUTS)
    if found_output_without_label:
        lint_context.warn(LINT_FAILED_OUTPUT_NO_LABEL)

    _lint_training(lint_context, nnw.tags, nnw.annotation)


def lint_ga_path(lint_context, path):
    """Apply linting of native workflows to specified path."""
    workflow_dict = ordered_load_path(path)
    nnw = _try_build_nnw(lint_context, workflow_dict)
    if nnw is None:
        return None
    return lint_ga(lint_context, nnw, raw_dict=workflow_dict)


def lint_format2_path(lint_context, path):
    """Apply linting of Format2 workflows to specified path."""
    workflow_dict = ordered_load_path(path)
    nf2 = _try_build_nf2(lint_context, workflow_dict)
    if nf2 is None:
        return None
    return lint_format2(lint_context, nf2, raw_dict=workflow_dict)


def lint_format2(lint_context, nf2, raw_dict: dict | None = None, path=None):
    """Lint a Format 2 Galaxy workflow and populate the corresponding LintContext.

    Backward-compat: ``nf2`` may be a raw dict (legacy Planemo signature), in
    which case it is expanded to ``NormalizedFormat2`` internally. ``path`` is
    accepted for Planemo compatibility and currently ignored.
    """
    if isinstance(nf2, dict):
        if raw_dict is None:
            raw_dict = nf2
        nf2 = ensure_format2(nf2, expand=True)
    if raw_dict is not None:
        if "steps" not in raw_dict:
            lint_context.error("expected to find key [steps] but absent")
        if "class" not in raw_dict:
            lint_context.error("expected to find key [class] but absent")

    # Check the labels conversion will assign to the native steps.
    _lint_duplicate_step_labels(
        lint_context,
        [(native_input_label(inp, i), f"input {inp.id or i}", None) for i, inp in enumerate(nf2.inputs)]
        + [(native_step_label(step), f"step {step.id}", None) for step in nf2.steps],
    )

    for step in nf2.steps:
        _lint_step_errors(lint_context, step.errors)
        _lint_tool_if_present(lint_context, step.tool_id)
        if isinstance(step.run, NormalizedFormat2):
            if not step.run.steps:
                lint_context.error("subworkflow is missing steps or steps are empty")
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


def _native_step_context(lint_context: LintContext, step_key: str) -> LintContext:
    return lint_context.child("steps").child(step_key)


def _lint_duplicate_step_labels(
    lint_context: LintContext, labeled_steps: Iterable[tuple[str | None, str, LintContext | None]]
) -> None:
    """Error on step labels shared by more than one step, as Galaxy rejects these at import.

    ``labeled_steps`` holds ``(label, description, label_context)`` for each step
    of one workflow level (subworkflows have their own label namespace);
    ``label_context`` locates the label, or ``None`` to report at ``lint_context``.
    Empty labels are ignored, matching Galaxy.
    """
    steps_by_label: dict[str, list[tuple[str, LintContext | None]]] = {}
    for label, description, label_context in labeled_steps:
        if label:
            steps_by_label.setdefault(label, []).append((description, label_context))
    for label, steps in steps_by_label.items():
        if len(steps) < 2:
            continue
        (steps[1][1] or lint_context).error(
            f"Duplicated step label '{label}' ({', '.join(description for description, _ in steps)})",
            linter=StepLabelNotUnique,
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
        # type_ lives on concrete subclasses, not BaseInputParameter
        _lint_input_default(lint_context, inp.id, getattr(inp, "type_", None), inp.default)


def _lint_native_input_defaults(lint_context: LintContext, nnw: NormalizedNativeWorkflow):
    for key, step in nnw.steps.items():
        if step.type_ != NativeStepType.parameter_input:
            continue
        input_type = native_input_to_format2_type({"type": step.type_}, step.tool_state)
        _lint_input_default(
            _native_step_context(lint_context, key), step.label or key, input_type, step.tool_state.get("default")
        )


def _is_string(value) -> bool:
    return isinstance(value, str)


def _is_integer(value) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _is_number(value) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


class _DefaultCheck(NamedTuple):
    type_name: str
    expected: str
    expected_list: str
    is_valid: Callable[[Any], bool]


_STRING_DEFAULT = _DefaultCheck("string", "a string", "a string or a list of strings", _is_string)
_INTEGER_DEFAULT = _DefaultCheck("int", "an integer", "an integer or a list of integers", _is_integer)
_FLOAT_DEFAULT = _DefaultCheck("float", "a number", "a number or a list of numbers", _is_number)
_DEFAULT_CHECKS: dict[str, _DefaultCheck] = {
    GalaxyType.string: _STRING_DEFAULT,
    GalaxyType.text: _STRING_DEFAULT,
    GalaxyType.int: _INTEGER_DEFAULT,
    GalaxyType.integer: _INTEGER_DEFAULT,
    GalaxyType.float: _FLOAT_DEFAULT,
    GalaxyType.double: _FLOAT_DEFAULT,
    GalaxyType.color: _STRING_DEFAULT._replace(type_name="color"),
    GalaxyType.directory_uri: _STRING_DEFAULT._replace(type_name="directory_uri"),
}


def _lint_input_default(lint_context: LintContext, label, input_type, default):
    if default is None:
        return
    if isinstance(input_type, list):
        # Galaxy wraps a bare default for multiple parameter inputs.
        check = _DEFAULT_CHECKS.get(input_type[0]) if len(input_type) == 1 else None
        if check and not all(check.is_valid(value) for value in _as_list(default)):
            _invalid_default(lint_context, label, f"[{check.type_name}]", check.expected_list)
        return
    check = _DEFAULT_CHECKS.get(input_type)
    if check and not check.is_valid(default):
        _invalid_default(lint_context, label, check.type_name, check.expected)


def _invalid_default(lint_context: LintContext, label, input_type: str, expected: str):
    lint_context.error(
        f"Input default is of invalid type. Input {label} is {input_type}; its default must be {expected}."
    )


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


def _lint_workflow_top_level(lint_context, nf2: NormalizedFormat2):
    """Top-level (non step-level) best practices shared by native and Format2 paths."""
    doc = nf2.doc
    if not doc or not doc.strip():
        lint_context.warn("Workflow is not annotated.")

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

    if not nf2.license:
        lint_context.warn("Workflow does not specify a license.")


def lint_best_practices(lint_context, nf2: NormalizedFormat2):
    """Lint best practices for a Format2 workflow (top-level + format2 step-level)."""
    _lint_workflow_top_level(lint_context, nf2)
    input_types = {inp.id: format2_input_step_type(inp) for inp in nf2.inputs if inp.id}
    scope = _ReplacementScope(
        parameter_labels={label for label, t in input_types.items() if t == NativeStepType.parameter_input},
        data_labels={label for label, t in input_types.items() if t in DATA_INPUT_STEP_TYPES},
        connected_inputs={},
    )
    for step in nf2.steps:
        connected_inputs = {
            resolve_source_reference(source, scope.data_labels).step_label: _input_reference(step_input.id)
            for step_input in step.in_
            if step_input.id
            for source in _as_list(step_input.source)
        }
        _lint_step_best_practices(lint_context, step, scope._replace(connected_inputs=connected_inputs))


def _lint_step_best_practices(lint_context, step: NormalizedWorkflowStep, scope: _ReplacementScope):
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

    tool_state = step.state or step.tool_state
    if tool_state:
        if isinstance(tool_state, str):
            try:
                tool_state = json.loads(tool_state)
            except (json.JSONDecodeError, TypeError):
                tool_state = {}
        if isinstance(tool_state, dict):
            _lint_untyped_tool_state(lint_context, step_id, tool_state)

    # format2 step outputs carry the post-job actions as fields
    for out in step.out:
        for field, value in out.model_dump(exclude_none=True).items():
            if field != "id":
                _lint_untyped_pja(lint_context, step_id, out.id, field, value, field == "rename", scope)


SKIP_DISCONNECTED_CHECK_TYPES_NATIVE = {
    NativeStepType.data_input,
    NativeStepType.data_collection_input,
    NativeStepType.parameter_input,
    NativeStepType.pause,
}


def _lint_native_step_best_practices(lint_context, step: NormalizedNativeStep, scope: _ReplacementScope):
    """Native step best practice checks using native step fields (avoids format2 sentinel ids)."""
    step_id = step.label or step.annotation or step.id

    # disconnected inputs — compare declared inputs against input_connections
    if step.type_ not in SKIP_DISCONNECTED_CHECK_TYPES_NATIVE:
        input_connections = step.input_connections
        for input_def in step.inputs:
            if input_def.name and input_def.name not in input_connections:
                lint_context.warn(f"Input {input_def.name} of workflow step {step_id} is disconnected.")

    # missing metadata
    if not step.annotation:
        lint_context.warn(f"Workflow step {step_id} has no annotation.")
    if not step.label:
        lint_context.warn(f"Workflow step {step_id} has no label.")

    _lint_untyped_tool_state(lint_context, step_id, step.tool_state)

    for pja in step.post_job_actions.values():
        for argument, value in (pja.action_arguments or {}).items():
            is_rename = pja.action_type == RENAME_ACTION and argument == "newname"
            action = "rename" if is_rename else pja.action_type
            _lint_untyped_pja(lint_context, step_id, pja.output_name, action, value, is_rename, scope)


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

    Runs top-level checks on NormalizedFormat2 (for shared doc/creator/license
    interpretation) plus step-level checks on NormalizedNativeWorkflow so step
    messages reference native ids / labels / annotations rather than format2
    sentinels like ``_unlabeled_step_1``.
    """
    nf2 = _try_build_nf2(lint_context, workflow_dict)
    if nf2 is not None:
        _lint_workflow_top_level(lint_context, nf2)
    nnw = _try_build_nnw(lint_context, workflow_dict)
    if nnw is not None:
        labels = {step.id: step.label for step in nnw.steps.values() if step.label}
        scope = _ReplacementScope(
            parameter_labels={
                step.label for step in nnw.steps.values() if step.type_ == NativeStepType.parameter_input and step.label
            },
            data_labels={
                step.label for step in nnw.steps.values() if step.type_ in DATA_INPUT_STEP_TYPES and step.label
            },
            connected_inputs={},
        )
        for step in nnw.steps.values():
            connected_inputs = {
                labels[connection.id]: _input_reference(input_name)
                for input_name, connections in step.input_connections.items()
                for connection in connections
                if connection.id in labels
            }
            _lint_native_step_best_practices(lint_context, step, scope._replace(connected_inputs=connected_inputs))


def lint_best_practices_format2(lint_context, workflow_dict):
    """Lint best practices for a Format2 Galaxy workflow."""
    nf2 = _try_build_nf2(lint_context, workflow_dict)
    if nf2 is not None:
        lint_best_practices(lint_context, nf2)


def _untyped_parameter_names(value) -> list[str]:
    """Distinct ``${name}`` references anywhere in a JSON-like value, in order."""
    if isinstance(value, dict):
        value = list(value.values())
    if isinstance(value, list):
        return list(dict.fromkeys(name for item in value for name in _untyped_parameter_names(item)))
    if isinstance(value, str):
        return UNTYPED_PARAMETER_PATTERN.findall(value)
    return []


def _lint_untyped_tool_state(lint_context, step_id, tool_state):
    for name in _untyped_parameter_names(tool_state):
        lint_context.warn(
            f"Workflow step {step_id} specifies an untyped parameter as an input. ${{{name}}} is filled only by "
            "the expanded run form, never via the API; connect a workflow parameter input instead."
        )


def _as_list(value) -> list:
    if value is None:
        return []
    return value if isinstance(value, list) else [value]


def _input_reference(input_name: str) -> str:
    """Rename ``#{...}`` reference for a step input; Galaxy reads nested ``a|b`` as ``a.b``."""
    return input_name.replace("|", ".")


def _lint_untyped_pja(lint_context, step_id, output_name, action, value, is_rename, scope: _ReplacementScope):
    """Warn for ``${name}`` references Galaxy won't fill from a declared parameter input."""
    target = f"output {output_name}" if output_name else "all outputs"
    for name in _untyped_parameter_names(value):
        if not is_rename:
            detail = "stays literal; Galaxy substitutes parameters only in renames."
        elif name in scope.parameter_labels:
            continue
        elif name in scope.data_labels:
            input_reference = scope.connected_inputs.get(name, "input_name")
            detail = (
                "names a data input, but Galaxy fills ${...} only from parameter inputs; "
                f"use #{{{input_reference}}} for that dataset's name."
            )
        else:
            detail = (
                "is not a parameter input label, so Galaxy prompts for it at run time and leaves it literal via "
                f"the API; add a parameter input labelled {name}, or use #{{input_name}} for an input dataset's name."
            )
        lint_context.warn(
            f"Workflow step {step_id} specifies an untyped parameter in the post-job actions. "
            f"${{{name}}} in {action} of {target} {detail}"
        )


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

    # Best practices — dispatch by format; native path uses native step ids.
    if not args.skip_best_practices:
        if is_format2:
            lint_best_practices_format2(lint_context, workflow_dict)
        else:
            lint_best_practices_ga(lint_context, workflow_dict)

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
    "lint_best_practices",
    "lint_best_practices_format2",
    "lint_best_practices_ga",
    "lint_format2",
    "lint_ga",
    "lint_pydantic_validation",
    "main",
)
