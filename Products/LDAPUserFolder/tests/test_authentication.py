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
""" LDAPUserFolder authentication tests

$Id$
"""

import unittest

from Products.LDAPUserFolder.tests.base.testcase import LDAPTest
from Products.LDAPUserFolder.tests.config import user
ug = user.get

class TestAuthentication(LDAPTest):

    def testAuthenticateUser(self):
        acl = self.folder.acl_users
        for role in user.get('user_roles'):
            acl.manage_addGroup(role)
        acl.manage_addUser(REQUEST=None, kwargs=user)
        user_ob = acl.authenticate( user.get(acl.getProperty('_login_attr'))
                                  , user.get('user_pw')
                                  , {}
                                  )
        self.failIf(user_ob is None)
        user_ob = acl.authenticate( "%s " % # extra space after login attr
                                    user.get(acl.getProperty('_login_attr'))
                                  , user.get('user_pw')
                                  , {}
                                  )
        self.failIf(user_ob is None)
        user_ob = acl.authenticate( " %s" % # extra space before login attr
                                    user.get(acl.getProperty('_login_attr'))
                                  , user.get('user_pw')
                                  , {}
                                  )
        self.failIf(user_ob is None)
        user_ob = acl.authenticate( " %s " % # extra spaces around login attr
                                    user.get(acl.getProperty('_login_attr'))
                                  , user.get('user_pw')
                                  , {}
                                  )
        self.failIf(user_ob is None)
        user_ob = acl.authenticate( user.get(acl.getProperty('_login_attr'))
                                  , ''
                                  , {}
                                  )
        self.failUnless(user_ob is None)
        user_ob = acl.authenticate( user.get(acl.getProperty('_login_attr'))
                                  , 'falsepassword'
                                  , {}
                                  )
        self.failUnless(user_ob is None)

    def testAuthenticateUserWithCache(self):
        acl = self.folder.acl_users
        for role in user.get('user_roles'):
            acl.manage_addGroup(role)
        acl.manage_addUser(REQUEST=None, kwargs=user)

        user_ob = acl.authenticate( user.get(acl.getProperty('_login_attr'))
                                  , 'falsepassword'
                                  , {}
                                  )

        # make sure the user could not connect
        self.failUnless(user_ob is None)

        # now let's try again with the right password
        user_ob = acl.authenticate( user.get(acl.getProperty('_login_attr'))
                                  , user.get('user_pw')
                                  , {}
                                  )
    
        # now we should be OK
        self.failIf(user_ob is None)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestAuthentication),
        ))

