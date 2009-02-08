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
""" LDAP-based CMF member data tool

$Id$
"""

# Python imports
import os
from copy import deepcopy

# General Zope imports
from AccessControl import ClassSecurityInfo
from Acquisition import aq_base
from App.class_init import default__class_init__ as InitializeClass
from App.Common import package_home
from ZPublisher.HTTPRequest import HTTPRequest
from Products.PageTemplates.PageTemplateFile import PageTemplateFile

# CMF imports
from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.MemberDataTool import MemberDataTool
from Products.CMFCore.MemberDataTool import MemberData

_marker = []
_wwwdir = os.path.join(package_home(globals()), 'www')

class LDAPMemberDataTool(MemberDataTool):
    """ This tool wraps user objects, making them act as Member objects. """
    security = ClassSecurityInfo()
    meta_type = 'LDAP Member Data Tool'
    title = 'LDAP Member Data Tool'

    security.declareProtected(ManagePortal, 'manage_showContents')
    manage_showContents = PageTemplateFile('cmfldap_contents.pt', _wwwdir)

    security.declareProtected(ManagePortal, 'manage_memberProperties')
    manage_memberProperties = PageTemplateFile( 'cmfldap_memberProperties.pt'
                                              , _wwwdir
                                              )

    manage_options = ( ( { 'label' : 'Member Properties'
                         , 'action' : 'manage_memberProperties'
                         }
                       ,
                       )
                     + MemberDataTool.manage_options
                     )

    def __init__(self, id='portal_memberdata'):
        self.id = id
        MemberDataTool.__init__(self)
        self._sorted_attributes = ()

    def wrapUser(self, u):
        """
        If possible, returns the Member object that corresponds
        to the given User object.
        """
        id = u.getUserName()
        members = self._members

        if not members.has_key(id):
            base = aq_base(self)
            members[id] = LDAPMemberData(base, id)

        wrapper = members[id].__of__(self).__of__(u)

        # We set the MemberData global options if we found values
        # in the UserData. (for instance the 'email')
        try:
            global mapped_attrs
            mapped_attrs = self.acl_users.getMappedUserAttrs()

            for MappedUserAttr in mapped_attrs:
                try:
                    # get the property value from LDAPUser object, if it is 
                    # empty then the method will raise an exception
                    PropertyValue = u.getProperty(MappedUserAttr[1])
                    # now read the value from the wrapper
                    WrapperPropertyValue = wrapper.getProperty(MappedUserAttr[1])
                    # redefine the wrapper value if it differ
                    if ( PropertyValue is not None and 
                         PropertyValue != '' and 
                         PropertyValue != WrapperPropertyValue ):
                        setattr(wrapper, MappedUserAttr[1], PropertyValue)
                except:
                    # the exception may be thrown if PropertyValue is empty
                    pass
        except:
            pass

        # Return a wrapper with self as containment and
        # the user as context.
        return wrapper


    #################################################################
    # CMFLDAP-specific API used in the ZMI only
    #################################################################

    security.declareProtected(ManagePortal, 'getAvailableMemberProperties')
    def getAvailableMemberProperties(self):
        """ Return a list of attributes that have not been assigned yet """
        uf_schema = deepcopy(self.acl_users.getSchemaConfig())
        
        return [uf_schema[x] for x in uf_schema.keys()
                                   if x not in self._sorted_attributes]

    security.declarePublic('getSortedMemberProperties')
    def getSortedMemberProperties(self):
        """ Return a sorted sequence of dictionaries describing the properties
        available for portal members

        This method is declared Public because it is used for the join_form
        as well.
        """
        sorted_schema = []
        uf_schema = deepcopy(self.acl_users.getSchemaConfig())
        uf_login = self.acl_users.getProperty('_login_attr')
        
        for property_id in self._sorted_attributes:
            property_info = uf_schema.get(property_id, None)

            # Filtering out those properties that are either invalid
            # or provided already by the default machinery.
            if ( property_info is not None and 
                 property_id not in (uf_login, 'mail') ):
                sorted_schema.append(property_info)

        return tuple(sorted_schema)

    security.declareProtected(ManagePortal, 'addMemberProperty')
    def addMemberProperty(self, property_id):
        """ Add a new property. The property_id represents the true LDAP
        attribute name
        """
        if property_id in self._sorted_attributes:
            return
        
        if property_id not in self.acl_users.getSchemaConfig().keys():
            return

        sorted = list(self._sorted_attributes)
        sorted.append(property_id)
        self._sorted_attributes = tuple(sorted)

    security.declareProtected(ManagePortal, 'manage_addMemberProperty')
    def manage_addMemberProperty(self, property_id, REQUEST=None):
        """ ZMI wrapper for addMemberProperty """
        self.addMemberProperty(property_id)

        if REQUEST is not None:
            msg = 'Property %s added.' % property_id
            return self.manage_memberProperties(manage_tabs_message=msg)

    security.declareProtected(ManagePortal, 'removeMemberProperty')
    def removeMemberProperty(self, property_id):
        """ Remove a member property. The property_id represents the true
        LDAP attribute name
        """
        if property_id not in self._sorted_attributes:
            return

        sorted = list(self._sorted_attributes)
        sorted.remove(property_id)
        self._sorted_attributes = tuple(sorted)

    security.declareProtected(ManagePortal, 'manage_removeMemberProperty')
    def manage_removeMemberProperty(self, property_id=None, REQUEST=None):
        """ ZMI wrapper for removeMemberProperty """
        if property_id is None:
            msg = 'Please select a property.'
        else:
            self.removeMemberProperty(property_id)
            msg = 'Property %s removed.' % property_id

        if REQUEST is not None:
            return self.manage_memberProperties(manage_tabs_message=msg)

    security.declareProtected(ManagePortal, 'moveMemberPropertyUp')
    def moveMemberPropertyUp(self, property_id):
        """ Move a member property up in the sort ranking. The property_id
        represents the true LDAP attribute name.
        """
        if property_id not in self._sorted_attributes:
            return

        sorted = list(self._sorted_attributes)
        property_idx = sorted.index(property_id)
        prior_idx = property_idx - 1

        if property_idx > 0:
            current_occupier = sorted[prior_idx]
            sorted[prior_idx] = property_id
            sorted[property_idx] = current_occupier
            self._sorted_attributes = tuple(sorted)

    security.declareProtected(ManagePortal, 'manage_moveMemberPropertyUp')
    def manage_moveMemberPropertyUp(self, property_id=None, REQUEST=None):
        """ ZMI wrapper for moveMemberPropertyUp """
        if property_id is None:
            msg = 'Please select a property.'
        else:
            self.moveMemberPropertyUp(property_id)
            msg = 'Property %s moved.' % property_id

        if REQUEST is not None:
            return self.manage_memberProperties(manage_tabs_message=msg)

    security.declareProtected(ManagePortal, 'moveMemberPropertyDown')
    def moveMemberPropertyDown(self, property_id):
        """ Move a member property down in the sort ranking. The property_id
        represents the true LDAP attribute name.
        """
        if property_id not in self._sorted_attributes:
            return

        sorted = list(self._sorted_attributes)
        property_idx = sorted.index(property_id)
        next_idx = property_idx + 1

        if property_idx < len(sorted) - 1:
            current_occupier = sorted[next_idx]
            sorted[next_idx] = property_id
            sorted[property_idx] = current_occupier
            self._sorted_attributes = tuple(sorted)

    security.declareProtected(ManagePortal, 'manage_moveMemberPropertyDown')
    def manage_moveMemberPropertyDown(self, property_id=None, REQUEST=None):
        """ ZMI wrapper for moveMemberPropertyDown """
        if property_id is None:
            msg = 'Please select a property.'
        else:
            self.moveMemberPropertyDown(property_id)
            msg = 'Property %s moved.' % property_id

        if REQUEST is not None:
            return self.manage_memberProperties(manage_tabs_message=msg)

InitializeClass(LDAPMemberDataTool)


class LDAPMemberData(MemberData):
    """ Member Data wrapper for the LDAP-driven Member Data Tool """

    def setMemberProperties(self, mapping):
        """ Sets the properties of the member.  """
        acl = self.acl_users
        ldap_schemakeys = [x[0] for x in acl.getLDAPSchema()]

        if isinstance(mapping, HTTPRequest):
            mapping = mapping.form

        # back conversion of mapped attributes
        mapped_attrs = acl.getMappedUserAttrs()
        for mapped_attr in mapped_attrs:
            if ( not mapping.has_key(mapped_attr[0]) 
                 and mapping.has_key(mapped_attr[1]) ):
                mapping[mapped_attr[0]] = mapping[mapped_attr[1]]

        # Special-case a couple keys which are pretty much "hard-coded" 
        # in CMF
        if mapping.has_key('email') and not mapping.has_key('mail'):
            mapping['mail'] = mapping['email']
        
        change_vals = filter( None
                            , map( lambda x, lsk=ldap_schemakeys: x in lsk
                                 , mapping.keys()
                                 )
                            )

        try:
            if change_vals:
                user_obj = self.getUser()
                rdn_attr = acl.getProperty('_rdnattr')

                if not mapping.has_key(rdn_attr):
                    mapping[rdn_attr] = user_obj.getUserName()

                acl.manage_editUser( user_obj.getUserDN()
                                   , kwargs=mapping
                                   )
        except:
            pass

        # Before we hand this over to the default MemberData implementation,
        # purge out all keys we have already set via LDAP so that we never
        # shadow a LDAP value on the member data wrapper
        # We want to hand over the "default" stuff like listed status or
        # the skin selection.
        consumed_attributes = [x[0] for x in mapped_attrs]
        consumed_attributes.extend(ldap_schemakeys)
        for key in consumed_attributes:
            if mapping.has_key(key):
                del mapping[key]

        MemberData.setMemberProperties(self, mapping)
        

    def setSecurityProfile(self, password=None, roles=None, domains=None):
        """ Set the user's basic security profile """
        acl = self.acl_users
        u = self.getUser()
        user_dn = u.getUserDN()
        
        if password is not None:
            acl.manage_editUserPassword(user_dn, password)
            u.__ = password

        if roles is not None:
            all_roles = acl.getGroups()
            role_dns = []
            my_new_roles = []
            
            for role_name, role_dn in all_roles:
                if role_name in roles:
                    my_new_roles.append(role_name)
                    role_dns.append(role_dn)
                    
            u.roles = my_new_roles
            acl.manage_editUserRoles(user_dn, role_dns)

        if domains is not None:
            u.domains = domains


    def getPassword(self):
        """ Retrieve the user's password if there is a valid record in the 
        user folder cache, otherwise create a new one and set it on the user 
        object and in LDAP
        """
        user_obj = self.getUser()
        pwd = user_obj._getPassword()

        if pwd == 'undef':      # This user object did not result from a login
            reg_tool = getToolByName(self, 'portal_registration')
            pwd = reg_tool.generatePassword()
            self.setSecurityProfile(password=pwd)
            self.acl_users._expireUser(user_obj)

        return pwd


InitializeClass(LDAPMemberData)
