"""Workflow linting entry point - main script."""
import os
import sys

from gxformat2._yaml import ordered_load
from gxformat2.linting import LintContext

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
        lint_context.error("expected value [{value}] with key [{key}] to be of class {clazz}", key=key, value=value, clazz=has_class)
    if has_value is not None and value != has_value:
        lint_context.error("expected value [{value}] with key [{key}] to be {expected_value}", key=key, value=value, expected_value=has_value)
    return value


def _lint_step_errors(lint_context, step):
    step_errors = step.get("errors")
    if step_errors is not None:
        lint_context.warn("tool step contains error indicated during Galaxy export - %s" % step_errors)


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

    report_dict = ensure_key_if_present(lint_context, workflow_dict, "report", default=None, has_class=dict)
    if report_dict is not None:
        ensure_key(lint_context, report_dict, "markdown", has_class=str)

    if not found_outputs:
        lint_context.warn(LINT_FAILED_NO_OUTPUTS)

    if found_output_without_label:
        lint_context.warn(LINT_FAILED_OUTPUT_NO_LABEL)


def lint_format2(lint_context, workflow_dict, path=None):
    """Lint a Format 2 Galaxy workflow and populate the corresponding LintContext."""
    from gxformat2.schema.v19_09 import load_document
    from schema_salad.exceptions import SchemaSaladException
    try:
        load_document("file://" + os.path.normpath(path))
    except SchemaSaladException as e:
        lint_context.error("Validation failed " + str(e))

    steps = ensure_key_if_present(lint_context, workflow_dict, 'steps', default={}, has_class=dict)
    for key, step in steps.items():
        _lint_step_errors(lint_context, step)


def main(argv):
    """Script entry point for linting workflows."""
    path = argv[1]
    with open(path, "r") as f:
        try:
            workflow_dict = ordered_load(f)
        except Exception:
            return EXIT_CODE_FILE_PARSE_FAILED
    workflow_class = workflow_dict.get("class")
    lint_func = lint_format2 if workflow_class == "GalaxyWorkflow" else lint_ga
    lint_context = LintContext()
    lint_func(lint_context, workflow_dict, path=path)
    lint_context.print_messages()
    if lint_context.found_errors:
        return EXIT_CODE_FORMAT_ERROR
    elif lint_context.found_warns:
        return EXIT_CODE_LINT_FAILED
    else:
        return EXIT_CODE_SUCCESS


if __name__ == "__main__":
    sys.exit(main(sys.argv))


__all__ = ('main', 'lint_format2', 'lint_ga')
