"""CLI smoke tests for gxformat2.mermaid.

Behavioral coverage of workflow_to_mermaid lives in declarative YAML
(gxformat2/examples/expectations/mermaid.yml) and runs from
test_interop_tests.py — keep this file for things that aren't a pure
function of (workflow dict) -> result.
"""

import os
import tempfile

from gxformat2.mermaid import main, to_mermaid

from ._helpers import example_path

EXAMPLE_PATH = example_path("real-hacked-unicycler-assembly-extra-annotations.ga")


def test_cli_writes_mmd_raw():
    with tempfile.NamedTemporaryFile(suffix=".mmd", delete=False) as out:
        out_path = out.name
    try:
        main([EXAMPLE_PATH, out_path])
        with open(out_path) as f:
            content = f.read()
        assert content.startswith("graph LR\n")
        assert "```" not in content
    finally:
        os.unlink(out_path)


def test_cli_wraps_md_in_fence():
    with tempfile.NamedTemporaryFile(suffix=".md", delete=False) as out:
        out_path = out.name
    try:
        main([EXAMPLE_PATH, out_path])
        with open(out_path) as f:
            content = f.read()
        assert content.startswith("```mermaid\n")
        assert content.rstrip().endswith("```")
        assert "graph LR" in content
    finally:
        os.unlink(out_path)


def test_cli_stdout(capsys):
    main([EXAMPLE_PATH])
    captured = capsys.readouterr()
    assert captured.out.startswith("graph LR\n")


def test_cli_comments_flag(capsys):
    # Workflow without frame comments → flag is a no-op (no subgraph).
    main([EXAMPLE_PATH, "--comments"])
    captured = capsys.readouterr()
    assert captured.out.startswith("graph LR\n")


def test_to_mermaid_stdout_passthrough(capsys):
    to_mermaid(EXAMPLE_PATH)
    captured = capsys.readouterr()
    assert "graph LR" in captured.out
