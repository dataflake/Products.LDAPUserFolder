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
""" LDAPUserFolder server management tests
"""

from .base.testcase import LDAPTest


class TestServerManagement(LDAPTest):

    def testServerManagement(self):
        acl = self.folder.acl_users
        self.assertEqual(len(acl.getServers()), 1)
        acl.manage_addServer('ldap.some.com', port=636, use_ssl=1)
        self.assertEqual(len(acl.getServers()), 2)
        acl.manage_addServer('ldap.some.com', port='636', use_ssl=1)
        self.assertEqual(len(acl.getServers()), 2)
        acl.manage_addServer('localhost')
        self.assertEqual(len(acl.getServers()), 2)
        acl.manage_deleteServers([1])
        self.assertEqual(len(acl.getServers()), 1)
        acl.manage_deleteServers()
        self.assertEqual(len(acl.getServers()), 1)

        acl.manage_addServer('ldap.some.com', port=636, use_ssl=1)
        svr = [x for x in acl.getServers() if x['host'] == 'ldap.some.com'][0]
        self.assertEqual(svr['conn_timeout'], 5)
        self.assertEqual(svr['op_timeout'], -1)
        acl.manage_addServer('ldap.some.com', port=636, use_ssl=1,
                             op_timeout=10, conn_timeout=15)
        svr = [x for x in acl.getServers() if x['host'] == 'ldap.some.com'][0]
        self.assertEqual(svr['conn_timeout'], 15)
        self.assertEqual(svr['op_timeout'], 10)
