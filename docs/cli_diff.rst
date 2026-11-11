gxwf-diff
=========

``gxwf-diff`` compares two Format 2 workflows, BEFORE and AFTER. Either one may
be a draft (``class: GalaxyWorkflowDraft``). It reports:

- workflow inputs, outputs and steps that were added or removed
- input field changes and output ``outputSource`` changes
- per-step changes to ``label``, ``type``, ``tool_id``, ``tool_version``,
  ``when``, a linked ``run`` reference, ``state`` and connections
- AFTER inputs that feed no step

Steps are matched by step key. That is the dict key, or for list-form steps the
label, then the id, then the index id. Unlabeled list-form steps are matched by
position, and the diff warns when it does this. ``_plan_*`` fields never count
as changes. They are reported on each added, removed and changed step, so a
step can be traced back to its source. Only the top level is compared.

``--json`` prints the ``gxformat2.diff.WorkflowDiff`` model. The declarative
cases in ``gxformat2/examples/expectations/diff.yml`` pin its shape. The exit
status is 0 unless ``--exit-code`` is given, in which case it is 1 when the
workflows differ.

.. argparse::
   :module: gxformat2.diff
   :func: _parser
   :prog: gxwf-diff
