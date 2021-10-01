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
""" The LDAPUserFolder class
"""

import logging
import os
import random
import time
import urllib
from hashlib import sha1

from AccessControl import ClassSecurityInfo
from AccessControl.class_init import InitializeClass
from AccessControl.Permissions import manage_users
from AccessControl.Permissions import view_management_screens
from AccessControl.SecurityManagement import getSecurityManager
from AccessControl.users import domainSpecMatch
from Acquisition import aq_base
from App.Common import package_home
from App.special_dtml import DTMLFile
from BTrees.OOBTree import OOBTree
from OFS.SimpleItem import SimpleItem
from OFS.userfolder import BasicUserFolder
from zope.interface import implementer

from dataflake.cache.simple import SimpleCache

from .cache import UserCache
from .cache import getResource
from .interfaces import ILDAPUserFolder
from .LDAPUser import LDAPUser
from .LDAPUser import NonexistingUser
from .permissions import change_ldapuserfolder
from .utils import GROUP_MEMBER_ATTRIBUTES
from .utils import GROUP_MEMBER_MAP
from .utils import VALID_GROUP_ATTRIBUTES
from .utils import _createDelegate
from .utils import _createLDAPPassword
from .utils import crypt
from .utils import guid2string
from .utils import to_utf8


logger = logging.getLogger('event.LDAPUserFolder')
_marker = []
_dtmldir = os.path.join(package_home(globals()), 'dtml')


@implementer(ILDAPUserFolder)
class LDAPUserFolder(BasicUserFolder):
    """ LDAPUserFolder

        The LDAPUserFolder is a user database.  It contains management
        hooks so that it can be added to a Zope folder as an 'acl_users'
        database.  Its important public method is validate() which
        returns a Zope user object of type LDAPUser
    """

    security = ClassSecurityInfo()

    meta_type = 'LDAPUserFolder'
    id = 'acl_users'
    isAUserFolder = 1
    isPrincipiaFolderish = 1
    zmi_icon = 'fas fa-users-cog'
    zmi_show_add_dialog = False

    #################################################################
    #
    # Setting up all ZMI management screens and default login pages
    #
    #################################################################

    manage_options = (
        ({'label': 'Configure', 'action': 'manage_main'},
         {'label': 'LDAP Servers',  'action': 'manage_servers'},
         {'label': 'LDAP Schema', 'action': 'manage_ldapschema'},
         {'label': 'Caches', 'action': 'manage_cache'},
         {'label': 'Users', 'action': 'manage_userrecords'},
         {'label': 'Groups',
          'action': 'manage_grouprecords'}) + SimpleItem.manage_options)

    security.declareProtected(view_management_screens, 'manage')
    security.declareProtected(view_management_screens, 'manage_main')
    manage = manage_main = DTMLFile('dtml/properties', globals())
    manage_main._setName('manage_main')

    security.declareProtected(view_management_screens, 'manage_servers')
    manage_servers = DTMLFile('dtml/servers', globals())

    security.declareProtected(view_management_screens, 'manage_ldapschema')
    manage_ldapschema = DTMLFile('dtml/ldapschema', globals())

    security.declareProtected(view_management_screens, 'manage_cache')
    manage_cache = DTMLFile('dtml/cache', globals())

    security.declareProtected(view_management_screens, 'manage_userrecords')
    manage_userrecords = DTMLFile('dtml/users', globals())

    security.declareProtected(view_management_screens, 'manage_grouprecords')
    manage_grouprecords = DTMLFile('dtml/groups', globals())

    #################################################################
    #
    # Initialization code
    #
    #################################################################

    def __init__(self, delegate_type='LDAP delegate'):
        """ Create a new LDAPUserFolder instance """
        self._hash = '%s%s' % (self.meta_type, str(random.random()))
        self._delegate = _createDelegate(delegate_type)
        self._ldapschema = {'cn': {'ldap_name': 'cn',
                                   'friendly_name': 'Canonical Name',
                                   'multivalued': False,
                                   'public_name': '',
                                   'binary': False},
                            'sn': {'ldap_name': 'sn',
                                   'friendly_name': 'Last Name',
                                   'multivalued': False,
                                   'public_name': '',
                                   'binary': False}}

        # Local DN to role tree for storing roles
        self._groups_store = OOBTree()
        # List of additionally known roles
        self._additional_groups = []
        # Place to store mappings from LDAP group to Zope role
        self._groups_mappings = {}

        # Caching-related
        self._anonymous_timeout = 600
        self._authenticated_timeout = 600

        # Set up some safe defaults
        self.title = ''
        self._login_attr = 'cn'
        self._uid_attr = ''
        self._bindpwd = ''
        self._rdnattr = ''
        self.users_base = 'ou=people,dc=mycompany,dc=com'
        self._user_objclasses = ['top', 'person']
        self._binduid = ''
        self._binduid_usage = 0
        self.users_scope = 2
        self.groups_base = 'ou=groups,dc=mycompany,dc=com'
        self.groups_scope = 2
        self._local_groups = False
        self._roles = ['Anonymous']
        self._implicit_mapping = False
        self._pwd_encryption = 'SHA'
        self.read_only = False
        self._extra_user_filter = ''

    def _clearCaches(self):
        """ Clear all logs and caches for user-related information """
        self._cache('anonymous').invalidate()
        self._cache('authenticated').invalidate()
        self._cache('negative').invalidate()
        self._misc_cache().invalidate()

    def _lookupuserbyattr(self, name, value, pwd=None):
        """
            returns a record's DN and the groups a uid belongs to
            as well as a dictionary containing user attributes
        """
        users_base = self.users_base

        if name == 'dn':
            if value.find(',') == -1:
                # micro-optimization: this is not a valid dn because it
                # doesn't contain any commas; don't bother trying to look it
                # up
                msg = '_lookupuserbyattr: not a valid dn "%s"' % value
                logger.debug(msg)
                return None, None, None, None

            users_base = to_utf8(value)
            search_str = '(objectClass=*)'
        elif name == 'objectGUID':
            # we need to convert the GUID to a specially formatted string
            # for the query to work
            value = guid2string(value)
            # we can't escape the objectGUID query piece using filter_format
            # because it replaces backslashes, which we need as a result
            # of guid2string
            ob_flt = ['(%s=%s)' % (name, value)]
            search_str = self._getUserFilterString(filters=ob_flt)
        else:
            ob_flt = [self._delegate.filter_format('(%s=%s)', (name, value))]
            search_str = self._getUserFilterString(filters=ob_flt)

        # Step 1: Bind either as the Manager or anonymously to look
        #         up the user from the login given
        if self._binduid_usage > 0:
            bind_dn = self._binduid
            bind_pwd = self._bindpwd
        else:
            bind_dn = bind_pwd = ''

        # If you want to log the password as well, which can introduce
        # security problems, uncomment the next lines and comment out
        # the line after that, then restart Zope.
        logger.debug('_lookupuserbyattr: Binding as "%s"' % bind_dn)
        logger.debug('_lookupuserbyattr: Using filter "%s"' % search_str)

        known_attrs = list(self.getSchemaConfig().keys())

        res = self._delegate.search(base=users_base, scope=self.users_scope,
                                    filter=search_str, attrs=known_attrs,
                                    bind_dn=bind_dn, bind_pwd=bind_pwd)

        if res['size'] == 0 or res['exception']:
            msg = '_lookupuserbyattr: No user "%s=%s" (%s)' % (
                name, value, res['exception'] or 'n/a')
            logger.debug(msg)
            return None, None, None, None

        user_attrs = res['results'][0]
        dn = user_attrs.get('dn')
        utf8_dn = to_utf8(dn)

        if pwd is not None:
            # Step 2: Re-bind using the password passed in and the DN we
            #         looked up in Step 1. This will catch bad passwords.
            if self._binduid_usage != 1:
                user_dn = dn
                user_pwd = pwd
            else:
                user_dn = self._binduid
                user_pwd = self._bindpwd

                # Even though I am going to use the Manager DN and password
                # for the "final" lookup I *must* ensure that the password
                # is not a bad password. Since LDAP passwords
                # are one-way encoded I must ask the LDAP server to verify
                # the password, I cannot do it myself.
                try:
                    self._delegate.connect(bind_dn=utf8_dn, bind_pwd=pwd)
                except Exception:
                    # Something went wrong, most likely bad credentials
                    msg = '_lookupuserbyattr: Binding as "%s" fails' % dn
                    logger.debug(msg)
                    return None, None, None, None

            logger.debug('_lookupuserbyattr: Re-binding as "%s"' % user_dn)

            auth_res = self._delegate.search(base=utf8_dn,
                                             scope=self._delegate.BASE,
                                             filter='(objectClass=*)',
                                             attrs=known_attrs,
                                             bind_dn=user_dn,
                                             bind_pwd=user_pwd)

            if auth_res['size'] == 0 or auth_res['exception']:
                msg = '_lookupuserbyattr: "%s" lookup fails bound as "%s"' % (
                    dn, user_dn)
                logger.debug(msg)
                return None, None, None, None

            user_attrs = auth_res['results'][0]

        else:
            user_pwd = pwd

        logger.debug('_lookupuserbyattr: user_attrs %s' % str(user_attrs))

        groups = list(self.getGroups(dn=dn, attr='cn', pwd=user_pwd))
        roles = self._mapRoles(groups)
        roles.extend(self._roles)

        return roles, dn, user_attrs, groups

    @security.protected(manage_users)
    def manage_reinit(self, REQUEST=None):
        """ re-initialize and clear out users and log """
        self._clearCaches()
        self._hash = '%s-%s' % (str(self.getPhysicalPath()),
                                str(random.random()))
        logger.info('manage_reinit: Cleared caches')

        if REQUEST:
            msg = 'User caches cleared'
            return self.manage_cache(manage_tabs_message=msg)

    def _setProperty(self, prop_name, prop_value):
        """ Set a property on the LDAP User Folder object """
        if not hasattr(self, prop_name):
            msg = 'No property "%s" on the LDAP User Folder' % prop_name
            raise AttributeError(msg)

        setattr(self, prop_name, prop_value)

    @security.protected(change_ldapuserfolder)
    def manage_changeProperty(self, prop_name, prop_value,
                              client_form='manage_main', REQUEST=None):
        """ The public front end for changing single properties """
        try:
            self._setProperty(prop_name, prop_value)
            self._clearCaches()
            msg = 'Attribute "%s" changed.' % prop_name
        except AttributeError as e:
            msg = e.args[0]

        if REQUEST is not None:
            form = getattr(self, client_form)
            return form(manage_tabs_message=msg)

    @security.protected(change_ldapuserfolder)
    def manage_edit(self, title, login_attr, uid_attr, users_base,
                    users_scope, roles,  groups_base, groups_scope,
                    binduid, bindpwd, binduid_usage=1, rdn_attr='cn',
                    obj_classes='top,person', local_groups=0,
                    implicit_mapping=0, encryption='SHA', read_only=0,
                    extra_user_filter='', REQUEST=None):
        """ Edit the LDAPUserFolder Object """
        if not binduid:
            binduid_usage = 0

        # The ZMI password field uses a hashed password string to make
        # sure no one can read the original password in the page source.
        # If the password here matches the expected hashed version, no
        # cahnge has occurred.
        if bindpwd == self.getEncryptedBindPassword():
            bindpwd = self._bindpwd

        self.title = title
        self.users_base = users_base
        self.users_scope = users_scope
        self.groups_base = groups_base or users_base
        self.groups_scope = groups_scope
        self.read_only = not not read_only

        self._binduid = binduid
        if bindpwd != self.getEncryptedBindPassword():
            self._bindpwd = bindpwd

        self._delegate.edit(login_attr=login_attr, users_base=users_base,
                            rdn_attr=rdn_attr, objectclasses=obj_classes,
                            bind_dn=self._binduid, bind_pwd=self._bindpwd,
                            binduid_usage=binduid_usage, read_only=read_only)

        if isinstance(roles, basestring):
            roles = [x.strip() for x in roles.split(',')]
        self._roles = roles

        self._binduid_usage = int(binduid_usage)
        self._local_groups = not not local_groups
        self._implicit_mapping = implicit_mapping

        if encryption == 'crypt' and crypt is None:
            encryption = 'SHA'

        self._pwd_encryption = encryption

        if isinstance(obj_classes, basestring):
            obj_classes = [x.strip() for x in obj_classes.split(',')]
        self._user_objclasses = obj_classes

        schema = self.getSchemaConfig()

        if rdn_attr not in schema:
            self.manage_addLDAPSchemaItem(ldap_name=rdn_attr,
                                          friendly_name=rdn_attr)
        self._rdnattr = rdn_attr

        if login_attr != 'dn' and login_attr not in schema:
            self.manage_addLDAPSchemaItem(ldap_name=login_attr,
                                          friendly_name=login_attr)
        self._login_attr = login_attr

        if uid_attr != 'dn' and uid_attr not in schema:
            self.manage_addLDAPSchemaItem(ldap_name=uid_attr,
                                          friendly_name=uid_attr)
        self._uid_attr = uid_attr

        self._extra_user_filter = extra_user_filter.strip()

        self._clearCaches()
        msg = 'Properties changed'

        connection = self._delegate.connect()

        if connection is None:
            msg = 'Cannot+connect+to+LDAP+server'

        if REQUEST:
            return self.manage_main(manage_tabs_message=msg)

    @security.protected(manage_users)
    def manage_addServer(self, host, port='389', use_ssl=0, conn_timeout=5,
                         op_timeout=-1, REQUEST=None):
        """ Add a new server to the list of servers in use """
        self._delegate.addServer(host, port, use_ssl, conn_timeout, op_timeout)
        msg = 'Server at %s:%s added' % (host, port)

        if REQUEST:
            return self.manage_servers(manage_tabs_message=msg)

    @security.protected(manage_users)
    def getServers(self):
        """ Proxy method used for the ZMI """
        return tuple(self._delegate.getServers())

    @security.protected(manage_users)
    def manage_deleteServers(self, position_list=[], REQUEST=None):
        """ Delete servers from the list of servers in use """
        if len(position_list) == 0:
            msg = 'No servers selected'
        else:
            self._delegate.deleteServers(position_list)
            msg = 'Servers deleted'

        if REQUEST:
            return self.manage_servers(manage_tabs_message=msg)

    @security.protected(manage_users)
    def getMappedUserAttrs(self):
        """ Return the mapped user attributes """
        schema = self.getSchemaDict()
        pn = 'public_name'
        ln = 'ldap_name'

        return tuple([(x[ln], x[pn]) for x in schema if x.get(pn, '')])

    @security.protected(manage_users)
    def getMultivaluedUserAttrs(self):
        """ Return sequence of user attributes that are multi-valued"""
        schema = self.getSchemaDict()
        mv = [x['ldap_name'] for x in schema if x.get('multivalued', '')]

        return tuple(mv)

    @security.protected(manage_users)
    def getBinaryUserAttrs(self):
        """ Return sequence of binary user attributes"""
        schema = self.getSchemaDict()
        bins = [x['ldap_name'] for x in schema if x.get('binary', '')]

        return tuple(bins)

    @security.protected(manage_users)
    def getUsers(self, authenticated=1):
        """Return a list of *cached* user objects"""
        if authenticated:
            return self._cache('authenticated').getCache()
        else:
            return self._cache('anonymous').getCache()

    @security.protected(manage_users)
    def getAttributesOfAllObjects(self, base_dn, scope, filter_str, attrnames):
        """ Return a dictionary keyed on attribute name where each value
        in the dict is a sequence of attribute values specified by 'attrnames'
        for all objects in the given base dn and scope filtered via filter_str.
        The attributes searched are assumed to be single-valued.  If an
        attribute is multivalued, only the first value of the attribute
        will be included in the returned structure.
        """
        result_dict = {}
        [result_dict.__setitem__(x, []) for x in attrnames]

        res = self._delegate.search(base=base_dn, scope=scope,
                                    attrs=attrnames, filter=filter_str)

        if res['size'] == 0 or res['exception']:
            msg = ('getAttributesOfAllObjects: Cannot find any users (%s)'
                   % res['exception'])
            logger.error(msg)

            return result_dict

        result_dicts = res['results']

        for attrname in attrnames:
            result_dict[attrname] = s = []
            for i in range(res['size']):

                if attrname == 'dn':
                    s.append(result_dicts[i].get(attrname))

                else:
                    result = result_dicts[i].get(attrname, [])
                    if len(result) == 0:
                        result = ''
                    elif len(result) > 0:
                        result = result[0]
                    s.append(result)

        return result_dict

    @security.protected(manage_users)
    def getUserIds(self):
        """ Return a tuple containing all user IDs """
        expires = self._misc_cache().get('useridlistexpires')
        if expires and expires > time.time():
            return self._misc_cache().get('useridlist')

        user_filter = self._getUserFilterString()

        useridlist = sorted(self.getAttributesOfAllObjects(
            self.users_base, self._delegate.getScopes()[self.users_scope],
            user_filter, (self._uid_attr,)).get(self._uid_attr))

        self._misc_cache().set('useridlist', useridlist[:])
        # Expire after 600 secs
        self._misc_cache().set('useridlistexpires', time.time() + 600)

        return tuple(useridlist)

    @security.protected(manage_users)
    def getUserNames(self):
        """ Return a tuple containing all logins """
        loginlist = []
        expires = self._misc_cache().get('loginlistexpires')
        if expires and expires > time.time():
            return self._misc_cache().get('loginlist')

        user_filter = self._getUserFilterString()

        loginlistinfo = self.getAttributesOfAllObjects(
            self.users_base, self._delegate.getScopes()[self.users_scope],
            user_filter, (self._login_attr,))

        if len(loginlistinfo) == 0 or \
           loginlistinfo.get(self._login_attr, None) == []:
            # Special case: Either there really is no user, or the server
            # got angry about requesting every single record and threw back
            # an exception as a result. In order to show the simple text
            # input widget instead of the multi-select box the ZMI expects
            # to receive a OverflowError exception.
            raise OverflowError

        loginlist = sorted(loginlistinfo[self._login_attr])

        self._misc_cache().set('loginlist', loginlist[:])
        # Expire after 600 secs
        self._misc_cache().set('loginlistexpires', time.time() + 600)

        return tuple(loginlist)

    @security.protected(manage_users)
    def getUserIdsAndNames(self):
        """ Return a tuple of (user ID, login) tuples """
        expires = self._misc_cache().get('useridnamelistexpires')
        if expires and expires > time.time():
            return self._misc_cache().get('useridnamelist')

        user_filter = self._getUserFilterString()

        d = self.getAttributesOfAllObjects(
            self.users_base, self._delegate.getScopes()[self.users_scope],
            user_filter, (self._uid_attr, self._login_attr))

        login_id_list = sorted(zip(d.get(self._uid_attr),
                                   d.get(self._login_attr)))

        self._misc_cache().set('useridnamelist', login_id_list)
        # Expire after 600 secs
        self._misc_cache().set('useridnamelistexpires', time.time() + 600)

        return tuple(login_id_list)

    def _getUserFilterString(self, filters=[]):
        """ Return filter string suitable for querying on user objects

        A filter is constructed from the following elements:

        o the user object classes from the ZMI configuration

        o if a sequence of filters is passed in, it is added

        o if no sequence of filters is passed in then a wildcard filter
          for all records with the attribute from the ZMI UID attribute
          configuration is added

        o if the Additional user search filter has been configured in the
          ZMI it will also be ANDed into the final search filter.
        """
        user_obclasses = [x for x in self._user_objclasses if x]
        user_filter_list = [self._delegate.filter_format('(%s=%s)',
                                                         ('objectClass', o))
                            for o in user_obclasses]
        if filters:
            user_filter_list.extend(filters)
        else:
            user_filter_list.append("(%s=*)" % self._uid_attr)
        extra_filter = self.getProperty('_extra_user_filter')
        if extra_filter:
            user_filter_list.append(extra_filter)
        user_filter = '(&%s)' % ''.join(user_filter_list)

        return user_filter

    def getUserByAttr(self, name, value, pwd=None, cache=0):
        """ Get a user based on a name/value pair representing an
            LDAP attribute provided to the user.  If cache is True,
            try to cache the result using 'value' as the key
        """
        if not value:
            return None

        cache_type = pwd and 'authenticated' or 'anonymous'
        negative_cache_key = '%s:%s:%s' % (name, value,
                                           sha1(pwd or '').hexdigest())
        if cache:
            if self._cache('negative').get(negative_cache_key) is not None:
                return None

            cached_user = self._cache(cache_type).get(value, pwd)

            if cached_user:
                msg = 'getUserByAttr: "%s" cached in %s cache' % (
                    value, cache_type)
                logger.debug(msg)
                return cached_user

        user_roles, user_dn, user_attrs, ldap_groups = self._lookupuserbyattr(
            name=name, value=value, pwd=pwd)

        if user_dn is None:
            logger.debug('getUserByAttr: "%s=%s" not found' % (name, value))
            self._cache('negative').set(negative_cache_key, NonexistingUser())
            return None

        if user_attrs is None:
            msg = 'getUserByAttr: "%s=%s" has no properties, bailing' % (
                name, value)
            logger.debug(msg)
            self._cache('negative').set(negative_cache_key, NonexistingUser())
            return None

        if user_roles is None or user_roles == self._roles:
            msg = 'getUserByAttr: "%s=%s" only has roles %s' % (
                name, value, str(user_roles))
            logger.debug(msg)

        login_name = user_attrs.get(self._login_attr, '')
        uid = user_attrs.get(self._uid_attr, '')

        if self._login_attr != 'dn' and len(login_name) > 0:
            if name == self._login_attr:
                logins = [x for x in login_name
                          if value.strip().lower() == x.lower()]
                login_name = logins[0]
            else:
                login_name = login_name[0]
        elif len(login_name) == 0:
            msg = 'getUserByAttr: "%s" has no "%s" (Login) value!' % (
                user_dn, self._login_attr)
            logger.debug(msg)
            self._cache('negative').set(negative_cache_key, NonexistingUser())
            return None

        if self._uid_attr != 'dn' and len(uid) > 0:
            uid = uid[0]
        elif len(uid) == 0:
            msg = 'getUserByAttr: "%s" has no "%s" (UID Attribute) value!' % (
                user_dn, self._uid_attr)
            logger.debug(msg)
            self._cache('negative').set(negative_cache_key, NonexistingUser())
            return None

        user_obj = LDAPUser(uid, login_name, pwd or 'undef', user_roles or [],
                            [], user_dn, user_attrs, self.getMappedUserAttrs(),
                            self.getMultivaluedUserAttrs(),
                            self.getBinaryUserAttrs(),
                            ldap_groups=ldap_groups)

        if cache:
            self._cache(cache_type).set(value, user_obj)

        return user_obj

    @security.protected(manage_users)
    def getUser(self, name, pwd=None):
        """Return a user object specified by its username or None """
        # we want to cache based on login attr, because it's the
        # most-frequently-used codepath
        user = self.getUserByAttr(self._login_attr, name, pwd, cache=1)

        return user

    @security.protected(manage_users)
    def getUserById(self, id, default=_marker):
        """ Return a user object specified by its user id or None """
        user = self.getUserByAttr(self._uid_attr, id, cache=1)
        if user is None and default is not _marker:
            return default

        return user

    @security.protected(manage_users)
    def getUserByDN(self, user_dn):
        """ Make a user object from a DN """
        uid_attr = self._uid_attr

        res = self._delegate.search(base=user_dn, scope=self._delegate.BASE,
                                    attrs=[uid_attr])

        if res['exception'] or res['size'] == 0:
            return None

        if uid_attr != 'dn':
            user_id = res['results'][0].get(uid_attr)[0]
        else:
            user_id = to_utf8(res['results'][0].get(uid_attr))

        user = self.getUserByAttr(uid_attr, user_id, cache=1)

        return user

    def authenticate(self, name, password, request):
        superuser = self._emergency_user

        if not name:
            return None

        if superuser and \
           name == superuser.getUserName() and \
           superuser.authenticate(password, request):
            user = superuser
        else:
            user = self.getUser(name, password)

        if user is not None:
            domains = user.getDomains()
            if domains:
                return (domainSpecMatch(domains, request) and user) or None

        return user

    #################################################################
    #
    # Stuff formerly in LDAPShared.py
    #
    #################################################################

    @security.protected(manage_users)
    def getUserDetails(self, encoded_dn, format=None, attrs=()):
        """ Return all attributes for a given DN """
        dn = to_utf8(urllib.unquote(encoded_dn))

        if not attrs:
            attrs = list(self.getSchemaConfig().keys())

        res = self._delegate.search(base=dn, scope=self._delegate.BASE,
                                    attrs=attrs)

        if res['exception']:
            if format is None:
                result = ((res['exception'], res),)
            elif format == 'dictionary':
                result = {'cn': '###Error: %s' % res['exception']}
        elif res['size'] > 0:
            value_dict = res['results'][0]

            if format is None:
                result = sorted(value_dict.items())
            elif format == 'dictionary':
                result = value_dict
        else:
            if format is None:
                result = ()
            elif format == 'dictionary':
                result = {}

        return result

    @security.protected(manage_users)
    def getGroupDetails(self, encoded_cn):
        """ Return all group details """
        result = ()
        cn = urllib.unquote(encoded_cn)

        if not self._local_groups:
            fltr = self._delegate.filter_format('(cn=%s)', (cn,))
            res = self._delegate.search(base=self.groups_base,
                                        scope=self.groups_scope,
                                        filter=fltr,
                                        attrs=list(VALID_GROUP_ATTRIBUTES))

            if res['exception']:
                exc = res['exception']
                logger.info('getGroupDetails: No group "%s" (%s)' % (cn, exc))
                result = (('Exception', exc),)

            elif res['size'] > 0:
                result = sorted(res['results'][0].items())

            else:
                logger.debug('getGroupDetails: No group "%s"' % cn)

        else:
            g_dn = ''
            all_groups = self.getGroups()
            for group_cn, group_dn in all_groups:
                if group_cn == cn:
                    g_dn = group_dn
                    break

            if g_dn:
                users = []

                for user_dn, role_dns in self._groups_store.items():
                    if g_dn in role_dns:
                        users.append(user_dn)

                result = [('', users)]

        return result

    @security.protected(manage_users)
    def getGroupedUsers(self, groups=None):
        """ Return all those users that are in a group """
        all_dns = {}
        users = []

        if groups is None:
            groups = self.getGroups()

        for group_id, group_dn in groups:
            group_details = self.getGroupDetails(group_id)
            for key, vals in group_details:
                if key in GROUP_MEMBER_ATTRIBUTES or key == '':
                    # If the key is an empty string then the groups are
                    # stored inside the user folder itself.
                    for dn in vals:
                        all_dns[dn] = 1

        for dn in all_dns.keys():
            try:
                user = self.getUserByDN(to_utf8(dn))
            except Exception:
                user = None

            if user is not None:
                users.append(user.__of__(self))

        return tuple(users)

    @security.protected(manage_users)
    def getLocalUsers(self):
        """ Return all those users who are in locally stored groups """
        local_users = []

        for user_dn, user_roles in self._groups_store.items():
            local_users.append((user_dn, user_roles))

        return tuple(local_users)

    @security.protected(manage_users)
    def searchUsers(self, attrs=(), exact_match=False, **kw):
        """ Look up matching user records based on one or mmore attributes

        This method takes any passed-in search parameters and values as
        keyword arguments and will sort out invalid keys automatically. It
        accepts all three forms an attribute can be known as, its real
        ldap name, the name an attribute is mapped to explicitly, and the
        friendly name it is known by.
        """
        users = []
        users_base = self.users_base
        search_scope = self.users_scope
        filt_list = []

        if not attrs:
            attrs = list(self.getSchemaConfig().keys())

        schema_translator = {}
        for ldap_key, info in self.getSchemaConfig().items():
            public_name = info.get('public_name', None)
            friendly_name = info.get('friendly_name', None)

            if friendly_name:
                schema_translator[friendly_name] = ldap_key

            if public_name:
                schema_translator[public_name] = ldap_key

            schema_translator[ldap_key] = ldap_key

        for (search_param, search_term) in kw.items():
            if search_param == 'dn':
                users_base = search_term
                search_scope = self._delegate.BASE

            elif search_param == 'objectGUID':
                # we can't escape the objectGUID query piece using
                # filter_format because it replaces backslashes, which we
                # need as a result of guid2string
                users_base = self.users_base
                guid = guid2string(search_term)

                if exact_match:
                    filt_list.append('(objectGUID=%s)' % guid)
                else:
                    filt_list.append('(objectGUID=*%s*)' % guid)

            else:
                # If the keyword arguments contain unknown items we will
                # simply ignore them and continue looking.
                ldap_param = schema_translator.get(search_param, None)
                if ldap_param is None:
                    continue

                parms = (ldap_param, search_term)
                if search_term and exact_match:
                    add_f = self._delegate.filter_format('(%s=%s)', parms)
                elif search_term:
                    add_f = self._delegate.filter_format('(%s=*%s*)', parms)
                else:
                    add_f = '(%s=*)' % ldap_param
                filt_list.append(add_f)

        if len(filt_list) == 0 and search_param != 'dn':
            # We have no useful filter criteria, bail now before bringing the
            # site down with a search that is overly broad.
            res = {'exception': 'No useful filter criteria given'}
            res['size'] = 0
            search_str = ''

        else:
            search_str = self._getUserFilterString(filters=filt_list)
            res = self._delegate.search(base=users_base, scope=search_scope,
                                        filter=search_str, attrs=attrs)

        if res['exception']:
            logger.debug('findUser Exception (%s)' % res['exception'])
            msg = 'findUser search filter "%s"' % search_str
            logger.debug(msg)
            users = [{'dn': res['exception'], 'cn': 'n/a', 'sn': 'Error'}]

        elif res['size'] > 0:
            res_dicts = res['results']
            for i in range(res['size']):
                dn = res_dicts[i].get('dn')
                rec_dict = {}
                rec_dict['sn'] = rec_dict['cn'] = ''

                for key, val in res_dicts[i].items():
                    rec_dict[key] = val[0]

                rec_dict['dn'] = dn

                users.append(rec_dict)

        return users

    @security.protected(manage_users)
    def searchGroups(self, attrs=(), exact_match=False, **kw):
        """ Look up matching group records based on one or mmore attributes

        This method takes any passed-in search parameters and values as
        keyword arguments and will sort out invalid keys automatically. For
        now it only accepts valid ldap keys, with no translation, as there
        is currently no schema support for groups. The list of accepted
        group attributes is static for now.
        """
        groups = []
        groups_base = self.groups_base
        filt_list = []
        search_str = ''

        for (search_param, search_term) in kw.items():
            if search_param not in VALID_GROUP_ATTRIBUTES:
                continue
            if search_param == 'dn':
                groups_base = search_term

            elif search_param == 'objectGUID':
                # we can't escape the objectGUID query piece using
                # filter_format because it replaces backslashes, which we
                # need as a result of guid2string
                groups_base = self.groups_base
                guid = guid2string(search_term)

                if exact_match:
                    filt_list.append('(objectGUID=%s)' % guid)
                else:
                    filt_list.append('(objectGUID=*%s*)' % guid)

            else:
                # If the keyword arguments contain unknown items we will
                # simply ignore them and continue looking.
                parms = (search_param, search_term)
                if search_term and exact_match:
                    add_f = self._delegate.filter_format('(%s=%s)', parms)
                elif search_term:
                    add_f = self._delegate.filter_format('(%s=*%s*)', parms)
                else:
                    add_f = '(%s=*)' % search_param
                filt_list.append(add_f)

        if len(filt_list) == 0:
            # We have no useful filter criteria, bail now before bringing the
            # site down with a search that is overly broad.
            res = {'exception': 'No useful filter criteria given'}
            res['size'] = 0

        else:
            ff = self._delegate.filter_format
            oc_filt = '(|%s)' % ''.join([ff('(%s=%s)', ('objectClass', o))
                                         for o in GROUP_MEMBER_MAP.keys()])
            filt_list.append(oc_filt)
            search_str = '(&%s)' % ''.join(filt_list)
            res = self._delegate.search(base=groups_base,
                                        scope=self.groups_scope,
                                        filter=search_str, attrs=attrs)

        if res['exception']:
            logger.warn('searchGroups Exception (%s)' % res['exception'])
            msg = 'searchGroups searched "%s"' % search_str
            logger.warn(msg)
            groups = [{'dn': res['exception'], 'cn': 'n/a'}]

        elif res['size'] > 0:
            res_dicts = res['results']
            for i in range(res['size']):
                dn = res_dicts[i].get('dn')
                rec_dict = {}

                for key, val in res_dicts[i].items():
                    if len(val) > 0:
                        rec_dict[key] = val[0]

                rec_dict['dn'] = dn

                groups.append(rec_dict)

        return groups

    @security.protected(manage_users)
    def findUser(self, search_param, search_term, attrs=(), exact_match=False):
        """ Look up matching user records based on a single attribute """
        kw = {search_param: search_term}
        if not attrs:
            attrs = list(self.getSchemaConfig().keys())

        return self.searchUsers(attrs=attrs, exact_match=exact_match, **kw)

    @security.protected(manage_users)
    def getGroups(self, dn='*', attr=None, pwd=''):
        """ returns a list of possible groups from the ldap tree
            (Used e.g. in showgroups.dtml) or, if a DN is passed
            in, all groups for that particular DN.
        """
        group_list = []
        no_show = ('Anonymous', 'Authenticated', 'Shared')

        if self._local_groups:
            if dn != '*':
                all_groups_list = self._groups_store.get(dn) or []
            else:
                all_groups_dict = {}
                zope_roles = list(self.valid_roles())
                zope_roles.extend(list(self._additional_groups))

                for role_name in zope_roles:
                    if role_name not in no_show:
                        all_groups_dict[role_name] = 1

                all_groups_list = all_groups_dict.keys()

            for group in all_groups_list:
                if attr is None:
                    group_list.append((group, group))
                else:
                    group_list.append(group)

            group_list.sort()

        else:
            gscope = self._delegate.getScopes()[self.groups_scope]

            if dn != '*':
                f_template = '(&(objectClass=%s)(%s=%s))'
                group_filter = '(|'

                for g_name, m_name in GROUP_MEMBER_MAP.items():
                    fltr = self._delegate.filter_format(f_template,
                                                        (g_name, m_name, dn))
                    group_filter += fltr

                group_filter += ')'

            else:
                group_filter = '(|'

                for g_name in GROUP_MEMBER_MAP.keys():
                    fltr = self._delegate.filter_format('(objectClass=%s)',
                                                        (g_name,))
                    group_filter += fltr

                group_filter += ')'

            res = self._delegate.search(base=self.groups_base, scope=gscope,
                                        filter=group_filter, attrs=['cn'],
                                        bind_dn='', bind_pwd='')

            exc = res['exception']
            if exc:
                if attr is None:
                    group_list = (('', exc),)
                else:
                    group_list = (exc,)
            elif res['size'] > 0:
                res_dicts = res['results']
                for i in range(res['size']):
                    dn = res_dicts[i].get('dn')
                    try:
                        cn = res_dicts[i]['cn'][0]
                    except KeyError:    # NDS oddity
                        cn = self._delegate.explode_dn(dn, 1)[0]

                    if attr is None:
                        group_list.append((cn, dn))
                    elif attr == 'cn':
                        group_list.append(cn)
                    elif attr == 'dn':
                        group_list.append(dn)

        return group_list

    @security.protected(manage_users)
    def getGroupType(self, group_dn):
        """ get the type of group """
        if self._local_groups:
            if group_dn in self._additional_groups:
                group_type = 'Custom Role'
            else:
                group_type = 'Zope Built-in Role'

        else:
            group_type = 'n/a'
            res = self._delegate.search(base=to_utf8(group_dn),
                                        scope=self._delegate.BASE,
                                        attrs=['objectClass'])
            if res['exception']:
                msg = 'getGroupType: No group "%s" (%s)' % (
                    group_dn, res['exception'])
                logger.info(msg)

            else:
                l_groups = [x.lower() for x in GROUP_MEMBER_MAP.keys()]
                g_attrs = res['results'][0]
                group_obclasses = g_attrs.get('objectClass', [])
                group_obclasses.extend(g_attrs.get('objectclass', []))
                g_types = [x for x in group_obclasses if x.lower() in l_groups]

                if len(g_types) > 0:
                    group_type = g_types[0]

        return group_type

    @security.protected(manage_users)
    def getGroupMappings(self):
        """ Return the dictionary that maps LDAP groups map to Zope roles """
        mappings = getattr(self, '_groups_mappings', {})

        return list(mappings.items())

    @security.protected(manage_users)
    def manage_addGroupMapping(self, group_name, role_name, REQUEST=None):
        """ Map a LDAP group to a Zope role """
        mappings = getattr(self, '_groups_mappings', {})
        mappings[group_name] = role_name
        self._groups_mappings = mappings
        self._clearCaches()

        if REQUEST:
            msg = 'Added LDAP group to Zope role mapping: %s -> %s' % (
                group_name, role_name)
            return self.manage_grouprecords(manage_tabs_message=msg)

    @security.protected(manage_users)
    def manage_deleteGroupMappings(self, group_names, REQUEST=None):
        """ Delete mappings from LDAP group to Zope role """
        mappings = getattr(self, '_groups_mappings', {})

        for group_name in group_names:
            if group_name in mappings:
                del mappings[group_name]

        self._groups_mappings = mappings
        self._clearCaches()

        if REQUEST:
            msg = 'Deleted LDAP group to Zope role mapping for: %s' % (
                ', '.join(group_names))
            return self.manage_grouprecords(manage_tabs_message=msg)

    def _mapRoles(self, groups):
        """ Perform the mapping of LDAP groups to Zope roles """
        mappings = getattr(self, '_groups_mappings', {})
        roles = []

        if getattr(self, '_implicit_mapping', None):
            roles = groups

        for group in groups:
            mapped_role = mappings.get(group, None)
            if mapped_role is not None and mapped_role not in roles:
                roles.append(mapped_role)

        return roles

    @security.protected(view_management_screens)
    def getProperty(self, prop_name, default=''):
        """ Get at LDAPUserFolder properties """
        return getattr(self, prop_name, default)

    @security.protected(manage_users)
    def getLDAPSchema(self):
        """ Retrieve the LDAP schema this product knows about """
        raw_schema = self.getSchemaDict()
        schema = sorted([(x['ldap_name'], x['friendly_name'])
                         for x in raw_schema])

        return tuple(schema)

    @security.protected(manage_users)
    def getSchemaDict(self):
        """ Retrieve schema as list of dictionaries """
        all_items = sorted(self.getSchemaConfig().values(),
                           key=lambda schema_item: schema_item['ldap_name'])

        return tuple(all_items)

    @security.protected(change_ldapuserfolder)
    def setSchemaConfig(self, schema):
        """ Set the LDAP schema configuration """
        self._ldapschema = schema
        self._clearCaches()

    @security.protected(manage_users)
    def getSchemaConfig(self):
        """ Retrieve the LDAP schema configuration """
        return self._ldapschema

    @security.protected(change_ldapuserfolder)
    def manage_addLDAPSchemaItem(self, ldap_name, friendly_name='',
                                 multivalued=False, public_name='',
                                 binary=False, REQUEST=None):
        """ Add a schema item to my list of known schema items """
        schema = self.getSchemaConfig()
        if ldap_name not in schema:
            schema[ldap_name] = {'ldap_name': ldap_name,
                                 'friendly_name': friendly_name,
                                 'public_name': public_name,
                                 'multivalued': multivalued,
                                 'binary': binary}

            self.setSchemaConfig(schema)
            msg = 'LDAP Schema item "%s" added' % ldap_name
        else:
            msg = 'LDAP Schema item "%s" already exists' % ldap_name

        if REQUEST:
            return self.manage_ldapschema(manage_tabs_message=msg)

    @security.protected(change_ldapuserfolder)
    def manage_deleteLDAPSchemaItems(self, ldap_names=[], REQUEST=None):
        """ Delete schema items from my list of known schema items """
        if len(ldap_names) < 1:
            msg = 'Please select items to delete'

        else:
            schema = self.getSchemaConfig()
            removed = []

            for ldap_name in ldap_names:
                if ldap_name in schema:
                    removed.append(ldap_name)
                    del schema[ldap_name]

            self.setSchemaConfig(schema)

            rem_str = ', '.join(removed)
            msg = 'LDAP Schema items %s removed.' % rem_str

        if REQUEST:
            return self.manage_ldapschema(manage_tabs_message=msg)

    @security.protected(manage_users)
    def manage_addGroup(self, newgroup_name,
                        newgroup_type='groupOfUniqueNames', REQUEST=None):
        """ Add a new group in groups_base """
        if self._local_groups and newgroup_name:
            add_groups = self._additional_groups

            if newgroup_name not in add_groups:
                add_groups.append(newgroup_name)

            self._additional_groups = add_groups
            msg = 'Added new group %s' % (newgroup_name)

        elif newgroup_name:
            attributes = {}
            attributes['cn'] = [newgroup_name]
            attributes['objectClass'] = ['top', newgroup_type]

            if self._binduid:
                initial_member = self._binduid
            else:
                user = getSecurityManager().getUser()
                try:
                    initial_member = user.getUserDN()
                except Exception:
                    initial_member = ''

            attributes[GROUP_MEMBER_MAP.get(newgroup_type)] = initial_member

            err_msg = self._delegate.insert(base=self.groups_base,
                                            rdn='cn=%s' % newgroup_name,
                                            attrs=attributes)
            msg = err_msg or 'Added new group %s' % (newgroup_name)

        else:
            msg = 'No group name specified'

        if REQUEST:
            return self.manage_grouprecords(manage_tabs_message=msg)

    @security.protected(manage_users)
    def manage_addUser(self, REQUEST=None, kwargs={}):
        """ Add a new user record to LDAP """
        base = self.users_base
        attr_dict = {}

        if REQUEST is None:
            source = kwargs
        else:
            source = REQUEST

        rdn_attr = self._rdnattr
        attr_dict[rdn_attr] = source.get(rdn_attr)
        rdn = '%s=%s' % (rdn_attr, source.get(rdn_attr))
        sub_loc = source.get('sub_branch', '')
        if sub_loc:
            base = '%s,%s' % (rdn, base)
        password = source.get('user_pw', '')
        confirm = source.get('confirm_pw', '')

        if password != confirm or password == '':
            msg = 'The password and confirmation do not match!'

        else:
            encrypted_pwd = _createLDAPPassword(password, self._pwd_encryption)
            attr_dict['userPassword'] = encrypted_pwd
            attr_dict['objectClass'] = self._user_objclasses

            for attribute, names in self.getSchemaConfig().items():
                attr_val = source.get(attribute, None)

                if names.get('binary', None) and attr_val:
                    attr_dict['%s;binary' % attribute] = [attr_val]
                elif attr_val:
                    attr_dict[attribute] = attr_val
                elif names.get('public_name', None):
                    attr_val = source.get(names['public_name'], None)

                    if attr_val:
                        attr_dict[attribute] = attr_val

            msg = self._delegate.insert(base=base, rdn=rdn, attrs=attr_dict)

        if msg:
            if REQUEST:
                return self.manage_userrecords(manage_tabs_message=msg)
            else:
                return msg

        if not msg:
            user_dn = '%s,%s' % (rdn, base)
            try:
                user_roles = source.get('user_roles', [])

                if self._local_groups:
                    self._groups_store[user_dn] = user_roles
                else:
                    if len(user_roles) > 0:
                        group_dns = []

                        for role in user_roles:
                            try:
                                exploded = self._delegate.explode_dn(role)
                                elements = len(exploded)
                            except Exception:
                                elements = 1

                            if elements == 1:  # simple string
                                role = 'cn=%s,%s' % (str(role),
                                                     self.groups_base)

                            group_dns.append(role)

                            try:
                                self.manage_editUserRoles(user_dn, group_dns)
                            except Exception:
                                raise

                # Clear the caches for the purpose of clearing any user ID
                # list cached by getUserNames
                self._clearCaches()

                msg = 'New user %s added' % user_dn
            except Exception as e:
                msg = str(e)
                user_dn = ''

        if REQUEST:
            return self.manage_userrecords(manage_tabs_message=msg,
                                           user_dn='%s,%s' % (rdn, base))

    @security.protected(manage_users)
    def manage_deleteGroups(self, dns=[], REQUEST=None):
        """ Delete groups from groups_base """
        msg = ''

        if len(dns) < 1:
            msg = 'You did not specify groups to delete!'

        else:
            if self._local_groups:
                add_groups = self._additional_groups
                for dn in dns:
                    if dn in add_groups:
                        del add_groups[add_groups.index(dn)]

                self._additional_groups = add_groups

            else:
                for dn in dns:
                    msg = self._delegate.delete(dn)

                    if msg:
                        break

            msg = msg or 'Deleted group(s):<br> %s' % '<br>'.join(dns)
            self._clearCaches()

        if REQUEST:
            return self.manage_grouprecords(manage_tabs_message=msg)

    @security.protected(manage_users)
    def manage_deleteUsers(self, dns=[], REQUEST=None):
        """ Delete all users in list dns """
        if len(dns) < 1:
            msg = 'You did not specify users to delete!'

        elif self._delegate.read_only:
            msg = 'Running in read-only mode, deletion is disabled'

        else:
            for dn in dns:
                # Ignoring return values for situations where outside
                # interactions with the LDAP store caused record deletions
                # we do not know about. We still must try to clean up
                # groups that might not have been affected by the
                # directory fiddling someone else might have done.
                self._delegate.delete(dn)

                if self._local_groups:
                    if dn in self._groups_store.keys():
                        del self._groups_store[dn]
                else:
                    user_groups = self.getGroups(dn=dn, attr='dn')

                    for group in user_groups:
                        group_type = self.getGroupType(group)
                        member_type = GROUP_MEMBER_MAP.get(group_type)
                        del_op = self._delegate.DELETE

                        msg = self._delegate.modify(dn=group,
                                                    mod_type=del_op,
                                                    attrs={member_type: [dn]})

            msg = 'Deleted user(s):<br> %s' % '<br>'.join(dns)
            self._clearCaches()

        if REQUEST:
            return self.manage_userrecords(manage_tabs_message=msg)

    @security.protected(manage_users)
    def manage_editUserPassword(self, dn, new_pw, REQUEST=None):
        """ Change a user password """
        err_msg = msg = ''

        if new_pw == '':
            msg = 'The password cannot be empty!'

        else:
            ldap_pw = _createLDAPPassword(new_pw, self._pwd_encryption)
            err_msg = self._delegate.modify(dn=dn,
                                            attrs={'userPassword': [ldap_pw]})
            if not err_msg:
                msg = 'Password changed for "%s"' % dn
                user_obj = self.getUserByDN(to_utf8(dn))
                self._expireUser(user_obj)

        if REQUEST:
            return self.manage_userrecords(manage_tabs_message=err_msg or msg,
                                           user_dn=dn)

    @security.protected(manage_users)
    def manage_editUserRoles(self, user_dn, role_dns=[], REQUEST=None):
        """ Edit the roles (groups) of a user """
        msg = ''
        all_groups = self.getGroups(attr='dn')
        cur_groups = self.getGroups(dn=user_dn, attr='dn')
        group_dns = []
        for group in role_dns:
            if group.find('=') == -1:
                group_dns.append('cn=%s,%s' % (group, self.groups_base))
            else:
                group_dns.append(group)

        if self._local_groups:
            if len(role_dns) == 0 and user_dn in self._groups_store:
                del self._groups_store[user_dn]
            else:
                self._groups_store[user_dn] = role_dns

        else:
            for group in all_groups:
                member_attr = GROUP_MEMBER_MAP.get(self.getGroupType(group))

                if group in cur_groups and group not in group_dns:
                    msg = self._delegate.modify(group, self._delegate.DELETE,
                                                {member_attr: [user_dn]})
                elif group in group_dns and group not in cur_groups:
                    msg = self._delegate.modify(group, self._delegate.ADD,
                                                {member_attr: [user_dn]})

        msg = msg or 'Roles changed for %s' % (user_dn)
        user_obj = self.getUserByDN(to_utf8(user_dn))
        if user_obj is not None:
            self._expireUser(user_obj)

        if REQUEST:
            return self.manage_userrecords(manage_tabs_message=msg,
                                           user_dn=user_dn)

    @security.protected(manage_users)
    def manage_setUserProperty(self, user_dn, prop_name, prop_value):
        """ Set a new attribute on the user record """
        schema = self.getSchemaConfig()
        prop_info = schema.get(prop_name, {})
        is_binary = prop_info.get('binary', None)

        if isinstance(prop_value, basestring):
            if is_binary:
                prop_value = [prop_value]
            elif not prop_info.get('multivalued', ''):
                prop_value = [prop_value.strip()]
            else:
                prop_value = [x.strip() for x in prop_value.split(';')]

        if not is_binary:
            for i in range(len(prop_value)):
                prop_value[i] = to_utf8(prop_value[i])

        cur_rec = self._delegate.search(base=user_dn,
                                        scope=self._delegate.BASE)

        if cur_rec['exception'] or cur_rec['size'] == 0:
            exc = cur_rec['exception']
            msg = 'manage_setUserProperty: No user "%s" (%s)' % (user_dn, exc)
            logger.debug(msg)

            return

        user_rec = cur_rec['results'][0]
        cur_prop = user_rec.get(prop_name, [''])

        if cur_prop != prop_value:
            if prop_value != ['']:
                mod = self._delegate.REPLACE
            else:
                mod = self._delegate.DELETE

            if is_binary:
                attrs = {'%s;binary' % prop_name: prop_value}
            else:
                attrs = {prop_name: prop_value}

            err_msg = self._delegate.modify(dn=user_dn, mod_type=mod,
                                            attrs=attrs)

            if not err_msg:
                user_obj = self.getUserByDN(to_utf8(user_dn))
                self._expireUser(user_obj)

    @security.protected(manage_users)
    def manage_editUser(self, user_dn, REQUEST=None, kwargs={}):
        """ Edit a user record """
        schema = self.getSchemaConfig()
        msg = ''
        new_attrs = {}
        utf8_dn = to_utf8(user_dn)
        cur_user = self.getUserByDN(utf8_dn)

        if REQUEST is None:
            source = kwargs
        else:
            source = REQUEST

        for attr, attr_info in schema.items():
            if attr in source:
                new = source.get(attr, '')
                if isinstance(new, basestring):
                    if attr_info.get('binary', ''):
                        new = [new]
                        attr = '%s;binary' % attr
                    elif not attr_info.get('multivalued', ''):
                        new = [new.strip()]
                    else:
                        new = [x.strip() for x in new.split(';')]

                new_attrs[attr] = new

        if cur_user is None:
            msg = 'No user with DN "%s"' % user_dn

        if new_attrs and not msg:
            msg = self._delegate.modify(user_dn, attrs=new_attrs)
        elif not new_attrs:
            msg = 'No attributes changed'

        if msg:
            if REQUEST:
                return self.manage_userrecords(manage_tabs_message=msg,
                                               user_dn=user_dn)
            else:
                return msg

        rdn = self._rdnattr
        new_cn = source.get(rdn, '')
        new_dn = ''

        # This is not good, but explode_dn mangles non-ASCII
        # characters so I simply cannot use it.
        old_utf8_rdn = to_utf8('%s=%s' % (rdn, cur_user.getProperty(rdn)))
        new_rdn = '%s=%s' % (rdn, new_cn)
        new_utf8_rdn = to_utf8(new_rdn)

        if new_cn and new_utf8_rdn != old_utf8_rdn:
            old_dn = utf8_dn
            old_dn_exploded = self._delegate.explode_dn(old_dn)
            old_dn_exploded[0] = new_rdn
            new_dn = ','.join(old_dn_exploded)
            old_groups = self.getGroups(dn=user_dn, attr='dn')

            if self._local_groups:
                if self._groups_store.get(user_dn):
                    del self._groups_store[user_dn]

                self._groups_store[new_dn] = old_groups

            else:
                for group in old_groups:
                    group_type = self.getGroupType(group)
                    member_type = GROUP_MEMBER_MAP.get(group_type)

                    msg = self._delegate.modify(group, self._delegate.DELETE,
                                                {member_type: [user_dn]})
                    msg = self._delegate.modify(group, self._delegate.ADD,
                                                {member_type: [new_dn]})

        self._expireUser(cur_user.getProperty(rdn))
        msg = msg or 'User %s changed' % (new_dn or user_dn)

        if REQUEST:
            return self.manage_userrecords(manage_tabs_message=msg,
                                           user_dn=new_dn or user_dn)

    @security.protected(manage_users)
    def _expireUser(self, user):
        """ Purge user object from caches """
        user = user or ''

        if not isinstance(user, basestring):
            user = user.getUserName()

        self._cache('anonymous').invalidate(user)
        self._cache('authenticated').invalidate(user)

        # This only removes records from the negative cache which
        # were retrieved without a password, since down here we do not
        # know that password. Only login and uid records are removed.
        for name in (self._login_attr, self._uid_attr):
            negative_cache_key = '%s:%s:%s' % (name, user,
                                               sha1('').hexdigest())
            self._cache('negative').invalidate(negative_cache_key)

    @security.protected(manage_users)
    def isUnique(self, attr, value):
        """ Find out if any objects have the same attribute value.
            This method should be called when a new user record is
            about to be created. It guards uniqueness of names by
            warning for items with the same name.
        """
        search_str = self._delegate.filter_format('(%s=%s)',
                                                  (attr, str(value)))
        res = self._delegate.search(base=self.users_base,
                                    scope=self.users_scope, filter=search_str)

        if res['exception']:
            return res['exception']

        return res['size'] < 1

    def getEncryptions(self):
        """ Return the possible encryptions """
        if not crypt:
            return ('SHA', 'SSHA', 'md5', 'clear')
        else:
            return ('crypt', 'SHA', 'SSHA', 'md5', 'clear')

    def _cache(self, cache_type='anonymous'):
        """ Get the specified user cache """
        cache = getResource('%s-%scache' % (self._hash, cache_type),
                            UserCache, ())
        cache.setTimeout(self.getCacheTimeout(cache_type))
        return cache

    def _misc_cache(self):
        """ Return the miscellaneous cache """
        return getResource('%s-misc_cache' % self._hash, SimpleCache, ())

    @security.protected(manage_users)
    def getCacheTimeout(self, cache_type='anonymous'):
        """ Retrieve the cache timout value (in seconds) """
        return getattr(self, '_%s_timeout' % cache_type, 600)

    @security.protected(manage_users)
    def setCacheTimeout(self, cache_type='anonymous', timeout=600,
                        REQUEST=None):
        """ Set the cache timeout """
        if not timeout and timeout != 0:
            timeout = 600
        else:
            timeout = int(timeout)

        setattr(self, '_%s_timeout' % cache_type, timeout)

        self._cache(cache_type).setTimeout(timeout)

        if REQUEST is not None:
            msg = 'Cache timeout changed'
            return self.manage_cache(manage_tabs_message=msg)

    @security.protected(manage_users)
    def getCurrentServer(self):
        """ Simple UI Helper to show who we are currently connected to. """
        try:
            conn = self._delegate.connect()
        except Exception:
            conn = None

        return getattr(conn, '_uri', '-- not connected --')

    @security.protected(manage_users)
    def getEncryptedBindPassword(self):
        """ Return a hashed bind password for safe use in forms etc.
        """
        return sha1(self.getProperty('_bindpwd')).hexdigest()


def manage_addLDAPUserFolder(self, delegate_type='LDAP delegate',
                             REQUEST=None):
    """ Called by Zope to create and install an LDAPUserFolder """
    this_folder = self.this()

    if hasattr(aq_base(this_folder), 'acl_users') and REQUEST is not None:
        msg = 'This+object+already+contains+a+User+Folder'

    else:
        n = LDAPUserFolder(delegate_type=delegate_type)

        this_folder._setObject('acl_users', n)
        this_folder.__allow_groups__ = self.acl_users

        msg = 'Added+LDAPUserFolder'

    # return to the parent object's manage_main
    if REQUEST is not None:
        url = this_folder.acl_users.absolute_url()
        qs = 'manage_tabs_message=%s' % msg
        REQUEST.RESPONSE.redirect('%s/manage_main?%s' % (url, qs))


InitializeClass(LDAPUserFolder)
