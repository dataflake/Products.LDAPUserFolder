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
""" LDAPUserFolder authentication tests
"""

from .base.testcase import LDAPTest
from .config import user


ug = user.get


class TestAuthentication(LDAPTest):

    def testAuthenticateUser(self):
        acl = self.folder.acl_users
        for role in user.get('user_roles'):
            acl.manage_addGroup(role)
        acl.manage_addUser(REQUEST=None, kwargs=user)

        # Correct login
        user_ob = acl.authenticate(user.get(acl.getProperty('_login_attr')),
                                   user.get('user_pw'), {})
        self.assertIsNotNone(user_ob)

        # Login with empty password
        user_ob = acl.authenticate(user.get(acl.getProperty('_login_attr')),
                                   '', {})
        self.assertIsNone(user_ob)

        # Login with wrong password
        user_ob = acl.authenticate(user.get(acl.getProperty('_login_attr')),
                                   'falsepassword', {})
        self.assertIsNone(user_ob)

        # Extra space after login attr - should not fail
        login = '%s ' % user.get(acl.getProperty('_login_attr'))
        user_ob = acl.authenticate(login, user.get('user_pw'), {})
        self.assertIsNotNone(user_ob)

        # extra space before login attr - should not fail
        login = ' %s' % user.get(acl.getProperty('_login_attr'))
        user_ob = acl.authenticate(login, user.get('user_pw'), {})
        self.assertIsNotNone(user_ob)

        # Extra spaces around login attr - should not fail
        login = ' %s ' % user.get(acl.getProperty('_login_attr'))
        user_ob = acl.authenticate(login, user.get('user_pw'), {})
        self.assertIsNotNone(user_ob)

    def testAuthenticateUserWithCache(self):
        acl = self.folder.acl_users
        for role in user.get('user_roles'):
            acl.manage_addGroup(role)
        acl.manage_addUser(REQUEST=None, kwargs=user)

        user_ob = acl.authenticate(user.get(acl.getProperty('_login_attr')),
                                   'falsepassword', {})

        # make sure the user could not connect
        self.assertIsNone(user_ob)

        # now let's try again with the right password
        user_ob = acl.authenticate(user.get(acl.getProperty('_login_attr')),
                                   user.get('user_pw'), {})

        # now we should be OK
        self.assertIsNotNone(user_ob)
