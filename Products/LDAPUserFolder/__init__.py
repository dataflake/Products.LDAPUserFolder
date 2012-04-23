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
""" LDAPUserFolder package initialization code

$Id$
"""

from AccessControl.Permissions import add_user_folders

from Products.LDAPUserFolder.LDAPUserFolder import LDAPUserFolder
from Products.LDAPUserFolder.LDAPUserFolder import manage_addLDAPUserFolder
from Products.LDAPUserFolder.LDAPUserSatellite import addLDAPUserSatelliteForm
from Products.LDAPUserFolder.LDAPUserSatellite import manage_addLDAPUserSatellite
from Products.LDAPUserFolder.LDAPUserSatellite import LDAPUserSatellite 

def initialize(context):
    context.registerClass( LDAPUserFolder
                         , permission=add_user_folders
                         , constructors=(manage_addLDAPUserFolder,)
                         , icon='www/ldapuserfolder.gif'
                         )

    context.registerClass( LDAPUserSatellite
                         , permission=add_user_folders
                         , constructors=( addLDAPUserSatelliteForm
                                        , manage_addLDAPUserSatellite
                                        )
                         , icon='www/ldapusersatellite.gif'
                         )

    context.registerHelp()

