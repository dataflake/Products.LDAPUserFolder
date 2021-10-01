.. image:: https://github.com/dataflake/Products.LDAPUserFolder/actions/workflows/tests.yml/badge.svg?branch=3.x
   :target: https://github.com/dataflake/Products.LDAPUserFolder/actions/workflows/tests.yml

.. image:: https://coveralls.io/repos/github/dataflake/Products.LDAPUserFolder/badge.svg?branch=3.x
   :target: https://coveralls.io/github/dataflake/Products.LDAPUserFolder?branch=3.x

.. image:: https://readthedocs.org/projects/productsldapuserfolder/badge/?version=latest
   :target: https://productsldapuserfolder.readthedocs.io
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/Products.LDAPUserFolder.svg
   :target: https://pypi.python.org/pypi/Products.LDAPUserFolder
   :alt: Current version on PyPI

.. image:: https://img.shields.io/pypi/pyversions/Products.LDAPUserFolder.svg
   :target: https://pypi.org/project/Products.LDAPUserFolder
   :alt: Supported Python versions

=========================
 Products.LDAPUserFolder
=========================
This product is a replacement for a Zope user folder. It does not store its 
own user objects but builds them on the fly after authenticating a user against 
the LDAP database.


Documentation
=============
Documentation is available at
https://productsldapuserfolder.readthedocs.io/


Bug tracker
===========
A bug tracker is available at
https://github.com/dataflake/Products.LDAPUserFolder/issues


Debugging problems
==================
All log messages are sent to the standard Zope event log 'event.log'. In 
order to see more verbose logging output you need to increase the log level 
in your Zope instance's zope.conf. See the 'eventlog' directive. Setting 
the 'level' key to 'debug' will maximize log output and may help pinpoint 
problems during setup and testing.
