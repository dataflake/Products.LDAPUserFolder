.. image:: https://api.travis-ci.org/dataflake/Products.LDAPUserFolder.svg?branch=master
   :target: https://travis-ci.org/dataflake/Products.LDAPUserFolder

.. image:: https://readthedocs.org/projects/productsldapuserfolder/badge/?version=latest
   :target: https://productsldapuserfolder.readthedocs.io
   :alt: Documentation Status

.. image:: https://img.shields.io/pypi/v/Products.LDAPUserFolder.svg
   :target: https://pypi.python.org/pypi/Products.LDAPUserFolder
   :alt: PyPI

.. image:: https://img.shields.io/pypi/pyversions/Products.LDAPUserFolder.svg
   :target: https://pypi.python.org/pypi/Products.LDAPUserFolder
   :alt: Python versions

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
