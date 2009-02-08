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
""" A simple non-persistent user object cache

$Id$
"""

import time

class SimpleCache:
    """ A simple non-persistent cache for user objects """

    def __init__(self):
        """ Initialize a new instance """
        self.cache = {}
        self.timeout = 600


    def set(self, id, object):
        """ Cache an object under the given id """
        id = id.lower()
        self.cache[id] = object


    def get(self, id, password=None):
        """ Retrieve a cached object if it is valid """
        try:
            id = id.lower()
        except AttributeError:
            return None

        user = self.cache.get(id, None)

        if ( password is not None and 
             user is not None and 
             password != user._getPassword() ):
            user = None

        if ( user and 
             (time.time() < user.getCreationTime().timeTime() + self.timeout) ):
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


    def remove(self, id):
        """ Purge a record out of the cache """
        id = id.lower()

        if self.cache.has_key(id):
            del self.cache[id]


    def clear(self):
        """ Clear the internal caches """
        self.cache = {}


    def setTimeout(self, timeout):
        """ Set the timeout (in seconds) for cached entries """
        self.timeout = timeout


class SharedObject:
    """ An even simpler class meant to be used as a cache for non-user-type
    objects """
    def __init__(self):
        self.values = {}

    def set(self, name, value):
        self.values[name] = value

    def get(self, name):
        return self.values.get(name)

    def clear(self, name=None):
        if name:
            try:
                del self.values[name]
            except (KeyError, IndexError):
                pass
        else:
            self.values = {}


