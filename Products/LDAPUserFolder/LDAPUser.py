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
""" LDAP-based user object
"""

import time

from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.User import BasicUser
from AccessControl.Permissions import access_contents_information
from DateTime import DateTime

from Products.LDAPUserFolder.utils import encoding
from Products.LDAPUserFolder.utils import _verifyUnicode


class NonexistingUser:
    """Fake user we can use in our negative cache."""
    def __init__(self):
        self.birth = DateTime()

    def getCreationTime(self):
        return self.birth

    def _getPassword(self):
        return None


class LDAPUser(BasicUser):
    """ A user object for LDAP users """
    security = ClassSecurityInfo()
    _properties = None

    def __init__(self, uid, name, password, roles, domains, user_dn,
                 user_attrs, mapped_attrs, multivalued_attrs=(),
                 ldap_groups=()):
        """ Instantiate a new LDAPUser object """
        self._properties = {}
        self.id = _verifyUnicode(uid)
        self.name = _verifyUnicode(name)
        self.__ = password
        self._dn = _verifyUnicode(user_dn)
        self.roles = roles
        self.domains = []
        self._ldap_groups = ldap_groups
        self.RID = ''
        self.groups = ''
        now = time.time()
        self._created = now

        for key in user_attrs.keys():
            if key in multivalued_attrs:
                prop = user_attrs.get(key, [None])
            else:
                prop = user_attrs.get(key, [None])[0]

            if isinstance(prop, str) and key != 'objectGUID':
                prop = _verifyUnicode(prop)

            self._properties[key] = prop

        for att_name, map_name in mapped_attrs:
            self._properties[map_name] = self._properties.get(att_name)

        self._properties['dn'] = user_dn

    ######################################################
    # Distinguish between user id and name
    #######################################################

    security.declarePublic('getId')

    def getId(self):
        if isinstance(self.id, unicode):
            return self.id.encode(encoding)

        return self.id

    ######################################################
    # User interface not implemented in class BasicUser
    #######################################################

    security.declarePrivate('_getPassword')

    def _getPassword(self):
        """ Retrieve the password """
        return self.__

    security.declarePublic('getUserName')

    def getUserName(self):
        """ Get the name associated with this user """
        if isinstance(self.name, unicode):
            return self.name.encode(encoding)

        return self.name

    security.declarePublic('getRoles')

    def getRoles(self):
        """ Return the user's roles """
        if self.name == 'Anonymous User':
            return tuple(self.roles)
        else:
            return tuple(self.roles) + ('Authenticated',)

    security.declarePublic('getDomains')

    def getDomains(self):
        """ The user's domains """
        return self.domains

    #######################################################
    # Interface unique to the LDAPUser class of user objects
    #######################################################

    security.declareProtected(access_contents_information, '__getattr__')

    def __getattr__(self, name):
        """ Look into the _properties as well... """
        my_props = self._properties

        if name in my_props:
            prop = my_props.get(name)

            if isinstance(prop, unicode):
                prop = prop.encode(encoding)

            return prop

        else:
            raise AttributeError(name)

    security.declareProtected(access_contents_information, 'getProperty')

    def getProperty(self, prop_name, default=''):
        """ Return the user property referred to by prop_name,
            if the attribute is indeed public.
        """
        prop = self._properties.get(prop_name, default)
        if isinstance(prop, unicode):
            prop = prop.encode(encoding)

        return prop

    security.declareProtected(access_contents_information, 'getUserDN')

    def getUserDN(self):
        """ Return the user's full Distinguished Name """
        if isinstance(self._dn, unicode):
            return self._dn.encode(encoding)

        return self._dn

    security.declareProtected(access_contents_information, 'getCreationTime')

    def getCreationTime(self):
        """ When was this user object created? """
        return DateTime(self._created)

    def _getLDAPGroups(self):
        """ What groups in LDAP does this user belong to? """
        return tuple(self._ldap_groups)


InitializeClass(LDAPUser)
