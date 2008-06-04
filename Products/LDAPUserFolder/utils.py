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
""" Utility functions and constants

$Id$
"""

import base64
import codecs
import md5
import random
from sets import Set
import sha
import SSHA
import string

#################################################
# "Safe" imports for use in the other modules
#################################################

try:
    import crypt
except ImportError:
    crypt = None

#################################################
# Constants used in other modules
#################################################

BINARY_ATTRIBUTES = ('objectguid', 'jpegphoto')

HTTP_METHODS = ('GET', 'PUT', 'POST')

GROUP_MEMBER_MAP = { 'groupOfUniqueNames' : 'uniqueMember'
                   , 'groupOfNames' : 'member'
                   , 'accessGroup' : 'member'
                   , 'group' : 'member'
                   , 'univentionGroup' : 'uniqueMember'
                   }

VALID_GROUP_ATTRIBUTES = Set(list(GROUP_MEMBER_MAP.values()) +
                             [ 'name'
                             , 'displayName'
                             , 'cn'
                             , 'dn'
                             , 'objectGUID'
                             , 'description'
                             , 'mail'
                             ]
                            )

encoding = 'latin1'


#################################################
# Helper methods for other modules
#################################################

def _verifyUnicode(st):
    """ Verify that the string is unicode """
    if isinstance(st, unicode):
        return st
    else:
        try:
            return unicode(st)
        except UnicodeError:
            return unicode(st, encoding)

def _createLDAPPassword(password, encoding='SHA'):
    """ Create a password string suitable for userPassword """
    if encoding == 'SSHA':
        pwd_str = '{SSHA}' + SSHA.encrypt(password)
    elif encoding == 'crypt':
        saltseeds = list('%s%s' % ( string.lowercase[:26]
                                  , string.uppercase[:26]
                                  ) )
        salt = ''
        for n in range(2):
            salt += random.choice(saltseeds)
        pwd_str = '{crypt}%s' % crypt.crypt(password, salt)
    elif encoding == 'md5':
        m = md5.new(password)
        pwd_str = '{md5}' + base64.encodestring(m.digest())
    elif encoding == 'clear':
        pwd_str = password
    else:
        sha_obj = sha.new(password)
        pwd_str = '{SHA}' + base64.encodestring(sha_obj.digest())

    return pwd_str.strip()


try:
    encodeLocal, decodeLocal, reader = codecs.lookup(encoding)[:3]
    encodeUTF8, decodeUTF8 = codecs.lookup('UTF-8')[:2]

    if getattr(reader, '__module__', '')  == 'encodings.utf_8':
        # Everything stays UTF-8, so we can make this cheaper
        to_utf8 = from_utf8 = str

    else:

        def from_utf8(s):
            return encodeLocal(decodeUTF8(s)[0])[0]

        def to_utf8(s):
            if isinstance(s, str):
                s = decodeLocal(s)[0]
            return encodeUTF8(s)[0]

except LookupError:
    raise LookupError, 'Unknown encoding "%s"' % encoding


def guid2string(val):
    """ convert an active directory binary objectGUID value as returned by
    python-ldap into a string that can be used as an LDAP query value """
    s = ['\\%02X' % ord(x) for x in val]
    return ''.join(s)


############################################################
# LDAP delegate registry
############################################################

delegate_registry = {}

def registerDelegate(name, klass, description=''):
    """ Register delegates that handle the LDAP-related work

    name is a short ID-like moniker for the delegate
    klass is a reference to the delegate class itself
    description is a more verbose delegate description
    """
    delegate_registry[name] = { 'name'        : name
                              , 'klass'       : klass
                              , 'description' : description
                              }

def registeredDelegates():
    """ Return the currently-registered delegates """
    return delegate_registry

def _createDelegate(name='LDAP delegate'):
    """ Create a delegate based on the name passed in """
    default = delegate_registry.get('LDAP delegate')
    info = delegate_registry.get(name, None) or default
    klass = info['klass']
    delegate = klass()

    return delegate
