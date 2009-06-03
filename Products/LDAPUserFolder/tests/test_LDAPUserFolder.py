##############################################################################
#
# Copyright (c) 2000-2009 Jens Vagelpohl and Contributors. All Rights Reserved.
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

$Id$
"""

import copy
import os.path
import unittest

from AccessControl.SecurityManagement import newSecurityManager
from AccessControl.SecurityManagement import noSecurityManager
from App.Common import package_home

from Products.LDAPUserFolder import manage_addLDAPUserFolder

from dataflake.ldapconnection.tests import fakeldap
from Products.LDAPUserFolder.tests.base.dummy import LDAPDummyUser
from Products.LDAPUserFolder.tests.base.testcase import LDAPTest
from Products.LDAPUserFolder.tests.config import defaults
from Products.LDAPUserFolder.tests.config import alternates
from Products.LDAPUserFolder.tests.config import user
from Products.LDAPUserFolder.tests.config import user2
from Products.LDAPUserFolder.tests.config import manager_user

class TestLDAPUserFolder(LDAPTest):

    def testLUFInstantiation(self):
        acl = self.folder.acl_users
        self.assertEquals( self.folder.__allow_groups__
                         , self.folder.acl_users
                         )
        self.assertEquals(acl.title, defaults['title'])
        self.assertEquals(acl._login_attr, defaults['login_attr'])
        self.assertEquals(acl._uid_attr, defaults['uid_attr'])
        self.assertEquals(acl.users_base, defaults['users_base'])
        self.assertEquals(acl.users_scope, defaults['users_scope'])
        self.assertEquals(acl._roles, [defaults['roles']])
        self.assertEquals(acl.groups_base, defaults['groups_base'])
        self.assertEquals(acl.groups_scope, defaults['groups_scope'])
        self.assertEquals(acl._binduid, defaults['binduid'])
        self.assertEquals(acl._bindpwd, defaults['bindpwd'])
        self.assertEquals(acl._binduid_usage, defaults['binduid_usage'])
        self.assertEquals(acl._rdnattr, defaults['rdn_attr'])
        self.assertEquals(acl._local_groups, bool(defaults['local_groups']))
        self.assertEquals( acl._implicit_mapping
                         , bool(defaults['implicit_mapping'])
                         )
        self.assertEquals(acl._pwd_encryption, defaults['encryption'])
        self.assertEquals(acl._extra_user_filter, defaults['extra_user_filter'])
        self.assertEquals(acl.read_only, bool(defaults['read_only']))
        self.assertEquals(len(acl._cache('anonymous').getCache()), 0)
        self.assertEquals(len(acl._cache('authenticated').getCache()), 0)
        self.assertEquals(len(acl._cache('negative').getCache()), 0)
        self.assertEquals(len(acl.getSchemaConfig().keys()), 2)
        self.assertEquals(len(acl.getSchemaDict()), 2)
        self.assertEquals(len(acl._groups_store), 0)
        self.assertEquals(len(acl._additional_groups), 0)
        self.assertEquals(len(acl.getGroupMappings()), 0)
        self.assertEquals(len(acl.getServers()), 1)

    def testAlternateLUFInstantiation(self):
        self.folder._delObject('acl_users')
        manage_addLDAPUserFolder(self.folder)
        acl = self.folder.acl_users
        host, port = alternates['server'].split(':')
        acl.manage_addServer(host, port=port)
        acl.manage_edit( title = alternates['title']
                       , login_attr = alternates['login_attr']
                       , uid_attr = alternates['uid_attr']
                       , users_base = alternates['users_base']
                       , users_scope = alternates['users_scope']
                       , roles= alternates['roles']
                       , groups_base = alternates['groups_base']
                       , groups_scope = alternates['groups_scope']
                       , binduid = alternates['binduid']
                       , bindpwd = alternates['bindpwd']
                       , binduid_usage = alternates['binduid_usage']
                       , rdn_attr = alternates['rdn_attr']
                       , local_groups = alternates['local_groups']
                       , implicit_mapping = alternates['implicit_mapping']
                       , encryption = alternates['encryption']
                       , read_only = alternates['read_only']
                       , extra_user_filter = alternates['extra_user_filter']
                       )
        self.assertEquals(acl.title, alternates['title'])
        self.assertEquals(acl._login_attr, alternates['login_attr'])
        self.assertEquals(acl._uid_attr, alternates['uid_attr'])
        self.assertEquals(acl.users_base, alternates['users_base'])
        self.assertEquals(acl.users_scope, alternates['users_scope'])
        self.assertEquals( acl._roles
                         , [x.strip() for x in alternates['roles'].split(',')]
                         )
        self.assertEquals(acl.groups_base, alternates['groups_base'])
        self.assertEquals(acl.groups_scope, alternates['groups_scope'])
        self.assertEquals(acl._binduid, alternates['binduid'])
        self.assertEquals(acl._bindpwd, alternates['bindpwd'])
        self.assertEquals(acl._binduid_usage, alternates['binduid_usage'])
        self.assertEquals(acl._rdnattr, alternates['rdn_attr'])
        self.assertEquals(acl._local_groups, bool(alternates['local_groups']))
        self.assertEquals( acl._implicit_mapping
                         , bool(alternates['implicit_mapping'])
                         )
        self.assertEquals(acl._pwd_encryption, alternates['encryption'])
        self.assertEquals( acl._extra_user_filter
                         , alternates['extra_user_filter']
                         )
        self.assertEquals(acl.read_only, bool(alternates['read_only']))

    def testLDAPDelegateInstantiation(self):
        ld = self.folder.acl_users._delegate
        self.assertEquals(len(ld.getServers()), 1)
        self.assertEquals(ld.login_attr, defaults['login_attr'])
        self.assertEquals(ld.rdn_attr, defaults['rdn_attr'])
        self.assertEquals(ld.bind_dn, defaults['binduid'])
        self.assertEquals(ld.bind_pwd, defaults['bindpwd'])
        self.assertEquals(ld.binduid_usage, defaults['binduid_usage'])
        self.assertEquals(ld.u_base, defaults['users_base'])
        self.assertEquals(ld.u_classes, ['top', 'person'])
        self.assertEquals(ld.read_only, bool(defaults['read_only']))

    def testLUFEdit(self):
        acl = self.folder.acl_users
        acl.manage_edit( title = alternates['title']
                       , login_attr = alternates['login_attr']
                       , uid_attr = alternates['uid_attr']
                       , users_base = alternates['users_base']
                       , users_scope = alternates['users_scope']
                       , roles = alternates['roles']
                       , groups_base = alternates['groups_base']
                       , groups_scope = alternates['groups_scope']
                       , binduid = alternates['binduid']
                       , bindpwd = alternates['bindpwd']
                       , binduid_usage = alternates['binduid_usage']
                       , rdn_attr = alternates['rdn_attr']
                       , obj_classes = alternates['obj_classes']
                       , local_groups = alternates['local_groups']
                       , implicit_mapping = alternates['implicit_mapping']
                       , encryption = alternates['encryption']
                       , read_only = alternates['read_only']
                       )
        self.assertEquals(acl.title, alternates['title'])
        self.assertEquals(acl._login_attr, alternates['login_attr'])
        self.assertEquals(acl._uid_attr, alternates['uid_attr'])
        self.assertEquals(acl.users_base, alternates['users_base'])
        self.assertEquals(acl.users_scope, alternates['users_scope'])
        self.assertEquals(', '.join(acl._roles), alternates['roles'])
        self.assertEquals(acl.groups_base, alternates['groups_base'])
        self.assertEquals(acl.groups_scope, alternates['groups_scope'])
        self.assertEquals(acl._binduid, alternates['binduid'])
        self.assertEquals(acl._bindpwd, alternates['bindpwd'])
        self.assertEquals(acl._binduid_usage, alternates['binduid_usage'])
        self.assertEquals(acl._rdnattr, alternates['rdn_attr'])
        self.assertEquals( ', '.join(acl._user_objclasses)
                         , alternates['obj_classes']
                         )
        self.assertEquals(acl._local_groups, bool(alternates['local_groups']))
        self.assertEquals( acl._implicit_mapping
                         , bool(alternates['implicit_mapping'])
                         )
        self.assertEquals(acl._pwd_encryption, alternates['encryption'])
        self.assertEquals(acl.read_only, bool(alternates['read_only']))

    def testAddUser(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        for role in user['user_roles']:
            self.assert_(role in user_ob.getRoles())
        for role in acl._roles:
            self.assert_(role in user_ob.getRoles())
        self.assertEquals(user_ob.getProperty('cn'), user['cn'])
        self.assertEquals(user_ob.getProperty('sn'), user['sn'])
        self.assertEquals(user_ob.getId(), user[acl._uid_attr])
        self.assertEquals(user_ob.getUserName(), user[acl._login_attr])

    def testAddUserReadOnly(self):
        acl = self.folder.acl_users
        acl.read_only = 1
        acl._delegate.read_only = 1
        ae=self.assertEqual
        self.assertRaises( RuntimeError
                         , acl.manage_addUser
                         , REQUEST=None
                         , kwargs=user
                         )
        user_ob = acl.getUser(user['cn'])
        self.assertEquals(user_ob, None)

    def testGetUser(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_ob = acl.getUserByDN(user_ob.getUserDN())
        self.assertNotEqual(user_ob, None)
        user_ob = acl.getUserById(user[acl._uid_attr])
        self.assertNotEqual(user_ob, None)
        self.assertEqual(len(acl.getUserNames()), 1)

    def testGetUserWrongObjectclasses(self):
        acl = self.folder.acl_users

        for role in user2['user_roles']:
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assert_(not msg)

        # Adding a new user will always add it with the object classes set
        # on the Configure tab. Need to do some more or less nasty munging
        # to put the undesirable object classes on this user!
        acl.manage_addLDAPSchemaItem( 'objectClass'
                                    , multivalued='1'
                                    )
        user_ob = acl.getUser(user2[acl._login_attr])
        ob_class_string = ';'.join(user2['objectClasses'])
        acl.manage_editUser( user_ob.getUserDN()
                           , REQUEST=None
                           , kwargs={ 'objectClass' : ob_class_string }
                           )

        user_ob = acl.getUser(user2[acl._login_attr])
        self.assertEqual(user_ob, None)

        user_ob = acl.getUserById(user2[acl._uid_attr])
        self.assertEqual(user_ob, None)

        results = acl.findUser('cn', user2['cn'])
        self.assertEqual(len(results), 0)

    def testFindUser(self):
        # test finding a user with specific or wildcard match on one attribute
        acl = self.folder.acl_users

        for role in user2['user_roles']:
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assert_(not msg)

        key = acl._login_attr
        user_cn = user2[key]
        crippled_cn = user_cn[:-1]

        # Search on a bogus attribute, must return error result
        result = acl.findUser('foobarkey', 'baz')
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get('sn'), 'Error')

        # Search on valid attribute with invalid term, must return empty result
        result = acl.findUser(key, 'invalid_cn')
        self.assertEquals(len(result), 0)

        # We can also try this through the extra user filter
        acl._extra_user_filter = "(%s=%s)" % (key, "invalid_cn")
        result = acl.findUser(key, user_cn)
        self.assertEquals(len(result), 0)
        acl._extra_user_filter = ''

        # Search with wildcard - both user_cn and crippled_cn must return
        # the data for user2.
        result = acl.findUser(key, user_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.findUser(key, crippled_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        # Repeat the previous two searches by asking for the friendly name
        # assigned to the cn ("Canonical Name")
        result = acl.findUser('Canonical Name', user_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.findUser('Canonical Name', crippled_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        # Test the mapped public name by putting one into the schema
        # by force, then asking for it
        acl._ldapschema['cn']['public_name'] = 'Comic Name'
        result = acl.findUser('Comic Name', user_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.findUser('Comic Name', crippled_cn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        # Now we ask for exact matches. Only user_cn returns results.
        result = acl.findUser(key, user_cn, exact_match=True)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.findUser(key, crippled_cn, exact_match=True)
        self.assertEquals(len(result), 0)

    def testSearchUsers(self):
        # test finding a user with specific or wildcard match on
        # multiple attributes
        acl = self.folder.acl_users

        for role in user2['user_roles']:
            acl.manage_addGroup(role)

        msg = acl.manage_addUser(REQUEST=None, kwargs=user2)
        self.assert_(not msg)

        key = acl._login_attr
        user_cn = user2[key]
        crippled_cn = user_cn[:-1]
        user_sn = user2['sn']
        crippled_sn = user_sn[:-1]

        # Search on a bogus attribute, must return error result
        result = acl.searchUsers(foobarkey='baz')
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get('sn'), 'Error')

        # Search on valid attribute with invalid term, must return empty result
        result = acl.searchUsers(cn='invalid_cn', sn=user_sn)
        self.assertEquals(len(result), 0)

        # Search with wildcard - both user_cn and crippled_cn must return
        # the data for user2.
        result = acl.searchUsers(cn=user_cn, sn=user_sn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.searchUsers(cn=crippled_cn, sn=crippled_sn)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        # Now we ask for exact matches. Only user_cn returns results.
        result = acl.searchUsers(cn=user_cn, sn=user_sn, exact_match=True)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)

        result = acl.searchUsers( cn=crippled_cn
                                , sn=crippled_sn
                                , exact_match=True
                                )
        self.assertEquals(len(result), 0)

        # Weird edge case: Someone put "dn" into the LDAP Schema tab and
        # searched for that
        acl.manage_addLDAPSchemaItem('dn', 'DN')
        user2_dn = 'cn=%s,%s' % (user_cn, acl.users_base)
        result = acl.searchUsers(dn=user2_dn, exact_match=True)
        self.assertEquals(len(result), 1)
        self.assertEquals(result[0].get(key), user_cn)


    def testGetUserNames(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
        expected = [`x` for x in range(100)]
        expected.sort()
        for name in expected:
            u = user.copy()
            u['cn'] = name
            u['sn'] = name
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assert_(not msg)
        userlist = acl.getUserNames()
        self.assertEqual(userlist, tuple(expected))

    def testUserIds(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
        expected = [`x` for x in range(100)]
        expected.sort()
        for name in expected:
            u = user.copy()
            u['cn'] = name
            u['sn'] = name
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assert_(not msg)
        userlist = acl.getUserIds()
        self.assertEqual(userlist, tuple(expected))

    def testUserIdsAndNames(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
        expected = [(`x`, `x`) for x in range(100)]
        expected.sort()
        for name in expected:
            u = user.copy()
            u['cn'] = name[0]
            u['sn'] = name[1]
            msg = acl.manage_addUser(REQUEST=None, kwargs=u)
            self.assert_(not msg)
        userlist = acl.getUserIdsAndNames()
        self.assertEqual(userlist, tuple(expected))

    def testDeleteUser(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assert_(not msg)
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
        self.assertNotEqual(mgr_ob, None)
        newSecurityManager({}, mgr_ob)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.manage_deleteUsers([user_dn])
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertEqual(user_ob, None)
        self.assertEqual(acl.getGroups(dn=user_dn), [])
        noSecurityManager()

    def testDeleteUserReadOnly(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.read_only = 1
        acl._delegate.read_only = 1
        acl.manage_deleteUsers([user_dn])
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        self.assertNotEqual(acl.getGroups(dn=user_dn), [])

    def testEditUser(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'sn' : 'New'})
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertEqual(user_ob.getProperty('sn'), 'New')

    def testEditUserMultivalueHandling(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'sn' : 'New; Lastname'})
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertEqual(user_ob.getProperty('sn'), 'New; Lastname')

    def testEditUserReadOnly(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        acl.read_only = 1
        acl._delegate.read_only = 1
        self.assertRaises( RuntimeError
                         , acl.manage_editUser
                         , user_dn
                         , kwargs={'sn' : 'New'}
                         )
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertEqual(user_ob.getProperty('sn'), user['sn'])

    def testEditUserPassword(self):
        conn = fakeldap.initialize('')
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        res = conn.search_s(user_ob.getUserDN(), scope=fakeldap.SCOPE_BASE)
        old_pw = res[0][1]['userPassword'][0]
        acl.manage_editUserPassword(user_dn, 'newpass')
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        res = conn.search_s(user_ob.getUserDN(), scope=fakeldap.SCOPE_BASE)
        new_pw = res[0][1]['userPassword'][0]
        self.assertNotEqual(old_pw, new_pw)

    def testEditUserPasswordReadOnly(self):
        conn = fakeldap.initialize('')
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        res = conn.search_s(user_ob.getUserDN(), scope=fakeldap.SCOPE_BASE)
        old_pw = res[0][1]['userPassword'][0]
        acl.read_only = 1
        acl._delegate.read_only = 1
        self.assertRaises( RuntimeError
                         , acl.manage_editUserPassword
                         , user_dn
                         , 'newpass'
                         )
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        res = conn.search_s(user_ob.getUserDN(), scope=fakeldap.SCOPE_BASE)
        new_pw = res[0][1]['userPassword'][0]
        self.assertEqual(old_pw, new_pw)

    def testEditUserRoles(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        new_role = 'Privileged'
        acl.manage_addGroup(new_role)
        acl.manage_addGroupMapping(new_role, new_role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        self.assert_(new_role not in user_ob.getRoles())
        user_dn = user_ob.getUserDN()
        acl.manage_editUserRoles(user_dn, ['Manager', new_role])
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        self.assert_(new_role in user_ob.getRoles())

    def testEditUserRolesReadOnly(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
        new_role = 'Privileged'
        acl.manage_addGroup(new_role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        self.assert_(new_role not in user_ob.getRoles())
        user_dn = user_ob.getUserDN()
        acl._delegate.read_only = 1
        self.assertRaises( RuntimeError
                         , acl.manage_editUserPassword
                         , user_dn 
                         , 'newpass'
                         )
        self.assertRaises( RuntimeError
                         , acl.manage_editUserRoles
                         , user_dn
                         , ['Manager', new_role]
                         )
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        self.assert_(new_role not in user_ob.getRoles())

    def testModRDN(self):
        acl = self.folder.acl_users
        for role in user['user_roles']:
            acl.manage_addGroup(role)
            acl.manage_addGroupMapping(role, role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assert_(not msg)
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
        self.assertNotEqual(mgr_ob, None)
        newSecurityManager({}, mgr_ob)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assert_(not msg)
        user_ob = acl.getUser(user[acl._login_attr])
        self.assertNotEqual(user_ob, None)
        user_dn = user_ob.getUserDN()
        msg = acl.manage_editUser(user_dn, kwargs={'cn' : 'new'})
        user_ob = acl.getUser('new')
        self.assertEquals(user_ob.getProperty('cn'), 'new')
        self.assertEquals(user_ob.getId(), 'new')
        new_dn = 'cn=new,%s' % acl.users_base
        self.assertEquals(user_ob.getUserDN(), new_dn)
        for role in user['user_roles']:
            self.assert_(role in user_ob.getRoles())
        for role in acl._roles:
            self.assert_(role in user_ob.getRoles())
        noSecurityManager()

    def testSetUserProperty(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assert_(not msg)
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
        self.assertNotEqual(mgr_ob, None)
        self.assertEqual( mgr_ob.getProperty('sn')
                        , manager_user['sn']
                        )
        acl.manage_setUserProperty( mgr_ob.getUserDN()
                                  , 'sn'
                                  , 'NewLastName'
                                  )
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
        self.assertEqual( mgr_ob.getProperty('sn')
                        , 'NewLastName'
                        )

    def testSetUserPropertyMultivalueHandling(self):
        acl = self.folder.acl_users
        msg = acl.manage_addUser(REQUEST=None, kwargs=manager_user)
        self.assert_(not msg)
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
        self.assertNotEqual(mgr_ob, None)
        self.assertEqual( mgr_ob.getProperty('sn')
                        , manager_user['sn']
                        )
        acl.manage_setUserProperty( mgr_ob.getUserDN()
                                  , 'sn'
                                  , 'NewLastName; Secondlastname'
                                  )
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
        self.assertEqual( mgr_ob.getProperty('sn')
                       , 'NewLastName; Secondlastname'
                       )

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
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), '')
        acl.manage_setUserProperty( mgr_ob.getUserDN()
                                  , 'jpegPhoto'
                                  , image_contents
                                  )
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
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
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
        self.assertEqual(mgr_ob.getProperty('jpegPhoto'), '')
        acl.manage_editUser( mgr_ob.getUserDN()
                           , kwargs={'jpegPhoto':image_contents}
                           )
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
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
        mgr_ob = acl.getUser(manager_user[acl._login_attr])
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
        res = acl.getAttributesOfAllObjects( acl.users_base
                                           , acl.users_scope
                                           , search_string
                                           , attributes
                                           )

        for attr in attributes:
            self.failUnless(res.has_key(attr))

    def testNegativeCaching(self):
        acl = self.folder.acl_users
        self.assertEquals(len(acl._cache('negative').getCache()), 0)
        self.assertEquals(acl.getUser('missing'), None)
        self.assertEquals(len(acl._cache('negative').getCache()), 1)
        acl.manage_addUser(REQUEST=None, kwargs=user)
        self.assertEquals(len(acl._cache('negative').getCache()), 0)

    def testGetUserFilterString(self):
        acl = self.folder.acl_users
        filt_string = acl._getUserFilterString()
        for ob_class in acl._user_objclasses:
            self.failUnless('(objectclass=%s)' % ob_class.lower() 
                                 in filt_string.lower())
        self.failUnless('(%s=*)' % defaults['uid_attr'] in 
                                                filt_string.lower())

        filters = ['(uid=test)', '(cn=test)']
        filt_string = acl._getUserFilterString(filters=filters)
        for ob_class in acl._user_objclasses:
            self.failUnless('(objectclass=%s)' % ob_class.lower() 
                                 in filt_string.lower())
        for filt in filters:
            self.failUnless(filt in filt_string)
        self.failIf('(%s=*)' % defaults['uid_attr'] in filt_string.lower())

        # Set up some different values
        acl.manage_edit( title = alternates['title']
                       , login_attr = alternates['login_attr']
                       , uid_attr = alternates['uid_attr']
                       , users_base = alternates['users_base']
                       , users_scope = alternates['users_scope']
                       , roles= alternates['roles']
                       , groups_base = alternates['groups_base']
                       , groups_scope = alternates['groups_scope']
                       , binduid = alternates['binduid']
                       , bindpwd = alternates['bindpwd']
                       , binduid_usage = alternates['binduid_usage']
                       , rdn_attr = alternates['rdn_attr']
                       , local_groups = alternates['local_groups']
                       , implicit_mapping = alternates['implicit_mapping']
                       , encryption = alternates['encryption']
                       , read_only = alternates['read_only']
                       , obj_classes = alternates['obj_classes']
                       , extra_user_filter = alternates['extra_user_filter']
                       )

        filt_string = acl._getUserFilterString()
        for ob_class in acl._user_objclasses:
            self.failUnless('(objectclass=%s)' % ob_class.lower() 
                                 in filt_string.lower())
        self.failUnless(alternates['extra_user_filter'] in filt_string)
        self.failUnless('(%s=*)' % alternates['uid_attr'] in filt_string)

        filters = ['(uid=test)', '(cn=test)']
        filt_string = acl._getUserFilterString(filters=filters)
        for ob_class in acl._user_objclasses:
            self.failUnless('(objectclass=%s)' % ob_class.lower() 
                                 in filt_string.lower())
        for filt in filters:
            self.failUnless(filt in filt_string)
        self.failIf('(%s=*)' % alternates['uid_attr'] in filt_string)


    def test_expireUser(self):
        # http://www.dataflake.org/tracker/issue_00617 etc.
        import sha
        acl = self.folder.acl_users
    
        # Retrieving an invalid user should return None
        nonexisting = acl.getUserById('invalid')
        self.failUnless(nonexisting is None)
    
        # The retrieval above will add the invalid user to the negative cache
        negative_cache_key = '%s:%s' % ('invalid', sha.new('').digest())
        self.failIf(acl._cache('negative').get(negative_cache_key) is None)
    
        # Expiring the user must remove it from the negative cache
        acl._expireUser('invalid')
        self.failUnless(acl._cache('negative').get(negative_cache_key) is None)

    def test_manage_reinit(self):
        # part of http://www.dataflake.org/tracker/issue_00629
        acl = self.folder.acl_users
        old_hash = acl._hash

        # Fill some caches
        acl._misc_cache().set('foo', 'bar')
        self.assertEquals(acl._misc_cache().get('foo'), 'bar')
        dummy = LDAPDummyUser('user1', 'pass')
        acl._cache('authenticated').set('user1', dummy)
        self.assertEquals(acl._cache('authenticated').get('user1'), dummy)
        acl._cache('anonymous').set('user1', dummy)
        self.assertEquals(acl._cache('anonymous').get('user1'), dummy)
        acl._cache('negative').set('user1', dummy)
        self.assertEquals(acl._cache('negative').get('user1'), dummy)

        acl.manage_reinit()
        self.failIf(acl._misc_cache().get('foo'))
        self.failIf(acl._cache('authenticated').get('user1'))
        self.failIf(acl._cache('anonymous').get('user1'))
        self.failIf(acl._cache('negative').get('user1'))
        self.failIf(acl._hash == old_hash)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestLDAPUserFolder),
        ))

