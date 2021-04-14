============
Contributing
============

Please note that this project is released with a `Contributor Code of Conduct 
<https://gxformat2.readthedocs.org/en/latest/conduct.html>`__. By participating
in this project you agree to abide by its terms.

Contributions are welcome, and they are greatly appreciated! Every
little bit helps, and credit will always be given.

You can contribute in many ways:

Types of Contributions
----------------------

Report Bugs
~~~~~~~~~~~

Report bugs at https://github.com/galaxyproject/gxformat2/issues.

If you are reporting a bug, please include:

* Your operating system name and version, versions of other relevant software 
  such as Galaxy or Planemo.
* Links to relevant tools and workflows.
* Any details about your local setup that might be helpful in troubleshooting.
* Detailed steps to reproduce the bug.

Fix Bugs
~~~~~~~~

Look through the GitHub issues for bugs. Anything tagged with "bug"
is open to whoever wants to implement it.

Implement Features
~~~~~~~~~~~~~~~~~~

Look through the GitHub issues for features. Anything tagged with
"enhancement" is open to whoever wants to implement it.

Write Documentation
~~~~~~~~~~~~~~~~~~~

gxformat2 could always use more documentation, whether as part of the
official gxformat2 docs, in docstrings, or even on the web in blog posts,
articles, and such.

Submit Feedback
~~~~~~~~~~~~~~~

The best way to send feedback is to file an issue at https://github.com/galaxyproject/gxformat2/issues.

If you are proposing a feature:

* Explain in detail how it would work.
* Keep the scope as narrow as possible, to make it easier to implement.
* This will hopefully become a community-driven project and contributions
  are welcome :)

Get Started!
------------

Ready to contribute? Here's how to set up `gxformat` for local development.

1. Fork the `gxformat2` repo on GitHub.
2. Clone your fork locally::

    $ git clone git@github.com:your_name_here/gxformat2.git

3. Install your local copy into a virtualenv. Assuming you have virtualenvwrapper installed, this is how you set up your fork for local development::

    $ make setup-venv

4. Create a branch for local development::

    $ git checkout -b name-of-your-bugfix-or-feature

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass ``flake8``
   and the tests
   
   ::

       $ tox -e lint
       $ tox -e mypy
       $ tox -e unit

6. Commit your changes and push your branch to GitHub::

    $ git add .
    $ git commit -m "Your detailed description of your changes."
    $ git push origin name-of-your-bugfix-or-feature

7. Submit a pull request through the GitHub website.

Pull Request Guidelines
-----------------------

Before you submit a pull request, check that it meets these guidelines:

1. If the pull request adds functionality, the docs should be updated. Put
   your new functionality into a function with a docstring.
2. The pull request should work for Python >=3.6. Check CI results on pull
   request and make sure that the tests pass for all supported Python versions.

Tox_
~~~~~~~~~~~

Tox_ is a tool to automate testing across different Python versions. The
``tox`` executable can be supplied with a ``-e`` argument to specify a
testing environment. gxformat2 defines the following environments:

``py37-lint``
    Lint the gxformat2 code using Python 3.7.

``py37-lint_docstrings``
    Lint the project Python docstrings.

``py36-unit``
    Run the unit tests with Python 3.6.

.. _Tox: https://tox.readthedocs.org/en/latest/

