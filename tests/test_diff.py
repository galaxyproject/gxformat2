"""CLI and text-rendering tests for gxformat2.diff.

Diff semantics live in declarative YAML (gxformat2/examples/expectations/diff.yml).
"""

import json

import pytest

from gxformat2.diff import diff_workflows, main, render_text
from gxformat2.examples import get_path, load

BASE = get_path("synthetic-diff-base.gxwf.yml")
REMOVED_STEP = get_path("synthetic-diff-removed-step.gxwf.yml")
DRAFT_BEFORE = get_path("synthetic-diff-draft-before.gxwf.yml")
DRAFT_AFTER = get_path("synthetic-diff-draft-after.gxwf.yml")


def test_cli_text_identical(capsys):
    assert main([BASE, BASE]) == 0
    assert capsys.readouterr().out == "No differences.\n"


def test_cli_text_removed_step(capsys):
    assert main([BASE, REMOVED_STEP]) == 0
    out = capsys.readouterr().out
    assert (
        "Step removed: trim (trim reads) [trimmer 1.0]\n    upstream: min_quality, reads\n    downstream: filter\n"
        in out
    )
    assert "    - trim/out_file1 -> filter/input\n    + reads -> filter/input\n" in out
    assert out.endswith("AFTER inputs feeding no step: min_quality\n")


def test_cli_json_matches_model(capsys):
    assert main(["--json", DRAFT_BEFORE, DRAFT_AFTER]) == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload == diff_workflows(DRAFT_BEFORE, DRAFT_AFTER).model_dump(mode="json")
    assert payload["has_changes"] is True
    assert list(payload["steps"]["removed"]) == ["chr_filter"]


@pytest.mark.parametrize("after,expected", [(BASE, 0), (REMOVED_STEP, 1)])
def test_cli_exit_code(after, expected, capsys):
    assert main(["--exit-code", BASE, after]) == expected


def test_render_text_lists_plan_fields_of_removed_draft_step():
    text = render_text(diff_workflows(load("synthetic-diff-draft-before.gxwf.yml"), DRAFT_AFTER))
    assert "Step removed: chr_filter (keep only requested chromosomes) [TODO TODO]" in text
    assert "    has _plan_state\n    has _plan_context" in text


def test_render_text_spells_out_unset_state_values():
    bare = get_path("synthetic-diff-explicit-false-bare.gxwf.yml")
    text = render_text(diff_workflows(bare, get_path("synthetic-diff-explicit-state.gxwf.yml")))
    assert "    state min_length: added null\n" in text
    assert '    state comment: added ""\n' in text
    assert "    state inclusive_filter: added []" in text


def test_native_workflow_rejected():
    with pytest.raises(ValueError, match="native"):
        diff_workflows(get_path("real-unicycler-assembly.ga"), BASE)


def test_render_text_names_nested_step_by_its_path():
    text = render_text(
        diff_workflows(
            get_path("synthetic-diff-inline-subworkflow.gxwf.yml"),
            get_path("synthetic-diff-inline-subworkflow-removed-step.gxwf.yml"),
        )
    )
    assert "Step removed: nested/first [cat1]\n    upstream: nested/inner_reads\n" in text


def test_nested_key_colliding_with_slash_keyed_step_rejected():
    before = load("synthetic-diff-inline-subworkflow.gxwf.yml")
    before["steps"]["nested/first"] = {"tool_id": "cat1", "in": {"input1": "reads"}}
    with pytest.raises(ValueError, match="nested/first"):
        diff_workflows(before, get_path("synthetic-diff-inline-subworkflow-removed-step.gxwf.yml"))


def test_nested_key_colliding_with_unchanged_slash_keyed_step_rejected():
    before = load("synthetic-diff-inline-subworkflow.gxwf.yml")
    after = load("synthetic-diff-inline-subworkflow-removed-step.gxwf.yml")
    for workflow in (before, after):
        workflow["steps"]["nested/first"] = {"tool_id": "cat1", "in": {"input1": "reads"}}
    with pytest.raises(ValueError, match="nested/first"):
        diff_workflows(before, after)


def test_nested_input_colliding_with_slash_keyed_input_rejected():
    before = load("synthetic-diff-inline-subworkflow.gxwf.yml")
    before["inputs"]["nested/inner_reads"] = "data"
    with pytest.raises(ValueError, match="nested/inner_reads"):
        diff_workflows(before, before)
