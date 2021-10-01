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
""" LDAPUserFolder group and role functionality tests
"""

from .base.testcase import LDAPTest
from .config import defaults
from .config import user2


class TestGroups(LDAPTest):

    def test_implicitRoleMapping(self):
        acl = self.folder.acl_users
        self.assertEqual(len(acl.getGroupMappings()), 0)
        have_roles = ['ldap_group', 'some_group']
        self.assertEqual(acl._mapRoles(have_roles), [])
        gp = acl.getProperty
        self.assertEqual(gp('_implicit_mapping'), 0)
        acl.manage_edit(title=gp('title'), login_attr=gp('login_attr'),
                        uid_attr=gp('uid_attr'), users_base=gp('users_base'),
                        users_scope=gp('users_scope'), roles=gp('roles'),
                        groups_base=gp('groups_base'),
                        groups_scope=gp('groups_scope'), binduid=gp('binduid'),
                        bindpwd=gp('bindpwd'),
                        binduid_usage=gp('binduid_usage'),
                        rdn_attr=gp('rdn_attr'), obj_classes=gp('obj_classes'),
                        local_groups=gp('local_groups'), implicit_mapping=1,
                        encryption=gp('encryption'), read_only=gp('read_only'))
        self.assertEqual(gp('_implicit_mapping'), 1)
        mapped_roles = acl._mapRoles(have_roles)
        self.assertEqual(len(mapped_roles), 2)
        for role in have_roles:
            self.assertTrue(role in mapped_roles)
        acl.manage_edit(title=gp('title'), login_attr=gp('login_attr'),
                        uid_attr=gp('uid_attr'), users_base=gp('users_base'),
                        users_scope=gp('users_scope'), roles=gp('roles'),
                        groups_base=gp('groups_base'),
                        groups_scope=gp('groups_scope'), binduid=gp('binduid'),
                        bindpwd=gp('bindpwd'),
                        binduid_usage=gp('binduid_usage'),
                        rdn_attr=gp('rdn_attr'), obj_classes=gp('obj_classes'),
                        local_groups=gp('local_groups'), implicit_mapping=0,
                        encryption=gp('encryption'), read_only=gp('read_only'))
        self.assertEqual(gp('_implicit_mapping'), 0)

    def test_groupMapping(self):
        acl = self.folder.acl_users
        self.assertEqual(len(acl.getGroupMappings()), 0)
        have_roles = ['ldap_group', 'some_group']
        self.assertEqual(acl._mapRoles(have_roles), [])
        acl.manage_addGroupMapping('ldap_group', 'Manager')
        self.assertEqual(len(acl.getGroupMappings()), 1)
        roles = acl._mapRoles(have_roles)
        self.assertEqual(len(roles), 1)
        self.assertTrue('Manager' in roles)
        acl.manage_deleteGroupMappings('unknown')
        self.assertEqual(len(acl.getGroupMappings()), 1)
        acl.manage_deleteGroupMappings(['ldap_group'])
        self.assertEqual(len(acl.getGroupMappings()), 0)
        self.assertEqual(acl._mapRoles(have_roles), [])

    def test_searchGroups(self):
        # test finding a group with specific or wildcard match on
        # multiple attributes
        acl = self.folder.acl_users

        # let's create some users
        acl.manage_addUser(REQUEST=None, kwargs=user2)
        # and put them in groups matching the uniqueMember shortcut in fakeldap
        ldapconn = acl._delegate.connect()
        group_cn = 'group1'
        crippled_cn = group_cn[:-1]
        group_description = 'a description'
        member = 'cn=test2,' + defaults.get('users_base')
        ldapconn.add_s("cn=" + group_cn + "," + defaults.get('groups_base'),
                       dict(objectClass=['groupOfUniqueNames', 'top'],
                            uniqueMember=[member],
                            description=[group_description],
                            mail=['group1@example.com'],
                            ).items())

        # now let's check these groups work
        u = acl.getUser('test2')
        self.assertFalse('Manager' in u.getRoles())
        acl.manage_addGroupMapping(group_cn, 'Manager')
        u = acl.getUser('test2')
        self.assertFalse('Manager' not in u.getRoles())

        # ok, so now we can try group searches by attributes
        # Search on a bogus attribute, must return error result
        result = acl.searchGroups(foobarkey='baz')
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get('cn'), 'n/a')

        # Search valid attribute with invalid term, must return empty result
        result = acl.searchGroups(cn='invalid_cn',
                                  description=group_description)
        self.assertEqual(len(result), 0, result)

        # Search with wildcard - both user_cn and crippled_cn must return
        # the data for user2.
        result = acl.searchGroups(cn=group_cn, description=group_description)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get('cn'), group_cn)

        result = acl.searchGroups(cn=crippled_cn,
                                  description=group_description)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get('cn'), group_cn)

        # Now we ask for exact matches. Only group_cn returns results.
        result = acl.searchGroups(cn=group_cn, description=group_description,
                                  exact_match=True)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].get('cn'), group_cn)

        result = acl.searchGroups(cn=crippled_cn,
                                  description=group_description,
                                  exact_match=True)
        self.assertEqual(len(result), 0)

    def test_groupLifecycle_nonutf8(self):
        # http://www.dataflake.org/tracker/issue_00527
        # Make sure groups with non-UTF8/non-ASCII characters can be
        # added and deleted.
        groupid = 'gr\xc3\xbcppe'  # Latin-1 Umlaut-U
        acl = self.folder.acl_users

        # Add the group with the odd character in it
        acl.manage_addGroup(groupid)
        all_groups = acl.getGroups()

        # Only one group record should exist, the one we just entered
        self.assertTrue(len(all_groups) == 1)
        self.assertTrue(all_groups[0][0] == groupid)

        # Now delete the group. The DN we get back from getGroups will have
        # been recoded into whatever is set in utils.py (normally latin-1).
        # Due to a lack of encoding into UTF-8 in the deletion code, the
        # deletion would fail silently and the group would still exist.
        group_dn = all_groups[0][1]
        acl.manage_deleteGroups(dns=[group_dn])
        self.assertTrue(len(acl.getGroups()) == 0)

    def test_groupsWithCharactersNeedingEscaping(self):
        # http://www.dataflake.org/tracker/issue_00507
        # Make sure groups with hash characters can be
        # added, deleted and used
        groupid = '"#APPLIKATIONEN LAUFWERK(a)#"'
        acl = self.folder.acl_users

        # Add the group with the odd character in it
        acl.manage_addGroup(groupid)
        all_groups = acl.getGroups()

        # Only one group record should exist, the one we just entered
        self.assertTrue(len(all_groups) == 1)
        self.assertTrue(all_groups[0][0] == groupid)

        # Now delete the group.
        group_dn = all_groups[0][1]
        # Shortcoming in fakeldap: DNs are not "unescaped", meaning escaping
        # done during insertion will be retained in the real record, unlike
        # a real LDAP server which will store and return unescaped DNs.
        # That means we cannot use the returned DN, we must construct it anew.
        group_dn = 'cn=%s,%s' % (groupid, acl.groups_base)
        acl.manage_deleteGroups(dns=[group_dn])
        self.assertTrue(len(acl.getGroups()) == 0)
