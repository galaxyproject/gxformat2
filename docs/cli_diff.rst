gxwf-diff
=========

``gxwf-diff`` compares two Format 2 workflows, BEFORE and AFTER. Either one may
be a draft (``class: GalaxyWorkflowDraft``). It reports:

- workflow inputs, outputs and steps that were added or removed
- input field changes and output ``outputSource`` changes
- per-step changes to ``label``, ``type``, ``tool_id``, ``tool_version``,
  ``when``, a linked ``run`` reference, ``state``, step input ``default``
  values, output actions (``rename``, ``hide``, ...) and connections
- AFTER inputs that feed no step

Steps are reported under their step key. That is the dict key, or for
list-form steps the label, then the id, then the index id. List-form steps with
the same ``id`` on both sides (unique on each side) are matched first and
reported under the AFTER key, so adding or changing a label is a ``label``
change, not a removed and an added step. A pair whose AFTER key is still another
unpaired BEFORE step's key is dropped. The remaining steps match on step key.
Unlabeled list-form steps with no ``id`` are matched by position, and the diff
warns when it does this. Each added or removed step carries its raw ``id``.

Inline subworkflows (an inline ``run`` on both sides of a matched step) are
diffed as well. Their steps, inputs and outputs appear in the same maps, with
every step key, input and output id and edge node prefixed by the parent's
AFTER step key and ``/``: a step ``first`` removed inside step ``nested`` is
``steps.removed["nested/first"]``. An added or removed subworkflow step is
reported as that one step, not its contents. ``unwired_inputs`` lists top-level
inputs only. A linked ``run`` (URL, path or ``@import``) is compared by
reference. A prefixed step key, input or output id that a slash-keyed one at
another level also uses raises ``ValueError``, changed or not.

``_plan_*`` fields never count as changes. They are reported on each added,
removed and changed step, so a step can be traced back to its source.

``--json`` prints the ``gxformat2.diff.WorkflowDiff`` model. The declarative
cases in ``gxformat2/examples/expectations/diff.yml`` pin its shape; key order
within its objects is not part of that shape. The exit
status is 0 unless ``--exit-code`` is given, in which case it is 1 when the
workflows differ.

.. argparse::
   :module: gxformat2.diff
   :func: _parser
   :prog: gxwf-diff
