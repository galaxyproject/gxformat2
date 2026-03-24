"""Tests for connection resolution during normalization."""

from gxformat2.to_format2 import ensure_format2
from gxformat2.yaml import ordered_load


def test_link_in_state_resolved():
    """$link in state → ConnectedValue in state + source in in_."""
    nf2 = ensure_format2(ordered_load("""
class: GalaxyWorkflow
inputs:
  moo: data
steps:
  s1:
    tool_id: cat1
    state:
      input:
        $link: moo/cow
"""))
    step = nf2.steps[0]
    assert step.state["input"] == {"__class__": "ConnectedValue"}
    sources = {si.id: si.source for si in step.in_}
    assert sources["input"] == "moo/cow"


def test_link_array_in_state_resolved():
    """Multiple $link in array → ConnectedValue markers + sources in in_."""
    nf2 = ensure_format2(ordered_load("""
class: GalaxyWorkflow
inputs:
  moo: data
steps:
  s1:
    tool_id: cat1
    state:
      input:
        - $link: moo/cow
        - $link: moo/cow2
"""))
    step = nf2.steps[0]
    assert step.state["input"] == [None, None]
    sources = {si.id: si.source for si in step.in_}
    assert "moo/cow" in sources["input"]
    assert "moo/cow2" in sources["input"]


def test_in_source_preserved():
    """Regular in sources pass through to in_."""
    nf2 = ensure_format2(ordered_load("""
class: GalaxyWorkflow
inputs:
  foo: data
steps:
  s1:
    tool_id: cat1
    in:
      bar: foo/moo
"""))
    step = nf2.steps[0]
    sources = {si.id: si.source for si in step.in_}
    assert sources["bar"] == "foo/moo"


def test_in_default_preserved():
    """in entries with default (no source) preserved."""
    nf2 = ensure_format2(ordered_load("""
class: GalaxyWorkflow
inputs: {}
steps:
  s1:
    tool_id: cat1
    in:
      bar:
        default: 7
"""))
    step = nf2.steps[0]
    defaults = {si.id: si.default for si in step.in_}
    assert defaults["bar"] == 7
