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
""" Utility functions and constants
"""

import base64
import codecs
from hashlib import md5

from AccessControl import AuthEncoding
from ZPublisher.HTTPRequest import default_encoding


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

GROUP_MEMBER_MAP = {'groupOfUniqueNames': 'uniqueMember',
                    'groupOfNames': 'member',
                    'accessGroup': 'member',
                    'group': 'member',
                    'univentionGroup': 'uniqueMember'}

GROUP_MEMBER_ATTRIBUTES = set(list(GROUP_MEMBER_MAP.values()))

VALID_GROUP_ATTRIBUTES = set(['name', 'displayName', 'cn', 'dn',
                              'objectGUID', 'description',
                              'mail']).union(GROUP_MEMBER_ATTRIBUTES)


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
            return unicode(st, default_encoding)


def _createLDAPPassword(password, encoding='SHA'):
    """ Create a password string suitable for the userPassword attribute
    """
    encoding = encoding.upper()

    if encoding in ('SSHA', 'SHA', 'CRYPT'):
        pwd_str = AuthEncoding.pw_encrypt(password, encoding)
    elif encoding == 'MD5':
        m = md5(password)
        pwd_str = '{MD5}' + base64.encodestring(m.digest())
    elif encoding == 'CLEAR':
        pwd_str = password
    else:
        pwd_str = AuthEncoding.pw_encrypt(password, 'SSHA')

    return pwd_str.strip()


encodeLocal, decodeLocal, reader = codecs.lookup(default_encoding)[:3]
encodeUTF8, decodeUTF8 = codecs.lookup('UTF-8')[:2]

if getattr(reader, '__module__', '') == 'encodings.utf_8':
    # Everything stays UTF-8, so we can make this cheaper
    to_utf8 = from_utf8 = str

else:

    def from_utf8(s):
        return encodeLocal(decodeUTF8(s)[0])[0]

    def to_utf8(s):
        if isinstance(s, str):
            s = decodeLocal(s)[0]
        return encodeUTF8(s)[0]


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
    delegate_registry[name] = {'name': name, 'klass': klass,
                               'description': description}


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
