.. image:: https://api.travis-ci.org/zmsdev/Products.LDAPUserFolder4.svg?branch=master
   :target: https://travis-ci.org/zmsdev/Products.LDAPUserFolder4

=========================
 Products.LDAPUserFolder4
=========================
This product is a replacement for a Zope 4 user folder. It does not store its 
own user objects but builds them on the fly after authenticating a user against 
the LDAP database.


To-Dos
===========
* fix tests, str/bytes-handling was revised and tested with real LDAP database.
* publish on pypi


Debugging problems
==================
All log messages are sent to the standard Zope event log 'event.log'. In 
order to see more verbose logging output you need to increase the log level 
in your Zope instance's zope.conf. See the 'eventlog' directive. Setting 
the 'level' key to 'debug' will maximize log output and may help pinpoint 
problems during setup and testing.
