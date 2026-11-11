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


def test_native_workflow_rejected():
    with pytest.raises(ValueError, match="native"):
        diff_workflows(get_path("real-unicycler-assembly.ga"), BASE)
