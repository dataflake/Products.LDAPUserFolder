Installation
============

You will need `Python <http://python.org>`_ version 2.7 to
run :mod:`Products.LDAPUserFolder`.

:mod:`Products.LDAPUserFolder` requires the :mod:`pyldap` library. Make
sure your system has LDAP development files and libraries installed so
:mod:`pyldap` can build without failure.

If you use :mod:`zc.buildout` you can add :mod:`Products.LDAPUserFolder`
to the necessary ``eggs`` section to have it pulled in automatically.
