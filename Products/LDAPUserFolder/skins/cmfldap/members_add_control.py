##parameters=member_id, password, member_email, send_password=False, **kw
##title=Add a member
##
from Products.CMFCore.utils import getUtilityByInterfaceName
from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.permissions import ManageUsers
from Products.CMFDefault.utils import Message as _

mtool = getToolByName(script, 'portal_membership')
mdtool = getToolByName(script, 'portal_memberdata')
ptool = getUtilityByInterfaceName('Products.CMFCore.interfaces.IPropertiesTool')
rtool = getToolByName(script, 'portal_registration')

properties = { 'username' : member_id
             , 'email' : member_email
             }
for prop_info in mdtool.getSortedMemberProperties():
    key = prop_info['ldap_name']
    value = kw.get(key, None)

    if value is not None:
        properties[key] = value

try:
    rtool.addMember( id=member_id
                   , password=password
                   , properties=properties
                   , REQUEST=context.REQUEST
                   )

except ValueError, errmsg:
    return context.setStatus(False, errmsg)
else:
    if ptool.getProperty('validate_email') or send_password:
        rtool.registeredNotify(member_id, REQUEST=context.REQUEST)
    if mtool.checkPermission(ManageUsers, mtool):
        return context.setStatus(True, _(u'Member registered.'))
    else:
        return context.setStatus(False, _(u'Success!'), is_newmember=True)
