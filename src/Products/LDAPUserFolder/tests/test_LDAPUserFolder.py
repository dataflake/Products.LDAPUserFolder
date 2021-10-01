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
""" LDAPUserFolder class tests
"""

import copy
import os
from hashlib import sha1

import ldap

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from App.Common import package_home

from dataflake.fakeldap import FakeLDAPConnection

from .base.dummy import LDAPDummyUser
from .base.testcase import LDAPTest
from .config import alternates
from .config import defaults
from .config import manager_user
from .config import user
from .config import user2


dg = defaults.get
ag = alternates.get
ug = user.get
u2g = user2.get


class TestLDAPUserFolder(LDAPTest):

    def testLUFInstantiation(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        self.assertTrue(acl.isPrincipiaFolderish)
        ae(self.folder.__allow_groups__, self.folder.acl_users)
        ae(acl.getProperty('title'), dg('title'))
        ae(acl.getProperty('_login_attr'), dg('login_attr'))
        ae(acl.getProperty('_uid_attr'), dg('uid_attr'))
        ae(acl.getProperty('users_base'), dg('users_base'))
        ae(acl.getProperty('users_scope'), dg('users_scope'))
        ae(acl.getProperty('_roles'), [dg('roles')])
        ae(acl.getProperty('groups_base'), dg('groups_base'))
        ae(acl.getProperty('groups_scope'), dg('groups_scope'))
        ae(acl.getProperty('_binduid'), dg('binduid'))
        ae(acl.getProperty('_bindpwd'), dg('bindpwd'))
        ae(acl.getProperty('_binduid_usage'), dg('binduid_usage'))
        ae(acl.getProperty('_rdnattr'), dg('rdn_attr'))
        ae(acl.getProperty('_local_groups'), not not dg('local_groups'))
        ae(acl.getProperty('_implicit_mapping'),
           not not dg('implicit_mapping'))
        ae(acl.getProperty('_pwd_encryption'), dg('encryption'))
        ae(acl.getProperty('_extra_user_filter'), dg('extra_user_filter'))
        ae(acl.getProperty('read_only'), not not dg('read_only'))
        ae(len(acl._cache('anonymous').getCache()), 0)
        ae(len(acl._cache('authenticated').getCache()), 0)
        ae(len(acl._cache('negative').getCache()), 0)
        ae(len(acl.getSchemaConfig()), 2)
        ae(len(acl.getSchemaDict()), 2)
        ae(len(acl._groups_store), 0)
        ae(len(acl.getProperty('additional_groups')), 0)
        ae(len(acl.getGroupMappings()), 0)
        ae(len(acl.getServers()), 1)

    def testAlternateLUFInstantiation(self):
        from ..LDAPUserFolder import manage_addLDAPUserFolder
        ae = self.assertEqual
        self.folder._delObject('acl_users')
        manage_addLDAPUserFolder(self.folder)
        acl = self.folder.acl_users
        host, port = ag('server').split(':')
        acl.manage_addServer(host, port=port)
        acl.manage_edit(title=ag('title'), login_attr=ag('login_attr'),
                        uid_attr=ag('uid_attr'), users_base=ag('users_base'),
                        users_scope=ag('users_scope'), roles=ag('roles'),
                        groups_base=ag('groups_base'),
                        groups_scope=ag('groups_scope'),
                        binduid=ag('binduid'), bindpwd=ag('bindpwd'),
                        binduid_usage=ag('binduid_usage'),
                        rdn_attr=ag('rdn_attr'),
                        local_groups=ag('local_groups'),
                        implicit_mapping=ag('implicit_mapping'),
                        encryption=ag('encryption'),
                        read_only=ag('read_only'),
                        extra_user_filter=ag('extra_user_filter'))
        acl = self.folder.acl_users
        ae(acl.getProperty('title'), ag('title'))
        ae(acl.getProperty('_login_attr'), ag('login_attr'))
        ae(acl.getProperty('_uid_attr'), ag('uid_attr'))
        ae(acl.getProperty('users_base'), ag('users_base'))
        ae(acl.getProperty('users_scope'), ag('users_scope'))
        ae(acl.getProperty('_roles'),
           [x.strip() for x in ag('roles').split(',')])
        ae(acl.getProperty('groups_base'), ag('groups_base'))
        ae(acl.getProperty('groups_scope'), ag('groups_scope'))
        ae(acl.getProperty('_binduid'), ag('binduid'))
        ae(acl.getProperty('_bindpwd'), ag('bindpwd'))
        ae(acl.getProperty('_binduid_usage'), ag('binduid_usage'))
        ae(acl.getProperty('_rdnattr'), ag('rdn_attr'))
        ae(acl.getProperty('_local_groups'), not not ag('local_groups'))
        ae(acl.getProperty('_implicit_mapping'),
           not not ag('implicit_mapping'))
        ae(acl.getProperty('_pwd_encryption'), ag('encryption'))
        ae(acl.getProperty('_extra_user_filter'), ag('extra_user_filter'))
        ae(acl.getProperty('read_only'), not not ag('read_only'))

    def testLDAPDelegateInstantiation(self):
        ld = self.folder.acl_users._delegate
        ae = self.assertEqual
        ae(len(ld.getServers()), 1)
        ae(ld.login_attr, dg('login_attr'))
        ae(ld.rdn_attr, dg('rdn_attr'))
        ae(ld.bind_dn, dg('binduid'))
        ae(ld.bind_pwd, dg('bindpwd'))
        ae(ld.binduid_usage, dg('binduid_usage'))
        ae(ld.u_base, dg('users_base'))
        ae(ld.u_classes, ['top', 'person'])
        ae(ld.read_only, not not dg('read_only'))

    def testLUFEdit(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        acl.manage_edit(title=ag('title'), login_attr=ag('login_attr'),
                        uid_attr=ag('uid_attr'), users_base=ag('users_base'),
                        users_scope=ag('users_scope'), roles=ag('roles'),
                        groups_base=ag('groups_base'),
                        groups_scope=ag('groups_scope'),
                        binduid=ag('binduid'), bindpwd=ag('bindpwd'),
                        binduid_usage=ag('binduid_usage'),
                        rdn_attr=ag('rdn_attr'), obj_classes=ag('obj_classes'),
                        local_groups=ag('local_groups'),
                        implicit_mapping=ag('implicit_mapping'),
                        encryption=ag('encryption'), read_only=ag('read_only'))
        ae(acl.getProperty('title'), ag('title'))
        ae(acl.getProperty('_login_attr'), ag('login_attr'))
        ae(acl.getProperty('_uid_attr'), ag('uid_attr'))
        ae(acl.getProperty('users_base'), ag('users_base'))
        ae(acl.getProperty('users_scope'), ag('users_scope'))
        ae(', '.join(acl.getProperty('_roles')), ag('roles'))
        ae(acl.getProperty('groups_base'), ag('groups_base'))
        ae(acl.getProperty('groups_scope'), ag('groups_scope'))
        ae(acl.getProperty('_binduid'), ag('binduid'))
        ae(acl._delegate.bind_dn, ag('binduid'))
        ae(acl.getProperty('_bindpwd'), ag('bindpwd'))
        ae(acl._delegate.bind_pwd, ag('bindpwd'))
        ae(acl.getProperty('_binduid_usage'), ag('binduid_usage'))
        ae(acl.getProperty('_rdnattr'), ag('rdn_attr'))
        ae(', '.join(acl.getProperty('_user_objclasses')), ag('obj_classes'))
        ae(acl.getProperty('_local_groups'), not not ag('local_groups'))
        ae(acl.getProperty('_implicit_mapping'),
           not not ag('implicit_mapping'))
        ae(acl.getProperty('_pwd_encryption'), ag('encryption'))
        ae(acl.getProperty('read_only'), not not ag('read_only'))

    def testLUFWebEdit(self):
        # The Properties form uses a hashed password field. Need to make sure
        # the hash does not end up as the actual password value anywhere.
        acl = self.folder.acl_users
        ae = self.assertEqual

        ae(acl.getProperty('_binduid'), dg('binduid'))
        ae(acl._delegate.bind_dn, dg('binduid'))
        ae(acl.getProperty('_bindpwd'), dg('bindpwd'))
        ae(acl._delegate.bind_pwd, dg('bindpwd'))

        acl.manage_edit(title=ag('title'), login_attr=ag('login_attr'),
                        uid_attr=ag('uid_attr'),
                        users_base=ag('users_base'),
                        users_scope=ag('users_scope'),
                        roles=ag('roles'), groups_base=ag('groups_base'),
                        groups_scope=ag('groups_scope'),
                        binduid=ag('binduid'),
                        bindpwd=acl.getEncryptedBindPassword(),
                        binduid_usage=ag('binduid_usage'),
                        rdn_attr=ag('rdn_attr'),
                        obj_classes=ag('obj_classes'),
                        local_groups=ag('local_groups'),
                        implicit_mapping=ag('implicit_mapping'),
                        encryption=ag('encryption'),
                        read_only=ag('read_only'))
        ae(acl.getProperty('_binduid'), ag('binduid'))
        ae(acl._delegate.bind_dn, ag('binduid'))
        ae(acl.getProperty('_bindpwd'), dg('bindpwd'))
        ae(acl._delegate.bind_pwd, dg('bindpwd'))

    def testAddUser(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(msg.split(' ')[0] == 'ALREADY_EXISTS')
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        for role in ug('user_roles'):
            self.assertTrue(role in user_ob.getRoles())
        for role in acl.getProperty('_roles'):
            self.assertTrue(role in user_ob.getRoles())
        ae(user_ob.getProperty('cn'), ug('cn'))
        ae(user_ob.getProperty('sn'), ug('sn'))
        ae(user_ob.getId(), ug(acl.getProperty('_uid_attr')))
        ae(user_ob.getUserName(), ug(acl.getProperty('_login_attr')))

    def testAddUserReadOnly(self):
        acl = self.folder.acl_users
        acl.read_only = 1
        acl._delegate.read_only = 1
        ae = self.assertEqual
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(msg)
        user_ob = acl.getUser(ug('cn'))
        ae(user_ob, None)

    def testGetUser(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_ob = acl.getUserByDN(user_ob.getUserDN())
        self.assertNotEqual(user_ob, None)
        user_ob = acl.getUserById(ug(acl.getProperty('_uid_attr')))
        self.assertNotEqual(user_ob, None)
        self.assertEqual(len(acl.getUserNames()), 1)

    def testGetUserWrongObjectclasses(self):
        acl = self.folder.acl_users

        for role in u2g('user_roles'):
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assertTrue(not msg)

        # Adding a new user will always add it with the object classes set
        # on the Configure tab. Need to do some more or less nasty munging
        # to put the undesirable object classes on this user!
        acl.manage_addLDAPSchemaItem('objectClass', multivalued='1')
        user_ob = acl.getUser(u2g(acl.getProperty('_login_attr')))
        ob_class_string = ';'.join(u2g('objectClasses'))
        acl.manage_editUser(user_ob.getUserDN(), REQUEST=None,
                            kwargs={'objectClass': ob_class_string})

        user_ob = acl.getUser(u2g(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob, None)

        user_ob = acl.getUserById(u2g(acl.getProperty('_uid_attr')))
        self.assertEqual(user_ob, None)

        results = acl.findUser('cn', u2g('cn'))
        self.assertEqual(len(results), 0)

    def testFindUser(self):
        # test finding a user with specific or wildcard match on one attribute
        acl = self.folder.acl_users

        for role in u2g('user_roles'):
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assertTrue(not msg)

        key = acl.getProperty('_login_attr')
        user_cn = u2g(key)
        crippled_cn = user_cn[:-1]

        # Search on a bogus attribute, must return error result
        result = acl.findUser('foobarkey', 'baz')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get('sn'), 'Error')

        # Search on valid attribute with invalid term, must return empty result
        result = acl.findUser(key, 'invalid_cn')
        self.assertEqual(len(result), 0)

        # We can also try this through the extra user filter
        acl._extra_user_filter = "(%s=%s)" % (key, "invalid_cn")
        result = acl.findUser(key, user_cn)
        self.assertEqual(len(result), 0)
        acl._extra_user_filter = ''

        # Search with wildcard - both user_cn and crippled_cn must return
        # the data for user2.
        result = acl.findUser(key, user_cn)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        result = acl.findUser(key, crippled_cn)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        # Repeat the previous two searches by asking for the friendly name
        # assigned to the cn ("Canonical Name")
        result = acl.findUser('Canonical Name', user_cn)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        result = acl.findUser('Canonical Name', crippled_cn)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        # Test the mapped public name by putting one into the schema
        # by force, then asking for it
        acl._ldapschema['cn']['public_name'] = 'Comic Name'
        result = acl.findUser('Comic Name', user_cn)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        result = acl.findUser('Comic Name', crippled_cn)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        # Now we ask for exact matches. Only user_cn returns results.
        result = acl.findUser(key, user_cn, exact_match=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        result = acl.findUser(key, crippled_cn, exact_match=True)
        self.assertEqual(len(result), 0)

    def testSearchUsers(self):
        # test finding a user with specific or wildcard match on
        # multiple attributes
        acl = self.folder.acl_users

        for role in u2g('user_roles'):
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assertTrue(not msg)

        key = acl.getProperty('_login_attr')
        user_cn = u2g(key)
        crippled_cn = user_cn[:-1]
        user_sn = u2g('sn')
        crippled_sn = user_sn[:-1]

        # Search on a bogus attribute, must return error result
        result = acl.searchUsers(foobarkey='baz')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get('sn'), 'Error')

        # Search on valid attribute with invalid term, must return empty result
        result = acl.searchUsers(cn='invalid_cn', sn=user_sn)
        self.assertEqual(len(result), 0)

        # Search with wildcard - both user_cn and crippled_cn must return
        # the data for user2.
        result = acl.searchUsers(cn=user_cn, sn=user_sn)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        result = acl.searchUsers(cn=crippled_cn, sn=crippled_sn)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        # Now we ask for exact matches. Only user_cn returns results.
        result = acl.searchUsers(cn=user_cn, sn=user_sn, exact_match=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

        result = acl.searchUsers(cn=crippled_cn, sn=crippled_sn,
                                 exact_match=True)
        self.assertEqual(len(result), 0)

        # Weird edge case: Someone put "dn" into the LDAP Schema tab and
        # searched for that
        acl.manage_addLDAPSchemaItem('dn', 'DN')
        user2_dn = 'cn=%s,%s' % (user_cn, acl.users_base)
        result = acl.searchUsers(dn=user2_dn, exact_match=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get(key), user_cn)

    def testGetUserNames(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        expected = sorted([repr(x) for x in range(100)])
        for name in expected:
            u = user.copy()
            u['cn'] = name
            u['sn'] = name
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assertTrue(not msg)
        userlist = acl.getUserNames()
        self.assertEqual(userlist, tuple(expected))

    def testGetUserNames_nouser(self):
        # Special behavior for the ZMI, which will show a different
        # widget if OverflowError is encountered
        acl = self.folder.acl_users
        self.assertRaises(OverflowError, acl.getUserNames)

    def testUserIds(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        expected = sorted([repr(x) for x in range(100)])
        for name in expected:
            u = user.copy()
            u['cn'] = name
            u['sn'] = name
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assertTrue(not msg)
        userlist = acl.getUserIds()
        self.assertEqual(userlist, tuple(expected))

    def testUserIdsAndNames(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        expected = sorted([(repr(x), repr(x)) for x in range(100)])
        for name in expected:
            u = user.copy()
            u['cn'] = name[0]
            u['sn'] = name[1]
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assertTrue(not msg)
        userlist = acl.getUserIdsAndNames()
        self.assertEqual(userlist, tuple(expected))

    def testDeleteUser(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assertTrue(not msg)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertNotEqual(mgr_ob, None)
        newSecurityManager({}, mgr_ob)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.manage_deleteUsers([user_dn])
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob, None)
        self.assertEqual(acl.getGroups(dn=user_dn), [])
        noSecurityManager()

    def testDeleteUserReadOnly(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.read_only = 1
        acl._delegate.read_only = 1
        acl.manage_deleteUsers([user_dn])
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assertNotEqual(acl.getGroups(dn=user_dn), [])

    def testEditUser(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'sn': 'New'})
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob.getProperty('sn'), 'New')

    def testEditUserMultivalueHandling(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'sn': 'New; Lastname'})
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob.getProperty('sn'), 'New; Lastname')

    def testEditUserReadOnly(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.read_only = 1
        acl._delegate.read_only = 1
        msg = acl.manage_editUser(user_dn, kwargs={'sn': 'New'})
        self.assertTrue(msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertEqual(user_ob.getProperty('sn'), ug('sn'))

    def testEditUserPassword(self):
        conn = FakeLDAPConnection()
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        res = conn.search_s(user_ob.getUserDN(), scope=ldap.SCOPE_BASE)
        old_pw = res[0][1]['userPassword'][0]
        acl.manage_editUserPassword(user_dn, 'newpass')
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        res = conn.search_s(user_ob.getUserDN(), scope=ldap.SCOPE_BASE)
        new_pw = res[0][1]['userPassword'][0]
        self.assertNotEqual(old_pw, new_pw)

    def testEditUserPasswordReadOnly(self):
        conn = FakeLDAPConnection()
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        res = conn.search_s(user_ob.getUserDN(), scope=ldap.SCOPE_BASE)
        old_pw = res[0][1]['userPassword'][0]
        acl.read_only = 1
        acl._delegate.read_only = 1
        acl.manage_editUserPassword(user_dn, 'newpass')
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        res = conn.search_s(user_ob.getUserDN(), scope=ldap.SCOPE_BASE)
        new_pw = res[0][1]['userPassword'][0]
        self.assertEqual(old_pw, new_pw)

    def testEditUserRoles(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        new_role = 'Privileged'
        acl.manage_addGroup(new_role)
        acl.manage_addGroupMapping(new_role, new_role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assertTrue(new_role not in user_ob.getRoles())
        user_dn = user_ob.getUserDN()
        acl.manage_editUserRoles(user_dn, ['Manager', new_role])
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assertTrue(new_role in user_ob.getRoles())

    def testEditUserRolesReadOnly(self):
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        new_role = 'Privileged'
        acl.manage_addGroup(new_role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assertTrue(new_role not in user_ob.getRoles())
        user_dn = user_ob.getUserDN()
        acl._delegate.read_only = 1
        acl.manage_editUserPassword(user_dn, 'newpass')
        acl.manage_editUserRoles(user_dn, ['Manager', new_role])
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        self.assertTrue(new_role not in user_ob.getRoles())

    def testModRDN(self):
        acl = self.folder.acl_users
        ae = self.assertEqual
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assertTrue(not msg)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertNotEqual(mgr_ob, None)
        newSecurityManager({}, mgr_ob)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertTrue(not msg)
        user_ob = acl.getUser(ug(acl.getProperty('_login_attr')))
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'cn': 'new'})
        user_ob = acl.getUser('new')
        ae(user_ob.getProperty('cn'), 'new')
        ae(user_ob.getId(), 'new')
        new_dn = 'cn=new,%s' % acl.getProperty('users_base')
        ae(user_ob.getUserDN(), new_dn)
        for role in ug('user_roles'):
            self.assertTrue(role in user_ob.getRoles())
        for role in acl.getProperty('_roles'):
            self.assertTrue(role in user_ob.getRoles())
        noSecurityManager()

    def testSetUserProperty(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assertTrue(not msg)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertNotEqual(mgr_ob, None)
        self.assertEqual(mgr_ob.getProperty('sn'), manager_user.get('sn'))
        acl.manage_setUserProperty(mgr_ob.getUserDN(), 'sn', 'NewLastName')
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('sn'), 'NewLastName')

    def testSetUserPropertyMultivalueHandling(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assertTrue(not msg)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertNotEqual(mgr_ob, None)
        self.assertEqual(mgr_ob.getProperty('sn'), manager_user.get('sn'))
        acl.manage_setUserProperty(mgr_ob.getUserDN(),
                                   'sn', 'NewLastName; Secondlastname')
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('sn'),
                         'NewLastName; Secondlastname')

    def testSetUserPropertyBinaryHandling(self):
        # Make sure binary attributes are never converted
        test_home = package_home(globals())
        image_path = os.path.join(test_home, 'test.jpg')
        image_file = open(image_path, 'rb')
        image_contents = image_file.read()
        image_file.close()
        acl = self.folder.acl_users
        acl.manage_addLDAPSchemaItem('jpegPhoto', binary=True)
        acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), '')
        acl.manage_setUserProperty(mgr_ob.getUserDN(),
                                   'jpegPhoto', image_contents)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), image_contents)

    def testManageEditUserBinaryHandling(self):
        # Make sure binary attributes are never converted
        test_home = package_home(globals())
        image_path = os.path.join(test_home, 'test.jpg')
        image_file = open(image_path, 'rb')
        image_contents = image_file.read()
        image_file.close()
        acl = self.folder.acl_users
        acl.manage_addLDAPSchemaItem('jpegPhoto', binary=True)
        acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), '')
        acl.manage_editUser(mgr_ob.getUserDN(),
                            kwargs={'jpegPhoto': image_contents})
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), image_contents)

    def testManageAddUserBinaryHandling(self):
        # Make sure binary attributes are never converted
        test_home = package_home(globals())
        image_path = os.path.join(test_home, 'test.jpg')
        image_file = open(image_path, 'rb')
        image_contents = image_file.read()
        image_file.close()
        acl = self.folder.acl_users
        acl.manage_addLDAPSchemaItem('jpegPhoto', binary=True)
        kw_args = copy.deepcopy(manager_user)
        kw_args['jpegPhoto'] = image_contents
        acl.manage_addUser(REQUEST=None, kwargs=kw_args)
        mgr_ob = acl.getUser(manager_user.get(acl.getProperty('_login_attr')))
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), image_contents)

    def testGetAttributesOfAllObjects(self):
        # Test the resilience of the getAttributesOfAllUsers method
        # Even if problems are encountered, the resultset should have
        # keys for each attribute asked for.
        acl = self.folder.acl_users

        # I'm adding a user to prevent a log message from the LDAPUserFolder
        # about not finding any users under Zope 2.8.x
        acl.manage_addUser(REQUEST=None, kwargs=manager_user)

        search_string = '(objectClass=*)'
        attributes = ['foobar', 'baz']
        res = acl.getAttributesOfAllObjects(acl.getProperty('users_base'),
                                            acl.getProperty('users_scope'),
                                            search_string, attributes)

        for attr in attributes:
            self.assertTrue(attr in res)

    def testNegativeCaching(self):
        ae = self.assertEqual
        acl = self.folder.acl_users

        ae(len(acl._cache('negative').getCache()), 0)
        ae(acl.getUser('missing'), None)
        ae(len(acl._cache('negative').getCache()), 1)
        acl.manage_addUser(REQUEST=None, kwargs=user)
        ae(len(acl._cache('negative').getCache()), 0)

    def testNegativeCachePoisoning(self):
        # Test against cache poisoning
        # https://bugs.launchpad.net/bugs/695821
        # The requested attribute value is part of the cache key now
        ae = self.assertEqual
        acl = self.folder.acl_users

        # Prep: Make sure the login and UID attributes are different
        old_login_attr = acl._login_attr
        old_uid_attr = acl._uid_attr
        acl._login_attr = 'cn'
        acl._uid_attr = 'uid'

        # Lookup by the login attrbute
        acl.getUser('missing2')
        acl.getUser('missing2')
        ae(len(acl._cache('negative').getCache()), 1)

        # Lookup by the UID
        acl.getUserById('missing2')
        acl.getUserById('missing2')
        ae(len(acl._cache('negative').getCache()), 2)

        # Lookup by arbitrary attribute
        acl.getUserByAttr('sn', 'missing2', cache=True)
        acl.getUserByAttr('sn', 'missing2', cache=True)
        ae(len(acl._cache('negative').getCache()), 3)

        # _expireUser only removes entries for the login and UID
        acl._expireUser('missing2')
        ae(len(acl._cache('negative').getCache()), 1)

        # Cleanup
        acl._login_attr = old_login_attr
        acl._uid_attr = old_uid_attr

    def testGetUserFilterString(self):
        acl = self.folder.acl_users
        filt_string = acl._getUserFilterString()
        for ob_class in acl.getProperty('_user_objclasses'):
            self.assertTrue('(objectclass=%s)' % ob_class.lower()
                            in filt_string.lower())
        self.assertTrue('(%s=*)' % dg('uid_attr') in filt_string.lower())

        filters = ['(uid=test)', '(cn=test)']
        filt_string = acl._getUserFilterString(filters=filters)
        for ob_class in acl.getProperty('_user_objclasses'):
            self.assertTrue('(objectclass=%s)' % ob_class.lower()
                            in filt_string.lower())
        for filt in filters:
            self.assertTrue(filt in filt_string)
        self.assertFalse('(%s=*)' % dg('uid_attr') in filt_string.lower())

        # Set up some different values
        acl.manage_edit(title=ag('title'), login_attr=ag('login_attr'),
                        uid_attr=ag('uid_attr'), users_base=ag('users_base'),
                        users_scope=ag('users_scope'), roles=ag('roles'),
                        groups_base=ag('groups_base'),
                        groups_scope=ag('groups_scope'), binduid=ag('binduid'),
                        bindpwd=ag('bindpwd'),
                        binduid_usage=ag('binduid_usage'),
                        rdn_attr=ag('rdn_attr'),
                        local_groups=ag('local_groups'),
                        implicit_mapping=ag('implicit_mapping'),
                        encryption=ag('encryption'), read_only=ag('read_only'),
                        obj_classes=ag('obj_classes'),
                        extra_user_filter=ag('extra_user_filter'))

        filt_string = acl._getUserFilterString()
        for ob_class in acl.getProperty('_user_objclasses'):
            self.assertTrue('(objectclass=%s)' % ob_class.lower()
                            in filt_string.lower())
        self.assertTrue(ag('extra_user_filter') in filt_string)
        self.assertTrue('(%s=*)' % ag('uid_attr') in filt_string)

        filters = ['(uid=test)', '(cn=test)']
        filt_string = acl._getUserFilterString(filters=filters)
        for ob_class in acl.getProperty('_user_objclasses'):
            self.assertTrue('(objectclass=%s)' % ob_class.lower()
                            in filt_string.lower())
        for filt in filters:
            self.assertTrue(filt in filt_string)
        self.assertFalse('(%s=*)' % ag('uid_attr') in filt_string)

    def test_expireUser(self):
        # http://www.dataflake.org/tracker/issue_00617 etc.
        acl = self.folder.acl_users

        # Retrieving an invalid user should return None
        nonexisting = acl.getUserById('invalid')
        self.assertIsNone(nonexisting)

        # The retrieval above will add the invalid user to the negative cache
        negative_cache_key = '%s:%s:%s' % (acl._uid_attr, 'invalid',
                                           sha1('').hexdigest())
        self.assertIsNotNone(acl._cache('negative').get(negative_cache_key))

        # Expiring the user must remove it from the negative cache
        acl._expireUser('invalid')
        self.assertIsNone(acl._cache('negative').get(negative_cache_key))

        # User IDs that come in as unicode should not break anything.
        # https://bugs.launchpad.net/bugs/700071
        acl._expireUser(u'invalid')

    def test_manage_reinit(self):
        # part of http://www.dataflake.org/tracker/issue_00629
        acl = self.folder.acl_users
        old_hash = acl._hash

        # Fill some caches
        acl._misc_cache().set('foo', 'bar')
        self.assertEqual(acl._misc_cache().get('foo'), 'bar')
        dummy = LDAPDummyUser('user1', 'pass')
        acl._cache('authenticated').set('user1', dummy)
        self.assertEqual(acl._cache('authenticated').get('user1'), dummy)
        acl._cache('anonymous').set('user1', dummy)
        self.assertEqual(acl._cache('anonymous').get('user1'), dummy)
        acl._cache('negative').set('user1', dummy)
        self.assertEqual(acl._cache('negative').get('user1'), dummy)

        acl.manage_reinit()
        self.assertFalse(acl._misc_cache().get('foo'))
        self.assertFalse(acl._cache('authenticated').get('user1'))
        self.assertFalse(acl._cache('anonymous').get('user1'))
        self.assertFalse(acl._cache('negative').get('user1'))
        self.assertFalse(acl._hash == old_hash)
