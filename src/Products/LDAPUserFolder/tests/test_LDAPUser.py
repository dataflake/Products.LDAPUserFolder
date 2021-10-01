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
""" Tests for the LDAPUser class
"""
import os
import unittest

from App.Common import package_home
from DateTime.DateTime import DateTime

from ..LDAPUser import LDAPUser
from .config import defaults
from .config import user


ug = user.get
dg = defaults.get


class TestLDAPUser(unittest.TestCase):

    def setUp(self):
        test_home = package_home(globals())
        image_path = os.path.join(test_home, 'test.jpg')
        image_file = open(image_path, 'rb')
        self.image_contents = image_file.read()
        image_file.close()

        u_attrs = {'cn': [ug('cn')], 'sn': [ug('sn')], 'mail': [ug('mail')],
                   'givenName': [ug('givenName')],
                   'jpegPhoto': [self.image_contents],
                   'objectClasses': ug('objectClasses')}
        self.u_ob = LDAPUser(ug('cn'), ug('mail'), ug('user_pw'),
                             ug('user_roles'), [],
                             'cn=%s,%s' % (ug('cn'),
                                           dg('users_base')), u_attrs,
                             list(ug('mapped_attrs').items()),
                             ug('multivalued_attrs'),
                             ug('binary_attrs'),
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

    def testBinaryAttributes(self):
        # Some attributes are marked binary
        # These must not get encoded by _verifyUnicode
        self.assertTrue(
            self.u_ob._properties['jpegPhoto'] == self.image_contents)

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
