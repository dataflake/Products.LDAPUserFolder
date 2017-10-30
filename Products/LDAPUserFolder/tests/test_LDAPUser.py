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
""" Tests for the LDAPUser class
"""

import unittest

from DateTime.DateTime import DateTime

from Products.LDAPUserFolder.LDAPUser import LDAPUser
from Products.LDAPUserFolder.tests.config import user
from Products.LDAPUserFolder.tests.config import defaults

ug = user.get
dg = defaults.get


class TestLDAPUser(unittest.TestCase):

    def setUp(self):
        u_attrs = {'cn': [ug('cn')], 'sn': [ug('sn')], 'mail': [ug('mail')],
                   'givenName': [ug('givenName')],
                   'objectClasses': ug('objectClasses')}
        self.u_ob = LDAPUser(ug('cn'), ug('mail'), ug('user_pw'),
                             ug('user_roles'), [], 'cn=%s,%s' % (ug('cn'),
                             dg('users_base')), u_attrs,
                             list(ug('mapped_attrs').items()),
                             ug('multivalued_attrs'),
                             ldap_groups=ug('ldap_groups'))

    def testLDAPUserInstantiation(self):
        ae = self.assertEqual
        u = self.u_ob
        ae(u.getProperty('cn'), ug('cn'))
        ae(u.getProperty('sn'), ug('sn'))
        ae(u.getProperty('mail'), ug('mail'))
        ae(u.getProperty('givenName'), ug('givenName'))
        ae(u._getPassword(), ug('user_pw'))
        ae(u.getId(), ug('cn'))
        ae(u.getUserName(), ug('mail'))
        for role in ug('user_roles'):
            self.assertTrue(role in u.getRoles())
        self.assertTrue('Authenticated' in u.getRoles())
        ae(u.getProperty('dn'), 'cn=%s,%s' % (ug('cn'), dg('users_base')))
        ae(u.getUserDN(), 'cn=%s,%s' % (ug('cn'), dg('users_base')))
        ae(u._getLDAPGroups(), tuple(ug('ldap_groups')))
        self.assertTrue(DateTime() >= u.getCreationTime())

    def testUnicodeAttributes(self):
        # Internally, most attributes are stored as unicode.
        # Test some to make sure.
        self.assertTrue(isinstance(self.u_ob.id, unicode))
        self.assertTrue(isinstance(self.u_ob.name, unicode))
        self.assertTrue(isinstance(self.u_ob._properties['givenName'],
                        unicode))

    def testMappedAttrs(self):
        ae = self.assertEqual
        u = self.u_ob
        attr_map = ug('mapped_attrs')

        for key, mapped_key in attr_map.items():
            ae(u.getProperty(key), u.getProperty(mapped_key))

    def testMultivaluedAttributes(self):
        u = self.u_ob
        multivals = ug('multivalued_attrs')

        for mv in multivals:
            self.assertTrue(isinstance(u.getProperty(mv), (list, tuple)))

    def testNameIdNotUnicode(self):
        # Make sure name and ID are never unicode
        u = self.u_ob
        self.assertFalse(isinstance(u.getUserName(), unicode))
        self.assertFalse(isinstance(u.getId(), unicode))
