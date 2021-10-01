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
""" Interfaces for LDAPUserFolder package classes
"""

from AccessControl.interfaces import IStandardUserFolder
from AccessControl.interfaces import IUser


class ILDAPUser(IUser):
    """ IUser interface with extended API for the LDAPUserFolder

    This interface is supported by user objects which
    are returned by user validation through the LDAPUserFolder
    product and used for access control.
    """

    def getProperty(name, default=''):
        """ Retrieve the value of a property of name "name". If this
        property does not exist, the default value is returned.

        Properties can be any public attributes that are part of the
        user record in LDAP. Refer to them by their LDAP attribute
        name or the name they have been mapped to in the LDAP User
        Folder

        Permission - Access contents information
        """

    def getUserDN():
        """ Retrieve the user object's Distinguished Name attribute.

        Permission - Access contents information
        """

    def getCreationTime():
        """ Return a DataTime object representing the user object creation time

        Permission - Access contents information
        """


class ILDAPUserFolder(IStandardUserFolder):
    """ This interface lists methods available for scripting
    LDAPUserFolder objects.

    Some others are accessible given the correct permissions but since
    they are used only in the internal workings of the LDAPUserFolder
    they are not listed here.
    """

    def getUsers():
        """ Return all user objects. Since the number of user records in
        an LDAP database is potentially very large this method will
        only return those user objects that are in the internal cache
        of the LDAPUserFolder and not expired.

        Permission - *Manage users*
        """

    def getUserNames():
        """ Return a list of user IDs for all users that can be found
        given the selected user search base and search scope.

        This method will return a simple error message if the
        number of users exceeds the limit of search hits that is
        built into the python-ldap module.

        Permission - *Manage users*
        """

    def getUser(name):
        """ Return the user object for the user "name". if the user
        cannot be found, None will be returned.

        Permission - *Manage users*
        """

    def getUserById(id):
        """ Return the user object with the UserID "id". The User ID
        may be different from the "Name", the Login. To get a user
        by its Login, call getUser.

        Permission - *Manage users*
        """

    def getGroups(dn='*', attr=None, pwd=''):
        """ Return a list of available group records under the group record
        base as defined in the LDAPUserFolder, or a specific group if the
        ``dn`` parameter is provided. The attr argument determines
        what gets returned and it can have the following values:

        o None: A list of tuples is returned where the group CN is the first
          and the group full DN is the second element.

        o cn: A list of CN strings is returned.

        o dn: A list of full DN strings is returned.

        Permission: *Manage users*
        """

    def manage_addGroup(newgroup_name, newgroup_type='groupOfUniqueNames',
                        REQUEST=None):
        """ Add a new group under the group record base of type
        ``newgroup_type``. If REQUEST is not None a MessageDialog screen will
        be returned. The group_name argument forms the new group CN while the
        full DN will be formed by combining this new CN with the group base DN.

        Since a group record cannot be empty, meaning there must be at least
        a single uniqueMember element in it, the DN given as the binduid in
        the LDAPUserFolder configuration is inserted.

        Permission: *Manage users*
        """

    def manage_deleteGroups(dns=[], REQUEST=None):
        """ Delete groups specified by a list of group DN strings which are
        handed in as the *dns* argument.

        Permission: *Manage users*
        """

    def findUser(search_param, search_term, attrs=(), exact_match=False):
        """ Find user records given the *search_param* string (which is the
        name of an LDAP attribute) and the *search_term* value. The
        ``attrs`` argument can be used the desired attributes to return, and
        ``exact_match`` determines whether the search is a wildcard search
        or not.

        This method will return a list of dictionaries where each matching
        record is represented by a dictionary. The dictionary will contain
        a key/value pair for each LDAP attribute, including *dn*, that is
        present for the given user record.

        Permission: *Manage users*
        """

    def searchUsers(attrs=(), exact_match=False, **kw):
        """ Search for user records by one or more attributes.

        This method takes any passed-in search parameters and values as
        keyword arguments and will sort out invalid keys automatically. It
        accepts all three forms an attribute can be known as, its real
        ldap name, the name an attribute is mapped to explicitly, and the
        friendly name it is known by.

        Permission: *Manage users*
        """

    def getUserDetails(encoded_dn, format=None, attrs=()):
        """ Retrieves all details for a user record represented by the DN that
        is handed in as the URL-encoded *encoded_dn* argument. The format
        argument determines the format of the returned data and can have
        two values:

        o None: All user attributes are handed back as a list of tuples
          where the first element of each tuple contains the LDAP attribute
          name and the second element contains the value.

        o dictionary: The user record is handed back as a simple dictionary
          of attributes as key/value pairs.

        The desired attributes can be limited by passing in a sequence of
        attribute names as the attrs argument.

        Permission: *Manage users*
        """

    def isUnique(attr, value):
        """ Determine whether a given LDAP attribute (attr) and its value
        (value) are unique in the LDAP tree branch set as the user record
        base in the LDAPUserFolder. This method should be called before
        inserting a new user record with attr being the attribute chosen as
        the login name in your LDAPUserFolder because that attribute value
        must be unique.

        This method will return a truth value (1) if the given attribute value
        is indeed unique, 0 if it is not and in the case of an exception it
        will return the string describing the exception.

        Permission: *Manage users*
        """

    def manage_addUser(REQUEST, kwargs):
        """ Create a new user record. If REQUEST is not None, it will be
        used to retrieve the values for the user record.

        To use this method from Python you must pass None as the REQUEST
        argument and a dictionary called *kwargs* containing key/value pairs
        for the user record attributes.

        The dictionary of values passed in, be it REQUEST or kwargs, must at
        the very least contain the following keys and values:

        o *cn* or *uid* (depending on what you set the RDN attribute to)

        o *user_pw* (the new user record's password)

        o *confirm_pw* (This must match password)

        o all attributes your user record LDAP schema must contain (consult
          your LDAP server schema)

        Only those attributes and values are used that are specified on the
        LDAP Schema tab of your LDAPUserFolder.

        Permission: *Manage users*
        """

    def manage_editUser(user_dn, REQUEST, kwargs):
        """ Edit an existing user record. If REQUEST is not None, it will
        be used to retrieve the values for the user record.

        To use this method from Python you must pass None as the REQUEST
        argument and a dictionary called *kwargs* containing key/value pairs
        for the user record attributes.

        Only those attributes and values are used that are specified on the
        LDAP Schema tab of your LDAPUserFolder.

        This method will handle modified RDN (Relative Distinguished name)
        attributes correctly and execute a *modrdn* as well if needed,
        including changing the DN in all group records it is part of.

        Permission: *Manage users*
        """

    def manage_editUserPassword(dn, new_pw, REQUEST):
        """ Change a users password. The *dn* argument contains the full DN
        for the user record in question and new_pw contains the new password.

        Permission: *Manage users*
        """

    def manage_editUserRoles(user_dn, role_dns, REQUEST):
        """ Change a user's group memberships. The user is specified by a
        full DN string, handed in as the *user_dn* attribute. All group
        records the user is supposed to be part of are handed in as
        *role_dns*, a list of DN strings for group records.

        Permission: *Manage users*
        """

    def manage_deleteUsers(dns, REQUEST):
        """ Delete the user records given by a list of DN strings. The user
        records will be deleted and their mentioning in any group record
        as well.

        Permission: *Manage users*
        """
