Development
===========

Bug tracker
-----------
For bug reports, suggestions or questions please use the
GitHub issue tracker at
https://github.com/dataflake/Products.LDAPUserFolder/issues.


Getting the source code
-----------------------
The source code is maintained on GitHub. To check out the main branch:

.. code-block:: console

  $ git clone https://github.com/dataflake/Products.LDAPUserFolder.git

You can also browse the code online at
https://github.com/dataflake/Products.LDAPUserFolder


Preparing the development sandbox
---------------------------------
The following steps only need to be done once to install all the tools and
scripts needed for building, packaging and testing. First, create a
:term:`Virtual environment`. The example here uses Python 3.11, but any Python
version supported by this package will work. Then install all the required
tools:

.. code-block:: console

    $ cd Products.LDAPUserFolder
    $ python3.11 -m venv .
    $ bin/pip install -U pip wheel
    $ bin/pip install -U setuptools zc.buildout tox twine


Running the tests
-----------------
You can use ``tox`` to run the unit and integration tests in this package. The
shipped ``tox`` configuration can run the tests for all supported platforms.
You can read the entire long list of possible options on the
`tox CLI interface documentation page
<https://tox.wiki/en/latest/cli_interface.html>`_, but the following examples
will get you started:

.. code-block:: console

    $ bin/tox -l       # List all available environments
    $ bin/tox -pall    # Run tests for all environments in parallel
    $ bin/tox -epy311  # Run tests on Python 3.11 only
    $ bin/tox -elint   # Run package sanity checks and lint the code


Building the documentation
--------------------------
``tox`` is also used to build the :term:`Sphinx`-based documentation. The
input files are in the `docs` subfolder and the documentation build step will
compile them to HTML. The output is stored in `docs/_build/html/`:

.. code-block:: console

    $ bin/tox -edocs

If the documentation contains doctests they are run as well.
