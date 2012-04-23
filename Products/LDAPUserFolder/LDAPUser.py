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

$Id$
"""

# General Python imports
import time

# Zope imports
from AccessControl.User import BasicUser
from AccessControl.Permissions import access_contents_information
from AccessControl import ClassSecurityInfo
from Acquisition import aq_inner
from Acquisition import aq_parent
from App.class_init import default__class_init__ as InitializeClass
from DateTime import DateTime

# LDAPUserFolder package imports
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

    def __init__( self
                , uid
                , name
                , password
                , roles
                , domains
                , user_dn
                , user_attrs
                , mapped_attrs
                , multivalued_attrs=()
                , ldap_groups=()
                ):
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
    # Overriding these to enable context-based role
    # computation with the LDAPUserSatellite
    #######################################################

    def getRolesInContext(self, object):
        """Return the list of roles assigned to the user,
           including local roles assigned in context of
           the passed in object."""
        roles = BasicUser.getRolesInContext(self, object)

        acl_satellite = self._getSatellite(object)
        if acl_satellite and hasattr(acl_satellite, 'getAdditionalRoles'):
            satellite_roles = acl_satellite.getAdditionalRoles(self)
            roles = list(roles) + satellite_roles

        return roles


    def allowed(self, object, object_roles=None):
        """ Must override, getRolesInContext is not always called """
        if BasicUser.allowed(self, object, object_roles):
            return 1

        acl_satellite = self._getSatellite(object)
        if acl_satellite and hasattr(acl_satellite, 'getAdditionalRoles'):
            satellite_roles = acl_satellite.getAdditionalRoles(self)

            for role in object_roles:
                if role in satellite_roles:
                    if self._check_context(object):
                        return 1

        return 0


    security.declarePrivate('_getSatellite')
    def _getSatellite(self, object):
        """ Get the acl_satellite (sometimes tricky!) """
        while 1:
            acl_satellite = getattr(object, 'acl_satellite', None)
            if acl_satellite is not None:
                return acl_satellite

            parent = aq_parent(aq_inner(object))
            if parent:
                object = parent
                continue

            if hasattr(object, 'im_self'):
                object = aq_inner(object.im_self)
                continue

            break

        return None


    #######################################################
    # Interface unique to the LDAPUser class of user objects
    #######################################################

    security.declareProtected(access_contents_information, '__getattr__')
    def __getattr__(self, name):
        """ Look into the _properties as well... """
        my_props = self._properties

        if my_props.has_key(name):
            prop = my_props.get(name)

            if isinstance(prop, unicode):
                prop = prop.encode(encoding)

            return prop

        else:
            raise AttributeError, name


    security.declareProtected(access_contents_information, 'getProperty')
    def getProperty(self, prop_name, default=''):
        """ 
            Return the user property referred to by prop_name,
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


    def getCreationTime(self):
        """ When was this user object created? """
        return DateTime(self._created)


    def _getLDAPGroups(self):
        """ What groups in LDAP does this user belong to? """
        return tuple(self._ldap_groups)
    

InitializeClass(LDAPUser)
