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
""" Tests for the UserCache class
"""

import time
import unittest

from DateTime.DateTime import DateTime


TESTPWD = 'test'


class CacheObject:

    def __init__(self, id):
        self.id = id
        self._created = time.time()

    def _getPassword(self):
        return TESTPWD

    def getCreationTime(self):
        return DateTime(self._created)


class TestUserCache(unittest.TestCase):

    def setUp(self):
        from Products.LDAPUserFolder.cache import UserCache
        self.cache = UserCache()
        self.cache.setTimeout(0.1)

    def testInstantiation(self):
        self.assertEqual(len(self.cache.getCache()), 0)

    def testCaching(self):
        nonauth_ob = CacheObject('nonauth')
        self.cache.set('TestId', nonauth_ob)
        self.assertEqual(len(self.cache.getCache()), 1)
        self.assertEqual(self.cache.get('testid', password=None), nonauth_ob)
        time.sleep(0.5)
        self.assertEqual(self.cache.get('testid', password=None), None)
        self.assertEqual(len(self.cache.getCache()), 0)
        auth_ob = CacheObject('auth')
        self.cache.set('NewId', auth_ob)
        self.assertEqual(len(self.cache.getCache()), 1)
        self.assertEqual(self.cache.get('newid', password=TESTPWD), auth_ob)
        time.sleep(0.5)
        self.assertEqual(self.cache.get('newid', password=TESTPWD), None)
        self.assertEqual(len(self.cache.getCache()), 0)

    def testRemove(self):
        nonauth_ob = CacheObject('nonauth')
        self.cache.set('TestId', nonauth_ob)
        self.cache.invalidate('testid')
        self.assertEqual(len(self.cache.getCache()), 0)
        auth_ob = CacheObject('auth')
        self.cache.set('NewId', auth_ob)
        self.cache.invalidate('newid')
        self.assertEqual(len(self.cache.getCache()), 0)

    def testClear(self):
        nonauth_ob = CacheObject('nonauth')
        self.cache.set('TestId', nonauth_ob)
        auth_ob = CacheObject('auth')
        self.cache.set('NewId', auth_ob)
        self.cache.invalidate()
        self.assertEqual(len(self.cache.getCache()), 0)
        self.assertEqual(len(self.cache.getCache()), 0)
