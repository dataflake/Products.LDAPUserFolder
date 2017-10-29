=============
 Development
=============


Getting the source code
=======================
The source code is maintained on GitHub. To check out the trunk:

.. code-block:: sh

  $ git clone https://github.com/dataflake/Products.LDAPUserFolder.git

You can also browse the code online at
https://github.com/dataflake/Products.LDAPUserFolder


Bug tracker
===========
For bug reports, suggestions or questions please use the 
GitHub issue tracker at
https://github.com/dataflake/Products.LDAPUserFolder/issues.


Running the tests using  :mod:`zc.buildout`
===========================================
:mod:`Products.LDAPUserFolder` ships with its own :file:`buildout.cfg` file and
:file:`bootstrap.py` for setting up a development buildout:

.. code-block:: sh

  $ python bootstrap.py
  ...
  Generated script '.../bin/buildout'
  $ bin/buildout
  ...

Once you have a buildout, the tests can be run as follows:

.. code-block:: sh

   $ bin/test 
   Running tests at level 1
   Running zope.testrunner.layer.UnitTests tests:
     Set up zope.testrunner.layer.UnitTests in 0.000 seconds.
     Running:
   ..............................................................
     Ran 62 tests with 0 failures and 0 errors in 0.043 seconds.
   Tearing down left over layers:
     Tear down zope.testrunner.layer.UnitTests in 0.000 seconds.


Building the documentation using :mod:`zc.buildout`
===================================================
The :mod:`Products.LDAPUserFolder` buildout installs the Sphinx 
scripts required to build the documentation, including testing 
its code snippets:

.. code-block:: sh

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

.. code-block:: sh

  $ bin/buildout -o
  $ python setup.py sdist bdist_wheel upload --sign

The ``bin/buildout`` step will make sure the correct package information 
is used.
