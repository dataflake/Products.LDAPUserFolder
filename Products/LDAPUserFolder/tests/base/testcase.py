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
""" A test case class for LDAPUserFolder tests
"""

import unittest

from OFS.Folder import Folder
from Testing import ZopeTestCase
import transaction

from dataflake.fakeldap import FakeLDAPConnection

from Products.LDAPUserFolder import LDAPDelegate
from Products.LDAPUserFolder import manage_addLDAPUserFolder
from Products.LDAPUserFolder.tests.config import defaults
from Products.LDAPUserFolder.tests.config import alternates
from Products.LDAPUserFolder.tests.config import user
from Products.LDAPUserFolder.tests.config import user2


LDAPDelegate.c_factory = FakeLDAPConnection
dg = defaults.get
ag = alternates.get
ug = user.get
u2g = user2.get


class LDAPTest(unittest.TestCase):

    def setUp(self):
        from dataflake.fakeldap import TREE
        self.db = TREE
        self.db.clear()
        transaction.begin()
        self.app = self.root = ZopeTestCase.app()
        self.root._setObject('luftest', Folder('luftest'))
        self.folder = self.root.luftest
        manage_addLDAPUserFolder(self.folder)
        luf = self.folder.acl_users
        host, port = dg('server').split(':')
        luf.manage_addServer(host, port=port)
        luf.manage_edit(dg('title'), dg('login_attr'), dg('uid_attr'),
                        dg('users_base'), dg('users_scope'), dg('roles'),
                        dg('groups_base'), dg('groups_scope'), dg('binduid'),
                        dg('bindpwd'), binduid_usage=dg('binduid_usage'),
                        rdn_attr=dg('rdn_attr'),
                        local_groups=dg('local_groups'),
                        implicit_mapping=dg('implicit_mapping'),
                        encryption=dg('encryption'), read_only=dg('read_only'))
        self.db.addTreeItems(dg('users_base'))
        self.db.addTreeItems(dg('groups_base'))

    def tearDown(self):
        transaction.abort()
        ZopeTestCase.close(self.app)
