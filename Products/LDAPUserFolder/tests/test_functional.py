##############################################################################
#
# Copyright (c) 2000-2008 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Functional tests for adding CMF members

$Id: __init__.py 58 2008-05-28 21:33:24Z jens $
"""

from unittest import main
from unittest import makeSuite
from unittest import TestCase
from unittest import TestSuite

import Testing
import Zope2
Zope2.startup()

try:
    from Products.CMFCore.tests.base.testcase import RequestTest
    from Products.CMFDefault.tests.test_join import MembershipTests
    from Products.LDAPUserFolder.tests.base.dummy import LDAPDummyUserFolder
    from Products.LDAPUserFolder.tests.base.dummy import LDAPDummyUser
except ImportError:
    RequestTest = MembershipTests = TestCase


class LDAPMembershipTests(MembershipTests):

    def setUp(self):
        MembershipTests.setUp(self)

        if getattr(self, 'app', None) is not None:
            # Running under CMF >= 2.1, need to set up a site
            self._mungeSite(self.app.site)


    def _makePortal(self):
        if getattr(self, 'app', None) is not None:
            # Running under CMF >= 2.1, this is a no-op since the portal is
            # already set up the way it is supposed to be.
            return self.app.site

        site = MembershipTests._makePortal(self)

        return self._mungeSite(site)
            

    def _mungeSite(self, site):
        # Load the LDAPUserFolder:default extension profile and run it
        profile_id = 'profile-LDAPUserFolder:default'
        try:
            site.portal_setup.runAllImportStepsFromProfile(profile_id)
        except AttributeError:
            # BBB GenericSetup < 1.3
            site.portal_setup.setImportContext(profile_id)
            site.portal_setup.runAllImportSteps()
    
        # Remove the "standard" user folder and replace it with a
        # LDAPDummyUserFolder
        site.manage_delObjects(['acl_users'])
        site._setObject('acl_users', LDAPDummyUserFolder())

        # Register one new attribute for testing
        site.portal_memberdata.addMemberProperty('sn')

        return site


    def test_join_rdn_not_login( self ):
        # Test joing for situations where the login attribute is not the
        # same as the RDN attribute
        site = self._makePortal()
        site.acl_users._login_attr = 'sn'
        member_id = 'MyLastName'

        # If the RDN attribute is not provided, a ValueError is raised
        self.assertRaises( ValueError
                         , site.portal_registration.addMember
                         , member_id
                         , 'zzyyxx'
                         , properties={ 'username': member_id
                                      , 'email' : 'foo@bar.com'
                                      }
                         )
        u = site.acl_users.getUser(member_id)
        self.failIf(u)

        # We provide it, so this should work
        site.portal_registration.addMember( member_id
                                          , 'zzyyzz'
                                          , properties={ 'username': member_id
                                                       , 'email' : 'foo@bar.com'
                                                       , 'cn' : 'someuser'
                                                       }
                                          )
        u = site.acl_users.getUser(member_id)
        self.failUnless(u)


def test_suite():
    try:
        from Products import CMFCore

        return TestSuite((
            makeSuite(LDAPMembershipTests),
            ))
    except ImportError:
        # No CMF, no tests.
        return TestSuite(())

if __name__ == '__main__':
    main(defaultTest='test_suite')
