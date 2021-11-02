=============
 Development
=============


Getting the source code
=======================
The source code is maintained on GitHub. To check out the main branch:

.. code-block:: console

  $ git clone https://github.com/dataflake/Products.LDAPUserFolder.git

You can also browse the code online at
https://github.com/dataflake/Products.LDAPUserFolder


Bug tracker
===========
For bug reports, suggestions or questions please use the GitHub issue tracker at
https://github.com/dataflake/Products.LDAPUserFolder/issues.


Running the tests using  :mod:`zc.buildout`
===========================================
:mod:`Products.LDAPUserFolder` ships with a :mod:`zc.buildout` configuration
for setting up a development buildout. As prerequisite you need to create a
virtual envuronment first using :mod:`virtualenv`:

.. code-block:: console

  $ cd Products.LDAPUserFolder
  $ python3.7 -m virtualenv .
  $ bin/pip install -U pip wheel
  $ bin/pip install "setuptools<52" zc.buildout tox twine
  $ bin/buildout

Once the buildout has run, the unit tests can be run as follows:

.. code-block:: console

  $ bin/test

Code coverage and linting is done through the script at ``bin/tox``:

.. code-block:: console

  $ bin/tox -pall  # This runs all tests in parallel to save time

Calling it without any arguments will run the unit tests, code coverage
report and linting. You can see the tests configured for it with the ``-l``
switch:

.. code-block:: console

  $ bin/tox -l
  lint
  py35
  py36
  py37
  py38
  py39
  coverage

``py37`` represents the unit tests, run under Python 3.7. You can run each
of these by themselves with the ``-e`` switch:

.. code-block:: console

  $ bin/tox -e coverage

Coverage report output is as text to the terminal, and as HTML files under
``parts/coverage/``.

The result of linting checks are shown as text on the terminal as well as
HTML files under ``parts/flake8/``


Building the documentation using :mod:`zc.buildout`
===================================================
The :mod:`Products.LDAPUserFolder` buildout installs the Sphinx 
scripts required to build the documentation, including testing 
its code snippets:

.. code-block:: console

    $ cd docs
    $ make html
    ...
    build succeeded.

    Build finished. The HTML pages are in _build/html.


Making a release
================
These instructions assume that you have a development sandbox set 
up using :mod:`zc.buildout` as the scripts used here are generated 
by the buildout.

.. code-block:: console

  $ bin/buildout -N
  $ bin/buildout setup setup.py sdist bdist_wheel
  $ bin/twine upload dist/Products.LDAPUserFolder-<VERSION>*

The first ``bin/buildout`` step will make sure the correct package information 
is used.
