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
""" A simple non-persistent user object cache
"""

import time
from threading import Lock

from dataflake.cache.timeout import TimeoutCache


_caches = {}
_cache_lock = Lock()


class UserCache(TimeoutCache):
    """ A simple non-persistent cache for user objects """

    def get(self, id, password=None):
        """ Retrieve a cached object if it is valid """
        user = super(UserCache, self).get(id)

        if password is not None and \
           user is not None and \
           password != user._getPassword():
            user = None

        if user and \
           (time.time() < user.getCreationTime().timeTime() + self.timeout):
            return user
        else:
            return None

    def getCache(self):
        """ Get valid cache records """
        valid = []
        cached = self.cache.values()
        now = time.time()

        for object in cached:
            created = object.getCreationTime().timeTime()
            if object and now < (created + self.timeout):
                valid.append(object)

        return valid


def getResource(id, factory=None, factoryArgs=()):
    """returns a resource for *id*.

    If such a resource does not yet exist, one is created
    by calling *factory* with *factoryArgs*.
    Note, that *factory* and *factoryArgs* should only
    depend on *id* and not any other context, as no
    object is created, when a resource for *id* already
    exists.
    """
    _cache_lock.acquire()

    try:
        try:
            return _caches[id]
        except KeyError:
            if factory is not None:
                _caches[id] = factory(*factoryArgs)
                return _caches[id]
    finally:
        _cache_lock.release()


def setResource(id, resource):
    """ Forcibly set the resource """
    _cache_lock.acquire()

    try:
        _caches[id] = resource
    finally:
        _cache_lock.release()


def removeResource(id):
    """ Forcibly remove a shared resource
    """
    _cache_lock.acquire()

    try:
        del _caches[id]
    except KeyError:
        pass
    finally:
        _cache_lock.release()
