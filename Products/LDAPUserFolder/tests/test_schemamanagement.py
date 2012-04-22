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
""" LDAPUserFolder schema handling tests

$Id$
"""

import unittest

from Products.LDAPUserFolder.tests.base.testcase import LDAPTest
from Products.LDAPUserFolder.tests.config import user

class TestSchema(LDAPTest):

    def test_schema(self):
        acl = self.folder.acl_users
        self.assertEquals(len(acl.getLDAPSchema()), 2)
        self.assertEquals(len(acl.getSchemaDict()), 2)
        acl.manage_addLDAPSchemaItem( 'mail'
                                    , 'Email'
                                    , ''
                                    , 'public'
                                    )
        self.assertEquals(len(acl.getLDAPSchema()), 3)
        self.assertEquals(len(acl.getSchemaDict()), 3)
        cur_schema = acl.getSchemaConfig()
        self.failUnless('mail' in cur_schema.keys())
        acl.manage_addLDAPSchemaItem( 'cn'
                                    , 'exists'
                                    , ''
                                    , 'exists'
                                    )
        self.assertEquals(len(acl.getLDAPSchema()), 3)
        self.assertEquals(len(acl.getSchemaDict()), 3)
        acl.manage_deleteLDAPSchemaItems(['cn', 'unknown', 'mail'])
        self.assertEquals(len(acl.getLDAPSchema()), 1)
        self.assertEquals(len(acl.getSchemaDict()), 1)
        cur_schema = acl.getSchemaConfig()
        self.failIf('mail' in cur_schema.keys())
        self.failIf('cn' in cur_schema.keys())

    def test_mapped_attributes(self):
        acl = self.folder.acl_users
        self.assertEquals(len(acl.getMappedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem( 'mail'
                                    , 'Email'
                                    , ''
                                    , 'public'
                                    )
        self.assertEquals(len(acl.getMappedUserAttrs()), 1)
        self.assertEquals(acl.getMappedUserAttrs(), (('mail', 'public'),))
        acl.manage_deleteLDAPSchemaItems(['mail'])
        self.assertEquals(len(acl.getMappedUserAttrs()), 0)

    def test_multivalued_attributes(self):
        acl = self.folder.acl_users
        self.assertEquals(len(acl.getMultivaluedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem( 'mail'
                                    , 'Email'
                                    , 'yes'
                                    , 'public'
                                    )
        self.assertEquals(len(acl.getMultivaluedUserAttrs()), 1)
        self.assertEquals(acl.getMultivaluedUserAttrs(), ('mail',))

    def test_user_mapped_attributes(self):
        acl = self.folder.acl_users
        self.assertEquals(len(acl.getMappedUserAttrs()), 0)
        acl.manage_addLDAPSchemaItem( 'mail'
                                    , 'Email'
                                    , ''
                                    , 'email'
                                    )
        for role in user.get('user_roles'):
            acl.manage_addGroup(role)
        msg = acl.manage_addUser(REQUEST=None, kwargs=user)
        user_ob = acl.getUser(user.get(acl.getProperty('_login_attr')))
        self.assertEqual(user.get('mail'), user_ob.getProperty('mail'))
        self.assertEqual(user.get('mail'), user_ob.getProperty('email'))


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestSchema),
        ))

