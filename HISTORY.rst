.. :changelog:

History
-------

.. to_doc

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
