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
""" LDAPUserFolder schema handling tests
"""

from .base.testcase import LDAPTest
from .config import user


class TestSchema(LDAPTest):

    def test_schema(self):
        acl = self.folder.acl_users
        self.assertEqual(len(acl.getLDAPSchema()), 2)
        self.assertEqual(len(acl.getSchemaDict()), 2)
        acl.manage_addLDAPSchemaItem('mail', 'Email', '', 'public')
        self.assertEqual(len(acl.getLDAPSchema()), 3)
        self.assertEqual(len(acl.getSchemaDict()), 3)
        cur_schema = acl.getSchemaConfig()
        self.assertTrue('mail' in cur_schema)
        acl.manage_addLDAPSchemaItem('cn', 'exists', '', 'exists')
        self.assertEqual(len(acl.getLDAPSchema()), 3)
        self.assertEqual(len(acl.getSchemaDict()), 3)
        acl.manage_deleteLDAPSchemaItems(['cn', 'unknown', 'mail'])
        self.assertEqual(len(acl.getLDAPSchema()), 1)
        self.assertEqual(len(acl.getSchemaDict()), 1)
        cur_schema = acl.getSchemaConfig()
        self.assertFalse('mail' in cur_schema)
        self.assertFalse('cn' in cur_schema)

    def test_mapped_attributes(self):
        acl = self.folder.acl_users
        self.assertEqual(len(acl.getMappedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem('mail', 'Email', '', 'public')
        self.assertEqual(len(acl.getMappedUserAttrs()), 1)
        self.assertEqual(acl.getMappedUserAttrs(), (('mail', 'public'),))
        acl.manage_deleteLDAPSchemaItems(['mail'])
        self.assertEqual(len(acl.getMappedUserAttrs()), 0)

    def test_multivalued_attributes(self):
        acl = self.folder.acl_users
        self.assertEqual(len(acl.getMultivaluedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem('mail', 'Email', 'yes', 'public')
        self.assertEqual(len(acl.getMultivaluedUserAttrs()), 1)
        self.assertEqual(acl.getMultivaluedUserAttrs(), ('mail',))

    def test_user_mapped_attributes(self):
        acl = self.folder.acl_users
        self.assertEqual(len(acl.getMappedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem('mail', 'Email', '', 'email')
        for role in user.get('user_roles'):
            acl.manage_addGroup(role)
        acl.manage_addUser(REQUEST=None, kwargs=user)
        user_ob = acl.getUser(user.get(acl.getProperty('_login_attr')))
        self.assertEqual(user.get('mail'), user_ob.getProperty('mail'))
        self.assertEqual(user.get('mail'), user_ob.getProperty('email'))
