.. :changelog:

History
-------

.. to_doc

---------------------
0.26.0.dev0
---------------------
* Restore Planemo-compatible ``lint_format2`` / ``lint_ga`` signatures: accept a
  raw ``dict`` in the second position (normalized internally) and a trailing
  ``path=`` keyword (currently ignored). `Issue 187`_
* Make ``LintContext`` message formatting compatible with
  ``galaxy.tool_util.lint`` by using ``%``-style substitution for positional
  arguments, falling back to ``.format()``. `Issue 187`_
* Restore ``gxformat2.interface`` as a deprecated compatibility shim for
  Planemo. ``bioblend`` is now an optional dependency (install
  ``gxformat2[bioblend]``) and is imported lazily inside
  ``BioBlendImporterGalaxyInterface``. `Issue 187`_

.. _Issue 187: https://github.com/galaxyproject/gxformat2/issues/187

---------------------
0.25.0 (2026-04-16)
---------------------
* Schema Salad Modeling for Native Workflows (thanks to `@jmchilton`_). `Pull Request 153`_
* Allow Pluggable State Handling During Conversion in Both Directions (thanks to `@jmchilton`_). `Pull Request 154`_
* Add deploy GitHub workflow (thanks to `@nsoranzo`_). `Pull Request 160`_
* Full GalaxyUserTool support in workflows (thanks to `@jmchilton`_). `Pull Request 158`_
* Add auto-generated CLI docs via sphinx-argparse (thanks to `@jmchilton`_). `Pull Request 156`_
* Migrate Best Practice Linting from Planemo, Rich Fixture Tracking and Docs (thanks to `@jmchilton`_). `Pull Request 159`_
* Modernize linting and dev tools in various small ways (thanks to `@jmchilton`_). `Pull Request 163`_
* Add pre-commit config sample based on Galaxy's setup (thanks to `@jmchilton`_). `Pull Request 166`_
* From foundation to finish: typed models across the library (thanks to `@jmchilton`_). `Pull Request 164`_
* Bump actions/upload-artifact from 6 to 7 (thanks to `@dependabot[bot]`_). `Pull Request 168`_
* Bump codecov/codecov-action from 5 to 6 (thanks to `@dependabot[bot]`_). `Pull Request 169`_
* Migrate a Bunch of Python Testing to be More Declarative/Interoparble (thanks to `@jmchilton`_). `Pull Request 173`_
* Bump actions/download-artifact from 7 to 8 (thanks to `@dependabot[bot]`_). `Pull Request 170`_
* Bump pygments from 2.19.2 to 2.20.0 (thanks to `@dependabot[bot]`_). `Pull Request 171`_
* Extract declarative test harness into gxformat2.testing, rename test file (thanks to `@jmchilton`_). `Pull Request 174`_
* Modernize Doc Styling (thanks to `@jmchilton`_). `Pull Request 176`_
* CLI Tweaks (thanks to `@jmchilton`_). `Pull Request 175`_
* More declarative testing (thanks to `@jmchilton`_). `Pull Request 179`_
* Mermaid docs (thanks to `@jmchilton`_). `Pull Request 177`_
* Improve rendering of schema files post Galaxy-Modern-Style refactor (thanks to `@jmchilton`_). `Pull Request 182`_
* Add sphinxcontrib-mermaid to docs requirements (thanks to `@jmchilton`_). `Pull Request 183`_
* Add strict_structure support to normalized models and conversion (thanks to `@jmchilton`_). `Pull Request 181`_
* Split WorkflowInputParameter into type-specific discriminated union (thanks to `@jmchilton`_). `Pull Request 180`_
* Fix merge issue (thanks to `@jmchilton`_). `Pull Request 184`_
* Enforce Literal types for native workflow marker fields (thanks to `@jmchilton`_). `Pull Request 185`_
* Linting Improvements (thanks to `@jmchilton`_). `Pull Request 188`_
* Use native step ids in native best-practice lint messages (thanks to `@jmchilton`_). `Pull Request 189`_

    

---------------------
0.24.0 (2026-03-21)
---------------------
* Migrate from ``setup.py`` to ``pyproject.toml`` (thanks to `@nsoranzo`_). `Pull Request 142`_
* Use _unlabeled_input_ sentinel to preserve label=None on round-trip (thanks to `@jmchilton`_). `Pull Request 144`_
* Fix `/` in step labels breaking source reference parsing (thanks to `@jmchilton`_). `Pull Request 148`_
* Add pick_value and comments to Format2 schema (thanks to `@jmchilton`_). `Pull Request 147`_
* Fix unlabeled tool steps getting dangling numeric source refs after roundtrip (thanks to `@jmchilton`_). `Pull Request 149`_
* Add uv dependency groups for lint, mypy, test; update dev docs (thanks to `@jmchilton`_). `Pull Request 150`_
* More dev process updates - including history generation stuff, better uv usage, etc (thanks to `@jmchilton`_). `Pull Request 152`_

    

---------------------
0.23.0 (2026-03-18)
---------------------
* Implement bidirectional workflow comment conversion (thanks to
  `@jmchilton`_). `Pull Request 137`_
* Support unencoded tool_state in native workflows (thanks to
  `@jmchilton`_). `Pull Request 138`_
* Add pick_value as valid step type with PJA support (thanks to
  `@jmchilton`_). `Pull Request 136`_
* Fix URI generation on Windows when linting (thanks to
  `@loichuder`_). `Pull Request 134`_
* Add to-native and to-format2 commands to README (thanks to
  `@loichuder`_). `Pull Request 133`_
* Lint code with black and ruff (thanks to `@nsoranzo`_). `Pull
  Request 131`_



---------------------
0.22.0 (2026-02-20)
---------------------
* Support URL and TRS URL references in subworkflow run: fields (thanks to
  `@mvdbeek`_). `Pull Request 130`_
* Add ``--compact`` flag (thanks to `@mvdbeek`_). `Pull Request 112`_
* Add support for Python 3.14 (thanks to `@nsoranzo`_). `Pull Request 117`_
* Drop unmaintained codecov.io dependency (thanks to `@nsoranzo`_). `Pull
  Request 125`_
* Enable dependabot version updates for GitHub actions (thanks to
  `@nsoranzo`_). `Pull Request 116`_

---------------------
0.21.0 (2025-09-19)
---------------------
* Fix gxformat2 to .ga conversion if ``hide: true`` specified on output (thanks to
  `@mvdbeek`_). `Pull Request 106`_
* Upgrade schema-salad version and auto-generated documents (thanks to
  `@mvdbeek`_). `Pull Request 107`_
* GalaxyWorkflow: improve parsing speed & codegen (thanks to `@mr-c`_). `Pull
  Request 108`_
* Fix docs building (thanks to `@nsoranzo`_). `Pull Request 109`_
* Add myst-parser to docs requirements (thanks to `@nsoranzo`_). `Pull Request
  111`_
* Rebuild schema, bump up minimum Python version to 3.9 (thanks to
  `@mvdbeek`_). `Pull Request 113`_
* Support for sample sheets and records  (thanks to `@jmchilton`_). `Pull
  Request 114`_

---------------------
0.20.0 (2024-08-23)
---------------------
* Arrays of workflow input parameters (thanks to `@mvdbeek`_). `Pull Request
  100`_
* Design goals (thanks to `@jmchilton`_). `Pull Request 97`_

---------------------
0.19.0 (2024-07-23)
---------------------
* Sync markdown_parse with Galaxy (thanks to `@mvdbeek`_). `Pull Request 99`_
* More helpers for reasoning about gxformat2 steps (thanks to `@jmchilton`_).
  `Pull Request 98`_
* Add abstraction for popping connection dictionary to model (thanks to
  `@jmchilton`_). `Pull Request 96`_
* Add now mandatory readthedocs config files (thanks to `@nsoranzo`_). `Pull
  Request 94`_
* Use `ConnectedValue` for connected values (thanks to `@mvdbeek`_). `Pull
  Request 95`_
* Refresh codegen using schema-salad 8.4.20230808163024 (thanks to `@mr-c`_).
  `Pull Request 92`_
* Update label comment (thanks to `@mvdbeek`_). `Pull Request 90`_

---------------------
0.18.0 (2023-05-12)
---------------------
* Fix input conversion if input has no label by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/89

---------------------
0.17.0 (2023-01-06)
---------------------

* Enable "when" for workflow steps by @mr-c in https://github.com/galaxyproject/gxformat2/pull/74
* When fixes by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/86

---------------------
0.16.0 (2022-09-20)
---------------------

* Add dev ``when`` on steps to backend (don't expose in schema yet). by @jmchilton in https://github.com/galaxyproject/gxformat2/pull/48
* Update project plumbing to allow dev release. by @jmchilton in https://github.com/galaxyproject/gxformat2/pull/49
* Drop support for Python 3.5, add 3.9 by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/52
* Relicense under the MIT license by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/58
* Format2: Add `label` attribute to `WorkflowInputParameter` and `WorkflowOutputParameter` by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/56
* Misc fixes and refactorings by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/55
* Convert Format2 workflow `label` to native `name` by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/54
* test_abstract_export: use different names for the different outputs by @simleo in https://github.com/galaxyproject/gxformat2/pull/57
* Fix 2 typos by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/62
* Propagate `doc` field to abstract CWL format by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/65
* Linting fixes by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/64
* Maintain collection_type if present by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/68
* Fix schema doc build by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/69
* Lint and deprecation fixes by @nsoranzo in https://github.com/galaxyproject/gxformat2/pull/70
* Run java codegenerator by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/71
* Run maven tests on pull_request by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/72
* fix schema-salad pycodegen by @mr-c in https://github.com/galaxyproject/gxformat2/pull/76
* Add workflow default file support by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/79
* Add typescript implementation by @mr-c in https://github.com/galaxyproject/gxformat2/pull/75
* Fix cytoscape HTML exports from dist package. by @jmchilton in https://github.com/galaxyproject/gxformat2/pull/82
* Add missing elements to schema, fix change_datatype conversion, CSS by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/83
* Support lists as data inputs by @mvdbeek in https://github.com/galaxyproject/gxformat2/pull/84


---------------------
0.15.0 (2020-08-12)
---------------------

* Lint types of default values.
* Fix bugs in schema related to differing type names between Galaxy and CWL.
* Generate cwl v1.2 instead of cwl v1.2.0-dev5 release now that it has been released.
* More testing of linting and CWL 1.2 export.

---------------------
0.14.0 (2020-08-11)
---------------------

* Bug fix where native export had explicit outputs declaration still in it (wouldn't break anything, but
  was deceptive).
* Fixes for experimental CWL 1.2 abstract export.
* Improve script structures and documentation.
* Improve code structure - add more types, make more things immutable, mention mutability in docstrings.

---------------------
0.13.1 (2020-08-03)
---------------------

* Improve package structure - publish fixed sphinx docs, fix readme badges, add mypy typing support.

---------------------
0.13.0 (2020-07-30)
---------------------

* Add experimental export to CWL 1.2 using new abstract Operation classes.

---------------------
0.12.0 (2020-07-27)
---------------------

* Drop support for Python 2 - to support next bullet.
* Update schema parser for recent changes to schema salad.

---------------------
0.11.4 (2020-07-27)
---------------------

* Added abstraction for uniform access to workflow outputs across formats.

---------------------
0.11.3 (2020-07-23)
---------------------

* Bug fixes for exporting newer input concepts from native to Format 2.
* Added abstraction for uniform access to workflow inputs across formats.

---------------------
0.11.2 (2020-07-22)
---------------------

* Rework cytoscape and helpers for reuse from Planemo.
* Rev markdown validator for and from latest Galaxy changes.

---------------------
0.11.1 (2020-02-25)
---------------------

* Bug fix for gxwf-lint invocation from setup.py installed script.

---------------------
0.11.0 (2020-02-25)
---------------------

* Validate Galaxy Markdown in workflow reports as part of linting.
* Improved null handling in native ga workflow linting.
* Enhancements to workflow linting from Python. Lint for lack of documentation,
  tools using the test toolshed, and implement special linting for training
  material workflows to ensure a tag matches the workflow topic.
* Add gxwf-viz script that produces a cytoscape visualization of a workflow.

---------------------
0.10.1 (2019-12-07)
---------------------

* Bug fix to handle outputs without labels in Format 2 - they
  don't validate per se but they are important for testing in the
  Galaxy framework.

---------------------
0.10.0 (2019-12-06)
---------------------

* Implement scheam, validation, linting (for Format 2 and .ga).
* Handle new reports field in Galaxy 19.09 workflows.
* Numerous fixes for conversiion to and from native workflows.
* Numerous new test cases.
* Implement Java project for valiating and linting both kinds of workflows.

---------------------
0.9.0 (2019-07-08)
---------------------

* Implement default values in gxformat2.

---------------------
0.8.4 (2019-06-24)
---------------------

* Fix output IDs of 0.

---------------------
0.8.3 (2019-05-23)
---------------------

* Implement set_columns PJA.

---------------------
0.8.2 (2019-03-16)
---------------------

* Allow another API return option for experimental tool creation API.

---------------------
0.8.1 (2019-03-11)
---------------------

* Implement change datatype PJA.

---------------------
0.8.0 (2018-11-01)
---------------------

* Implement experimental CWL-style step defaults (see Galaxy PR #6850).

---------------------
0.7.1 (2018-10-09)
---------------------

* Various small fixes for changes in 0.7.1.

---------------------
0.7.0 (2018-10-08)
---------------------

* Add some basic test cases.
* Allow ID-map style listing of steps.
* Ordered load (in addition to existing dump functionality) or ordering of steps in ID-map style variant works.
* Allow CWL-style $graph defs that can define multiple workflows in a single file.
* Initial work on de-duplicating subworkflow definitions on import.
* Fix position handling while exporting workflow.

---------------------
0.6.1 (2018-10-01)
---------------------

* Fix export of non-data parameters and implicit workflow connections.

---------------------
0.6.0 (2018-10-01)
---------------------

* Various fixes, allow id map style workflow input definitions.

---------------------
0.5.0 (2018-10-01)
---------------------

* More fixes for PJA, add the ``doc`` keyword to format 2 workflows to match CWL workflows. Map to and from native Galaxy workflows as annotations.

---------------------
0.4.0 (2018-10-01)
---------------------

* Fixes for exporting PJA when exporting workflows from native .ga to format 2.

---------------------
0.3.2 (2018-10-01)
---------------------

* Fixes for exporting workflow outputs from native .ga to format 2, support for modern map style output definitions like CWL 1.0.

---------------------
0.3.1 (2018-10-01)
---------------------

* Fixes for exporting subworkflows from native .ga to format 2.

---------------------
0.3.0 (2018-09-30)
---------------------

* More cwl style inputs, initial work on conversion from native workflows, various small fixes and tweaks.

---------------------
0.2.0 (2018-02-21)
---------------------

* Bring in latest Galaxy updates - Python 3 fixes, safe YAML usage, and more PJA implemented.

---------------------
0.1.1 (2016-08-15)
---------------------

* Fix one Python 3 incompatibility.

---------------------
0.1.0 (2016-05-02)
---------------------

* Initial version - code from Galaxy's test framework with changes
  based on planemo testing.

.. github_links
.. _Pull Request 153: https://github.com/galaxyproject/gxformat2/pull/153
.. _Pull Request 154: https://github.com/galaxyproject/gxformat2/pull/154
.. _Pull Request 160: https://github.com/galaxyproject/gxformat2/pull/160
.. _Pull Request 158: https://github.com/galaxyproject/gxformat2/pull/158
.. _Pull Request 156: https://github.com/galaxyproject/gxformat2/pull/156
.. _Pull Request 159: https://github.com/galaxyproject/gxformat2/pull/159
.. _Pull Request 163: https://github.com/galaxyproject/gxformat2/pull/163
.. _Pull Request 166: https://github.com/galaxyproject/gxformat2/pull/166
.. _Pull Request 164: https://github.com/galaxyproject/gxformat2/pull/164
.. _Pull Request 168: https://github.com/galaxyproject/gxformat2/pull/168
.. _Pull Request 169: https://github.com/galaxyproject/gxformat2/pull/169
.. _Pull Request 173: https://github.com/galaxyproject/gxformat2/pull/173
.. _Pull Request 170: https://github.com/galaxyproject/gxformat2/pull/170
.. _Pull Request 171: https://github.com/galaxyproject/gxformat2/pull/171
.. _Pull Request 174: https://github.com/galaxyproject/gxformat2/pull/174
.. _Pull Request 176: https://github.com/galaxyproject/gxformat2/pull/176
.. _Pull Request 175: https://github.com/galaxyproject/gxformat2/pull/175
.. _Pull Request 179: https://github.com/galaxyproject/gxformat2/pull/179
.. _Pull Request 177: https://github.com/galaxyproject/gxformat2/pull/177
.. _Pull Request 182: https://github.com/galaxyproject/gxformat2/pull/182
.. _Pull Request 183: https://github.com/galaxyproject/gxformat2/pull/183
.. _Pull Request 181: https://github.com/galaxyproject/gxformat2/pull/181
.. _Pull Request 180: https://github.com/galaxyproject/gxformat2/pull/180
.. _Pull Request 184: https://github.com/galaxyproject/gxformat2/pull/184
.. _Pull Request 185: https://github.com/galaxyproject/gxformat2/pull/185
.. _Pull Request 188: https://github.com/galaxyproject/gxformat2/pull/188
.. _Pull Request 189: https://github.com/galaxyproject/gxformat2/pull/189
.. _Pull Request 142: https://github.com/galaxyproject/gxformat2/pull/142
.. _Pull Request 144: https://github.com/galaxyproject/gxformat2/pull/144
.. _Pull Request 148: https://github.com/galaxyproject/gxformat2/pull/148
.. _Pull Request 147: https://github.com/galaxyproject/gxformat2/pull/147
.. _Pull Request 149: https://github.com/galaxyproject/gxformat2/pull/149
.. _Pull Request 150: https://github.com/galaxyproject/gxformat2/pull/150
.. _Pull Request 152: https://github.com/galaxyproject/gxformat2/pull/152
.. _Pull Request 137: https://github.com/galaxyproject/gxformat2/pull/137
.. _Pull Request 138: https://github.com/galaxyproject/gxformat2/pull/138
.. _Pull Request 136: https://github.com/galaxyproject/gxformat2/pull/136
.. _Pull Request 134: https://github.com/galaxyproject/gxformat2/pull/134
.. _Pull Request 133: https://github.com/galaxyproject/gxformat2/pull/133
.. _Pull Request 131: https://github.com/galaxyproject/gxformat2/pull/131
.. _Pull Request 130: https://github.com/galaxyproject/gxformat2/pull/130
.. _Pull Request 112: https://github.com/galaxyproject/gxformat2/pull/112
.. _Pull Request 117: https://github.com/galaxyproject/gxformat2/pull/117
.. _Pull Request 125: https://github.com/galaxyproject/gxformat2/pull/125
.. _Pull Request 116: https://github.com/galaxyproject/gxformat2/pull/116
.. _Pull Request 106: https://github.com/galaxyproject/gxformat2/pull/106
.. _Pull Request 107: https://github.com/galaxyproject/gxformat2/pull/107
.. _Pull Request 108: https://github.com/galaxyproject/gxformat2/pull/108
.. _Pull Request 109: https://github.com/galaxyproject/gxformat2/pull/109
.. _Pull Request 111: https://github.com/galaxyproject/gxformat2/pull/111
.. _Pull Request 113: https://github.com/galaxyproject/gxformat2/pull/113
.. _Pull Request 114: https://github.com/galaxyproject/gxformat2/pull/114
.. _Pull Request 100: https://github.com/galaxyproject/gxformat2/pull/100
.. _Pull Request 97: https://github.com/galaxyproject/gxformat2/pull/97
.. _Pull Request 99: https://github.com/galaxyproject/gxformat2/pull/99
.. _Pull Request 98: https://github.com/galaxyproject/gxformat2/pull/98
.. _Pull Request 96: https://github.com/galaxyproject/gxformat2/pull/96
.. _Pull Request 94: https://github.com/galaxyproject/gxformat2/pull/94
.. _Pull Request 95: https://github.com/galaxyproject/gxformat2/pull/95
.. _Pull Request 92: https://github.com/galaxyproject/gxformat2/pull/92
.. _Pull Request 90: https://github.com/galaxyproject/gxformat2/pull/90
.. _@mvdbeek: https://github.com/mvdbeek
.. _@mr-c: https://github.com/mr-c
.. _@nsoranzo: https://github.com/nsoranzo
.. _@jmchilton: https://github.com/jmchilton
.. _@loichuder: https://github.com/loichuder
.. _@simleo: https://github.com/simleo
