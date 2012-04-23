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
""" LDAPUserSatellite tests

$Id$
"""

# General Python imports
import unittest

# Zope imports
from OFS.Folder import manage_addFolder

# LDAPUserFolder package imports
from Products.LDAPUserFolder import manage_addLDAPUserSatellite
from Products.LDAPUserFolder.tests.base.testcase import LDAPTest
from Products.LDAPUserFolder.tests.config import user
from Products.LDAPUserFolder.tests.config import satellite_defaults
ug = user.get
sg = satellite_defaults.get

class TestLDAPUserSatellite(LDAPTest):

    def setUp(self):
        super(TestLDAPUserSatellite, self).setUp()
        luf = self.folder.acl_users
        luf._implicit_mapping = True

        self.db.addTreeItems(sg('groups_base'))
        manage_addFolder(self.folder, 'lustest')
        self.lustest = self.folder.lustest
        manage_addLDAPUserSatellite( self.lustest
                                   , sg('luf')
                                   , sg('title')
                                   , sg('recurse')
                                   )
        self.lus = self.lustest.acl_satellite
        acl = self.folder.acl_users
        for role in ug('user_roles'):
            acl.manage_addGroup(role)
        for group in ug('ldap_groups'):
            acl.manage_addGroup(group)
        acl.manage_addUser(REQUEST=None, kwargs=user)

    def testInstantiation(self):
        lus = getattr(self.lustest, 'acl_satellite').__of__(self.lustest)
        ae = self.assertEqual
        ae(lus._luf, sg('luf'))
        ae(lus.title, sg('title'))
        ae(lus.recurse, sg('recurse'))
        ae(len(lus.getCache()), 0)
        ae(len(lus.getGroupMappings()), 0)
        ae(len(lus.getGroups()), 0)
        ae(len(lus.getGroupedUsers()), 0)
        luf = lus.getLUF()
        ae('/'.join(luf.getPhysicalPath()), sg('luf'))

    def testEdit(self):
        lus = self.lus
        ae = self.assertEqual
        lus.manage_edit( '/acl_users'
                       , sg('groups_base')
                       , sg('groups_scope')
                       , title='New Title'
                       , recurse=1
                       )
        ae(lus.title, 'New Title')
        ae(lus.recurse, 1)
        ae(lus._luf, '/acl_users')
        ae(lus.groups_base, sg('groups_base'))
        ae(lus.groups_scope, sg('groups_scope'))


    def testRoleMapping(self):
        lus = self.lus
        ae = self.assertEqual
        ae(len(lus.getGroupMappings()), 0)
        lus.manage_addGroupMapping('Manager', ['Privileged'])
        lus.manage_addGroupMapping('Group2', ['MorePrivileged'])
        ae(len(lus.getGroupMappings()), 2)
        user = self.folder.acl_users.getUser('test')
        # Nasty quick hack
        user._ldap_groups = ug('ldap_groups')
        roles = lus.getAdditionalRoles(user)
        ae(len(lus.getCache()), 1)
        ae(roles, ['MorePrivileged', 'Privileged'])
        lus.manage_deleteGroupMappings(['Manager'])
        lus.manage_deleteGroupMappings(['Group2'])
        ae(len(lus.getGroupMappings()), 0)
        roles = lus.getAdditionalRoles(user)
        ae(len(roles), 0)

    def testLDAPRoleAdding(self):
        lus = self.lus
        ae = self.assertEqual
        acl = lus.getLUF()
        user = self.folder.acl_users.getUser('test')
        acl._delegate.insert( sg('groups_base')
                            , 'cn=Privileged'
                            , { 'objectClass' : ['top', 'groupOfUniqueNames']
                              , 'cn' : ['Privileged']
                              , 'uniqueMember' : user.getUserDN()
                              }
                            )
        lus.manage_edit( sg('luf')
                       , sg('groups_base')
                       , sg('groups_scope')
                       )
        ae(len(lus.getGroups()), 1)
        roles = lus.getAdditionalRoles(user)
        ae(roles, ['Privileged'])
        ae(len(lus.getGroupedUsers()), 1)
        ae(len(lus.getCache()), 1)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(TestLDAPUserSatellite))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

