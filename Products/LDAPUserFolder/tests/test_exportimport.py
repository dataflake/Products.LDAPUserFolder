##############################################################################
#
# Copyright (c) 2000-2021 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Export/import tests
"""

import unittest

from OFS.Folder import Folder
from Zope2.App import zcml

from ..LDAPUserFolder import LDAPUserFolder


try:
    import Products.GenericSetup as GenericSetup
    from Products.GenericSetup.testing import BodyAdapterTestCase
    from Products.GenericSetup.testing import ExportImportZCMLLayer
    from Products.GenericSetup.tests.common import BaseRegistryTests
except ImportError:
    class FakeTests(object):
        pass
    BaseRegistryTests = BodyAdapterTestCase = FakeTests
    ExportImportZCMLLayer = GenericSetup = None


class LDAPUserFolderXMLAdapterTests(BodyAdapterTestCase, unittest.TestCase):

    layer = ExportImportZCMLLayer

    def _getTargetClass(self):
        from ..exportimport import LDAPUserFolderXMLAdapter

        return LDAPUserFolderXMLAdapter

    def setUp(self):
        import Products.LDAPUserFolder
        super(LDAPUserFolderXMLAdapterTests, self).setUp()
        zcml.load_config('configure.zcml', Products.LDAPUserFolder)
        self._obj = LDAPUserFolder()
        self._BODY = _LDAPUSERFOLDER_BODY


class _LDAPUserFolderSetup(BaseRegistryTests):

    layer = ExportImportZCMLLayer

    def _initSite(self, use_changed=False):
        self.root.site = Folder(id='site')
        site = self.root.site
        acl = self.root.site.acl_users = LDAPUserFolder()

        if use_changed:
            acl.manage_edit('changed title', 'uid', 'cn',
                            'ou=users,dc=localhost', 1, 'Anonymous, Member',
                            'ou=groups,dc=localhost', 1,
                            'cn=Manager,dc=localhost', 'secret',
                            binduid_usage=2, rdn_attr='uid',
                            obj_classes='top,inetOrgPerson',
                            local_groups=True, implicit_mapping=True,
                            encryption='SSHA', read_only=1,
                            extra_user_filter='(usertype=privileged)')
            acl.manage_addLDAPSchemaItem('mail', friendly_name='Email Address',
                                         multivalued=True,
                                         public_name='publicmail', binary=True)
            acl.manage_addServer('localhost', port='636', use_ssl=True,
                                 conn_timeout=10, op_timeout=10)
            acl.manage_addServer('/var/spool/ldapi', port='', use_ssl=2,
                                 conn_timeout=2, op_timeout=2)
            acl.manage_addGroup('posixAdmin')
            acl.manage_addGroupMapping('posixAdmin', 'Manager')
            acl._anonymous_timeout = 60
            acl._authenticated_timeout = 60
            acl._groups_store['user1'] = ['posixAdmin', 'foobar']
            acl._groups_store['user2'] = ['baz']

        return site


class LDAPUserFolderExportTests(_LDAPUserFolderSetup):

    def test_unchanged(self):
        from Products.GenericSetup.tests.common import DummyExportContext

        from ..exportimport import exportLDAPUserFolder

        site = self._initSite(use_changed=False)
        context = DummyExportContext(site)
        exportLDAPUserFolder(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'ldapuserfolder.xml')
        self._compareDOM(text, _LDAPUSERFOLDER_BODY)
        self.assertEqual(content_type, 'text/xml')

    def test_changed(self):
        from Products.GenericSetup.tests.common import DummyExportContext

        from ..exportimport import exportLDAPUserFolder

        site = self._initSite(use_changed=True)
        context = DummyExportContext(site)
        exportLDAPUserFolder(context)

        self.assertEqual(len(context._wrote), 1)
        filename, text, content_type = context._wrote[0]
        self.assertEqual(filename, 'ldapuserfolder.xml')
        self._compareDOM(text, _CHANGED_EXPORT)
        self.assertEqual(content_type, 'text/xml')


class LDAPUserFolderImportTests(_LDAPUserFolderSetup):

    def test_normal(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from ..exportimport import importLDAPUserFolder

        site = self._initSite()
        acl = site.acl_users

        context = DummyImportContext(site)
        context._files['ldapuserfolder.xml'] = _CHANGED_EXPORT
        importLDAPUserFolder(context)

        self.assertEqual(acl.title, 'changed title')
        self.assertEqual(acl._login_attr, 'uid')
        self.assertEqual(acl._uid_attr, 'cn')
        self.assertEqual(acl.users_base, 'ou=users,dc=localhost')
        self.assertEqual(acl.users_scope, 1)
        self.assertEqual(acl._roles, ['Anonymous', 'Member'])
        self.assertEqual(acl.groups_base, 'ou=groups,dc=localhost')
        self.assertEqual(acl.groups_scope, 1)
        self.assertEqual(acl._binduid, 'cn=Manager,dc=localhost')
        self.assertEqual(acl._bindpwd, 'secret')
        self.assertEqual(acl._binduid_usage, 2)
        self.assertEqual(acl._rdnattr, 'uid')
        self.assertEqual(acl._user_objclasses, ['top', 'inetOrgPerson'])
        self.assertTrue(acl._local_groups)
        self.assertTrue(acl._implicit_mapping)
        self.assertEqual(acl._pwd_encryption, 'SSHA')
        self.assertTrue(acl.read_only)
        self.assertEqual(acl._extra_user_filter, '(usertype=privileged)')

        group_mappings = acl.getGroupMappings()
        self.assertEqual(len(group_mappings), 1)
        self.assertEqual(group_mappings[0], ('posixAdmin', 'Manager'))

        schema = acl.getSchemaConfig()
        self.assertEqual(len(schema), 4)
        self.assertEqual(schema.get('mail'),
                         {'ldap_name': 'mail',
                          'friendly_name': 'Email Address',
                          'public_name': 'publicmail', 'multivalued': True,
                          'binary': True})

        servers = acl.getServers()
        self.assertEqual(len(servers), 2)
        svr1 = {'host': 'localhost', 'port': 636, 'protocol': 'ldaps',
                'conn_timeout': 10, 'op_timeout': 10}
        svr2 = {'host': '/var/spool/ldapi', 'port': 0, 'protocol': 'ldapi',
                'conn_timeout': 2, 'op_timeout': 2}
        self.assertTrue(svr1 in servers)
        self.assertTrue(svr2 in servers)

        local_groups = list(acl._groups_store.items())
        self.assertEqual(len(local_groups), 2)
        self.assertTrue(('user1', ['posixAdmin', 'foobar']) in local_groups)
        self.assertTrue(('user2', ['baz']) in local_groups)

    def test_servers_purge(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from ..exportimport import importLDAPUserFolder

        site = self._initSite(use_changed=True)
        acl = site.acl_users

        context = DummyImportContext(site, purge=False)
        context._files['ldapuserfolder.xml'] = _SERVERS_SCHEMA_PURGE
        importLDAPUserFolder(context)

        servers = acl.getServers()
        self.assertEqual(len(servers), 2)
        svr1 = {'host': 'otherhost', 'port': 1389, 'protocol': 'ldap',
                'conn_timeout': 1, 'op_timeout': 1}
        svr2 = {'host': '/tmp/ldapi', 'port': 0, 'protocol': 'ldapi',
                'conn_timeout': 20, 'op_timeout': 20}
        self.assertTrue(svr1 in servers)
        self.assertTrue(svr2 in servers)

    def test_servers_nopurge(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from ..exportimport import importLDAPUserFolder

        site = self._initSite(use_changed=True)
        acl = site.acl_users

        context = DummyImportContext(site, purge=False)
        context._files['ldapuserfolder.xml'] = _SERVERS_SCHEMA_NOPURGE
        importLDAPUserFolder(context)

        servers = acl.getServers()
        self.assertEqual(len(servers), 4)
        svr1 = {'host': 'otherhost', 'port': 1389, 'protocol': 'ldap',
                'conn_timeout': 1, 'op_timeout': 1}
        svr2 = {'host': '/tmp/ldapi', 'port': 0, 'protocol': 'ldapi',
                'conn_timeout': 20, 'op_timeout': 20}
        svr3 = {'host': 'localhost', 'port': '636', 'protocol': 'ldaps',
                'conn_timeout': 10, 'op_timeout': 10}
        svr4 = {'host': '/var/spool/ldapi', 'port': 0, 'protocol': 'ldapi',
                'conn_timeout': 2, 'op_timeout': 2}
        self.assertTrue(svr1 in servers)
        self.assertTrue(svr2 in servers)
        self.assertTrue(svr3 in servers)
        self.assertTrue(svr4 in servers)

    def test_schema_purge(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from ..exportimport import importLDAPUserFolder

        site = self._initSite(use_changed=True)
        acl = site.acl_users

        context = DummyImportContext(site, purge=False)
        context._files['ldapuserfolder.xml'] = _SERVERS_SCHEMA_PURGE
        importLDAPUserFolder(context)

        schema = acl.getSchemaConfig()
        self.assertEqual(len(schema), 2)
        self.assertEqual(set(schema.keys()), set(['o', 'dc']))

    def test_schema_nopurge(self):
        from Products.GenericSetup.tests.common import DummyImportContext
        from ..exportimport import importLDAPUserFolder

        site = self._initSite(use_changed=True)
        acl = site.acl_users

        context = DummyImportContext(site, purge=False)
        context._files['ldapuserfolder.xml'] = _SERVERS_SCHEMA_NOPURGE
        importLDAPUserFolder(context)

        schema = acl.getSchemaConfig()
        self.assertEqual(len(schema), 6)
        self.assertEqual(set(schema.keys()),
                         set(['cn', 'dc', 'o', 'sn', 'mail', 'uid']))


def test_suite():
    if GenericSetup is None:
        return unittest.TestSuite()
    else:
        return unittest.TestSuite((
            unittest.makeSuite(LDAPUserFolderXMLAdapterTests),
            unittest.makeSuite(LDAPUserFolderExportTests),
            unittest.makeSuite(LDAPUserFolderImportTests),
        ))


_LDAPUSERFOLDER_BODY = """\
<?xml version="1.0" encoding="utf-8"?>
<object name="acl_users" meta_type="LDAPUserFolder">
 <property name="title"></property>
 <property name="_login_attr">cn</property>
 <property name="_uid_attr"></property>
 <property name="users_base">ou=people,dc=mycompany,dc=com</property>
 <property name="users_scope">2</property>
 <property name="_roles">
  <element value="Anonymous"/>
 </property>
 <property name="groups_base">ou=groups,dc=mycompany,dc=com</property>
 <property name="groups_scope">2</property>
 <property name="_binduid"></property>
 <property name="_bindpwd"></property>
 <property name="_binduid_usage">0</property>
 <property name="_rdnattr"></property>
 <property name="_user_objclasses">
  <element value="top"/>
  <element value="person"/>
 </property>
 <property name="_local_groups">False</property>
 <property name="_implicit_mapping">False</property>
 <property name="_pwd_encryption">SHA</property>
 <property name="read_only">False</property>
 <property name="_extra_user_filter"></property>
 <property name="_anonymous_timeout">600</property>
 <property name="_authenticated_timeout">600</property>
 <ldap-schema>
  <schema-item binary="False" friendly_name="Canonical Name" ldap_name="cn"
     multivalued="False" public_name=""/>
  <schema-item binary="False" friendly_name="Last Name" ldap_name="sn"
     multivalued="False" public_name=""/>
 </ldap-schema>
</object>
"""

_CHANGED_EXPORT = """\
<?xml version="1.0" encoding="utf-8"?>
<object name="acl_users" meta_type="LDAPUserFolder">
 <property name="title">changed title</property>
 <property name="_login_attr">uid</property>
 <property name="_uid_attr">cn</property>
 <property name="users_base">ou=users,dc=localhost</property>
 <property name="users_scope">1</property>
 <property name="_roles">
  <element value="Anonymous"/>
  <element value="Member"/>
 </property>
 <property name="groups_base">ou=groups,dc=localhost</property>
 <property name="groups_scope">1</property>
 <property name="_binduid">cn=Manager,dc=localhost</property>
 <property name="_bindpwd">secret</property>
 <property name="_binduid_usage">2</property>
 <property name="_rdnattr">uid</property>
 <property name="_user_objclasses">
  <element value="top"/>
  <element value="inetOrgPerson"/>
 </property>
 <property name="_local_groups">True</property>
 <property name="_implicit_mapping">True</property>
 <property name="_pwd_encryption">SSHA</property>
 <property name="read_only">True</property>
 <property name="_extra_user_filter">(usertype=privileged)</property>
 <property name="_anonymous_timeout">60</property>
 <property name="_authenticated_timeout">60</property>
 <additional-groups>
  <element value="posixAdmin"/>
 </additional-groups>
 <group-map>
  <mapped-group ldap_group="posixAdmin" zope_role="Manager"/>
 </group-map>
 <group-users>
  <user dn="user1">
   <element value="posixAdmin"/>
   <element value="foobar"/>
  </user>
  <user dn="user2">
   <element value="baz"/>
  </user>
 </group-users>
 <ldap-servers>
  <ldap-server host="localhost" port="636" protocol="ldaps" conn_timeout="10"
     op_timeout="10"/>
 <ldap-server host="/var/spool/ldapi" port="0" protocol="ldapi"
     conn_timeout="2" op_timeout="2"/>
 </ldap-servers>
 <ldap-schema>
  <schema-item binary="False" friendly_name="Canonical Name" ldap_name="cn"
     multivalued="False" public_name=""/>
  <schema-item binary="True" friendly_name="Email Address" ldap_name="mail"
     multivalued="True" public_name="publicmail"/>
  <schema-item binary="False" friendly_name="Last Name" ldap_name="sn"
     multivalued="False" public_name=""/>
  <schema-item binary="False" friendly_name="uid" ldap_name="uid"
     multivalued="False" public_name=""/>
 </ldap-schema>
</object>
"""

_SERVERS_SCHEMA_PURGE = """\
<?xml version="1.0" encoding="utf-8"?>
<object name="acl_users" meta_type="LDAPUserFolder">
 <ldap-servers purge="True">
  <ldap-server host="otherhost" port="1389" protocol="ldap" conn_timeout="1"
     op_timeout="1"/>
  <ldap-server host="/tmp/ldapi" port="0" protocol="ldapi" conn_timeout="20"
     op_timeout="20"/>
 </ldap-servers>
 <ldap-schema purge="True">
  <schema-item binary="False" friendly_name="Organisation" ldap_name="o"
     multivalued="False" public_name=""/>
  <schema-item binary="False" friendly_name="Domain Component" ldap_name="dc"
     multivalued="True" public_name=""/>
 </ldap-schema>
</object>
"""

_SERVERS_SCHEMA_NOPURGE = """\
<?xml version="1.0" encoding="utf-8"?>
<object name="acl_users" meta_type="LDAPUserFolder">
 <ldap-servers purge="False">
  <ldap-server host="otherhost" port="1389" protocol="ldap" conn_timeout="1"
     op_timeout="1"/>
  <ldap-server host="/tmp/ldapi" port="0" protocol="ldapi" conn_timeout="20"
     op_timeout="20"/>
 </ldap-servers>
 <ldap-schema purge="False">
  <schema-item binary="False" friendly_name="Organisation" ldap_name="o"
     multivalued="False" public_name=""/>
  <schema-item binary="False" friendly_name="Domain Component" ldap_name="dc"
     multivalued="True" public_name=""/>
 </ldap-schema>
</object>
"""
