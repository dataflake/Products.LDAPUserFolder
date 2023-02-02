Change log
==========

This change log covers releases starting with version 3.0. For earlier
releases, see the file `HISTORY.txt` in this folder.

5.0 (2023-02-02)
----------------
- Drop support for Python 3.5 and 3.6.


4.1 (2023-01-16)
----------------
- add support for Python 3.10 and 3.11

- python-ldap 3.4 is no longer compatible with Python 3.5


4.0 (2021-11-02)
----------------
- fixed configuration checkbox for `Read only`

- no longer use `Anonymous` as default value for `Default user Roles`.

- drop support for Python 2 and add support for Python 3.5 through 3.9.
  This package is now compatible with Zope 4 on Python 3 and Zope 5. If you
  use Zope 4 on Python 2, please use the LDAPUserFolder 3 release series. If
  you use Zope 2 please use the LDAPUserFolder 2 release series.


3.2 (2021-10-01)
----------------
- merge the old help system contents into the Sphinx documentation

- use coveralls.io for code coverage reporting

- use GitHub Actions for automated tests and ditch Travis CI

- complete historical change log and add it to the Sphinx documentation

- Use Zope's own string encoding instead of a hardcoded value in ``utils``

- full flake8/isort compatibility

- packaging cleanup


3.1 (2019-01-20)
----------------
- don't encode attributes when wrapping an LDAPUser if they are flagged binary


3.0 (2018-05-21)
----------------
- Zope 4 compatibility

- merge and fix old HelpSys API docs into interfaces and add Sphinx doc

- add instance scripts as a test/development convenience

- unbreak saving of bind passwords on the Configure tab

- remove old _SharedResource code and simplify caching

- replace Products.LDAPUserFolder.SimpleCache.SimpleCache with
  Products.LDAPUserFolder.cache.UserCache, based on
  dataflake.cache.timeout.TimeoutCache

- replace Products.LDAPUserFolder.SimpleCache.SharedObject with
  dataflake.cache.simple.SimpleCache

- flake8 whitespace cleanup

- moved the code to GitHub

- officially dropped Python 2.6 support, only Python 2.7 is supported.

- moved documentation to Sphinx

- sanitized buildout test script generation to always use the 
  ``exportimport`` extra and always test the `GenericSetup` 
  export/import support

- Add ``tox`` configuration to support automated testing
  on all supported Python versions

- Removed the LDAPUserSatellite code due to severe bit-rot. Please use
  the PluggableAuthService package in conjunction with LDAPMultiPlugins
  to gain the same functionality.

- Removed the CMF tools, please use the package ``Products.CMFLDAP``
  (see https://pypi.org/pypi/Products.CMFLDAP) instead.

- ensure bind passwords used for the LDAP delegate and the user
  folder do not get out of sync

- Refactor some definitions in the utils module to make them easier 
  to override (Patch by Godefroid Chapelle)

- Fixed a missing string conversion in getGroupedUsers (Patch by
  Godefroid Chapelle)

- Fix python-ldap error when receiving sets instead of lists for
  attributes to search on (Patch by Godefroid Chapelle)

- When comparing a login value to login values found on the LDAP 
  server strip the login value first. This follows OpenLDAP behavior
  which considers values as matches even with trailing or leading 
  spaces in the value query filter.
  (https://bugs.launchpad.net/bugs/1060080)

- LDAPDelegate: When using a user from the Zope security machinery 
  for the purpose of finding a suitable bind DN and password for 
  connecting to a LDAP server, discard it when it's not been created
  as the result of a real login and thus has an invalid password
  (https://bugs.launchpad.net/bugs/1060112)
