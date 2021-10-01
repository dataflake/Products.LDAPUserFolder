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
""" Tests for the UserCache class
"""

import threading
import time
import unittest

from DateTime.DateTime import DateTime

from ..cache import getResource


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
        from ..cache import UserCache
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


class TestGetSetRemoveResource(unittest.TestCase):

    def setUp(self):
        self.test_id = 'test_id'

    def tearDown(self):
        from ..cache import removeResource
        removeResource(self.test_id)

    def test_getResource(self):
        self.assertEqual(getResource(self.test_id, str, ('foobar',)), 'foobar')

    def test_getResource_nofactory(self):
        self.assertIsNone(getResource(self.test_id))
        getResource(self.test_id, str, ('foobar',))
        self.assertEqual(getResource(self.test_id), 'foobar')

    def test_setResource(self):
        from ..cache import setResource
        self.assertIsNone(getResource(self.test_id))
        setResource(self.test_id, 'forced')
        self.assertEqual(getResource(self.test_id), 'forced')

    def test_removeResource(self):
        from ..cache import removeResource
        from ..cache import setResource
        setResource(self.test_id, 'forced')
        self.assertEqual(getResource(self.test_id), 'forced')

        removeResource(self.test_id)
        self.assertIsNone(getResource(self.test_id))


class TestThreadSafety(unittest.TestCase):

    def setUp(self):
        from dataflake.cache.simple import SimpleCache
        self.c_class = SimpleCache
        self.c_name = 'cache_id'
        self.c_key = 'testkey'

    def test_getResource_threaded(self):
        threads = [CacheThread(self.c_class, self.c_name, self.c_key)
                   for x in range(100)]
        [x.start() for x in threads]
        while len(threading.enumerate()) > 1:
            time.sleep(.1)
        cache = getResource(self.c_name, self.c_class)
        # We accept results that prove a correct cache rate of 99%,
        # up to 100 less than the ideal count of 10000
        self.assertAlmostEqual(cache.get(self.c_key), 10000, delta=100)


class CacheThread(threading.Thread):

    def __init__(self, cache_class, cache_name, cache_key):
        super(CacheThread, self).__init__()
        self.cache_class = cache_class
        self.cache_name = cache_name
        self.cache_key = cache_key

    def run(self):
        for i in range(100):
            cache = getResource(self.cache_name, self.cache_class)
            cache.set(self.cache_key, (cache.get(self.cache_key) or 0) + 1)
