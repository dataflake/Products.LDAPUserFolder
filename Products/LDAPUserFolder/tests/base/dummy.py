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
""" Dummy objects for LDAPUserFolder unit tests
"""

import time

from Acquisition import Implicit
from DateTime.DateTime import DateTime


DN_BASE = 'dc=example,dc=com'


class LDAPDummyUser(Implicit):
    """ LDAP-enabled dummy user """

    def __init__(self, name, password='', roles=(), domains=()):
        self.name = name
        self.__ = password
        self.roles = tuple(roles)
        self.domains = tuple(domains)
        self._created = time.time()

    def getId(self):
        return self.name

    def getUserName(self):
        return self.name

    def getRoles(self):
        return self.roles + ('Authenticated',)

    def getRolesInContext(self, context):
        return self.roles

    def getDomains(self):
        return self.domains

    def getUserDN(self):
        return 'cn=%s,%s' % (self.getId(), DN_BASE)

    def _getPassword(self):
        return self.__

    def getCreationTime(self):
        return DateTime(self._created)

    def allowed(self, context, roles):
        if set(roles).intersection(set(self.roles)):
            return True
        return False


class LDAPDummyUserFolder(Implicit):
    """ LDAP-enabled dummy user folder """

    _rdnattr = 'cn'
    _login_attr = 'cn'
    _schema = {'cn': {'ldap_name': 'cn', 'friendly_name': 'Canonical Name',
                      'public_name': 'fullname', 'multivalued': False},
               'sn': {'ldap_name': 'sn', 'friendly_name': 'Last Name',
                      'multivalued': False},
               'givenName': {'ldap_name': 'givenName',
                             'friendly_name': 'First Name',
                             'multivalued': False},
               'mail': {'ldap_name': 'mail', 'friendly_name': 'Email',
                        'public_name': 'email', 'multivalued': False},
               'telephoneNumber': {'ldap_name': 'telephoneNumber',
                                   'friendly_name': 'Telephone number',
                                   'multivalued': False}}

    def __init__(self):
        self.id = 'acl_users'
        user_foo = LDAPDummyUser('user_foo', roles=['Dummy'])
        setattr(self, 'user_foo', user_foo)
        setattr(self, 'user_bar', LDAPDummyUser('user_bar'))
        omnipotent = LDAPDummyUser('all_powerful_Oz', roles=['Manager'])
        setattr(self, 'all_powerful_Oz', omnipotent)

    def getId(self):
        return self.id

    def getProperty(self, property_name):
        return getattr(self, property_name, None)

    def getGroups(self):
        return (('Role', 'cn=Role,ou=groups,%s' % DN_BASE),
                ('NewRole', 'cn=NewRole,ou=groups,%s' % DN_BASE))

    def manage_addUser(self, REQUEST, kwargs={}):
        user_id = kwargs.get(self._login_attr)
        setattr(self, user_id,
                LDAPDummyUser(user_id, roles=kwargs.get('user_roles', [])))

    def manage_editUser(self, dn, REQUEST=None, kwargs={}):
        user = self.getUserByDN(dn)

        if user is not None:
            for key, value in kwargs.items():
                setattr(user, key, value)

    def manage_editUserPassword(self, dn, password):
        user = self.getUserByDN(dn)

        if user is not None:
            user.__ = password

    def manage_editUserRoles(self, dn, role_dns):
        user = self.getUserByDN(dn)

        if user is not None:
            user.roles = [x[0] for x in self.getGroups() if x[1] in role_dns]

    def manage_deleteUsers(self, dns=[]):
        for dn in dns:
            user = self.getUserByDN(dn)

            if user is not None:
                delattr(self, user.getId())

    def getMappedUserAttrs(self):
        return []

    def getSchemaConfig(self):
        return self._schema

    def getLDAPSchema(self):
        return [(x['ldap_name'], x['friendly_name'])
                for x in self.getSchemaConfig().values()]

    def _expireUser(self, user_ob):
        pass

    def _addUser(self, user_ob):
        setattr(self, user_ob.getId(), user_ob)

    def getUserByDN(self, dn):
        rdn = dn.split(',')[0]
        user_id = rdn.split('=')[1]

        return getattr(self, user_id, None)

    def getUserById(self, id, default=None):
        return getattr(self, id, default)

    def getUser(self, name):
        return getattr(self, name, None)
