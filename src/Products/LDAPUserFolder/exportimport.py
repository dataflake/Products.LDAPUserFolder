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
""" LDAPUserFolder GenericSetup support
"""

from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from zope.component import adapts
from ZPublisher.HTTPRequest import default_encoding

from Products.GenericSetup.interfaces import ISetupEnviron
from Products.GenericSetup.utils import XMLAdapterBase
from Products.GenericSetup.utils import exportObjects
from Products.GenericSetup.utils import importObjects

from .interfaces import ILDAPUserFolder


PROPERTIES = ('title', '_login_attr', '_uid_attr', 'users_base',
              'users_scope', '_roles',  'groups_base', 'groups_scope',
              '_binduid', '_bindpwd', '_binduid_usage', '_rdnattr',
              '_user_objclasses', '_local_groups', '_implicit_mapping',
              '_pwd_encryption', 'read_only', '_extra_user_filter',
              '_anonymous_timeout', '_authenticated_timeout')


class LDAPUserFolderXMLAdapter(XMLAdapterBase):
    """ XML im/exporter for LDAPUserFolder instances
    """

    adapts(ILDAPUserFolder, ISetupEnviron)

    _LOGGER_ID = name = 'ldapuserfolder'
    _encoding = default_encoding

    def _exportNode(self):
        """Export the object as a DOM node.
        """
        node = self._getObjectNode('object')
        node.appendChild(self._extractSettings())
        node.appendChild(self._extractAdditionalGroups())
        node.appendChild(self._extractGroupMap())
        node.appendChild(self._extractGroupsStore())
        node.appendChild(self._extractServers())
        node.appendChild(self._extractLDAPSchema())

        self._logger.info('LDAPUserFolder at %s exported.' % (
                                    self.context.absolute_url_path()))
        return node

    def _importNode(self, node):
        """Import the object from the DOM node.
        """
        if self.environ.shouldPurge():
            self._purgeSettings()

        self._initSettings(node)
        self._initAdditionalGroups(node)
        self._initGroupMap(node)
        self._initGroupsStore(node)
        self._initServers(node)
        self._initLDAPSchema(node)

        self._logger.info('LDAPUserFolder at %s imported.' % (
                                    self.context.absolute_url_path()))

    node = property(_exportNode, _importNode)

    def _purgeSettings(self):
        """ Purge all settings before applying them
        """
        self.context._clearCaches()
        self.context.__init__()

    def _extractSettings(self):
        """ Read settings from the LDAPUserFolder instance
        """
        fragment = self._doc.createDocumentFragment()
        for prop_name in PROPERTIES:
            node = self._doc.createElement('property')
            node.setAttribute('name', prop_name)
            prop_value = self.context.getProperty(prop_name)

            if isinstance(prop_value, (list, tuple)):
                for value in prop_value:
                    if isinstance(value, str):
                        value = value.decode(self._encoding)
                    child = self._doc.createElement('element')
                    child.setAttribute('value', value)
                    node.appendChild(child)
            else:
                if isinstance(prop_value, str):
                    prop_value = prop_value.decode(self._encoding)
                elif not isinstance(prop_value, basestring):
                    prop_value = unicode(prop_value)
                child = self._doc.createTextNode(prop_value)
                node.appendChild(child)
            fragment.appendChild(node)

        return fragment

    def _extractAdditionalGroups(self):
        """ Extract additional locally-defined groups
        """
        fragment = self._doc.createDocumentFragment()
        local_groups = self.context._additional_groups

        if local_groups:
            node = self._doc.createElement('additional-groups')
            for group in local_groups:
                child = self._doc.createElement('element')
                child.setAttribute('value', group)
                node.appendChild(child)
            fragment.appendChild(node)

        return fragment

    def _extractGroupMap(self):
        """ Extract LDAP group to Zope role mapping
        """
        fragment = self._doc.createDocumentFragment()
        group_map = self.context.getGroupMappings()

        if group_map:
            node = self._doc.createElement('group-map')
            for ldap_group, zope_role in group_map:
                child = self._doc.createElement('mapped-group')
                child.setAttribute('ldap_group', ldap_group)
                child.setAttribute('zope_role', zope_role)
                node.appendChild(child)
            fragment.appendChild(node)

        return fragment

    def _extractGroupsStore(self):
        """ Extract localy stored group memberships
        """
        fragment = self._doc.createDocumentFragment()
        stored_groups = self.context._groups_store.items()

        if stored_groups:
            node = self._doc.createElement('group-users')
            for user_dn, role_dns in stored_groups:
                child = self._doc.createElement('user')
                child.setAttribute('dn', user_dn)
                for role_dn in role_dns:
                    gchild = self._doc.createElement('element')
                    gchild.setAttribute('value', role_dn)
                    child.appendChild(gchild)
                node.appendChild(child)
            fragment.appendChild(node)

        return fragment

    def _extractServers(self):
        """ Extract LDAP server information
        """
        fragment = self._doc.createDocumentFragment()
        servers = self.context.getServers()

        if servers:
            node = self._doc.createElement('ldap-servers')
            for server_info in self.context.getServers():
                child = self._doc.createElement('ldap-server')
                for key, value in server_info.items():
                    if isinstance(value, (int, bool)):
                        value = unicode(value)
                    child.setAttribute(key, value)
                node.appendChild(child)
            fragment.appendChild(node)

        return fragment

    def _extractLDAPSchema(self):
        """ Extract LDAP schema information
        """
        fragment = self._doc.createDocumentFragment()
        node = self._doc.createElement('ldap-schema')
        schema_config = self.context.getSchemaConfig()
        for schema_info in sorted(schema_config.values(),
                                  key=lambda x: x['ldap_name']):
            child = self._doc.createElement('schema-item')
            for key, value in schema_info.items():
                if isinstance(value, (int, bool)):
                    value = unicode(value)
                child.setAttribute(key, value)
            node.appendChild(child)
        fragment.appendChild(node)

        return fragment

    def _initSettings(self, node):
        """ Apply settings from the export to a LDAPUserFolder instance
        """
        # property
        for child in node.childNodes:
            if child.nodeName != 'property':
                continue

            multivalues = [x for x in child.childNodes if
                           x.nodeType == child.ELEMENT_NODE]

            if multivalues:
                value = self._readSequenceValue(multivalues)
            else:
                value = self._getNodeText(child).encode(self._encoding)
                if value.lower() in ('true', 'yes'):
                    value = True
                elif value.lower() in ('false', 'no'):
                    value = False
                else:
                    try:
                        value = int(value)
                    except ValueError:
                        pass
            self.context._setProperty(child.getAttribute('name'), value)

    def _readSequenceValue(self, nodes):
        """ Extract a sequence value (list or tuple)
        """
        values = []

        for node in nodes:
            if node.nodeName != 'element':
                continue
            values.append(node.getAttribute('value').encode(self._encoding))

        return values

    def _initAdditionalGroups(self, node):
        """ Initialize locally defined group data
        """
        # additional-groups/element/value
        for child in node.childNodes:
            if child.nodeName != 'additional-groups':
                continue

        value_nodes = [x for x in child.childNodes if
                       x.nodeType == child.ELEMENT_NODE]
        self.context._additional_groups = self._readSequenceValue(value_nodes)

    def _initGroupMap(self, node):
        """ Initialize LDAP group to Zope role mapping
        """
        # group-map/mapped-group/ldap_group/zope_role
        group_map = {}

        for child in node.childNodes:
            if child.nodeName != 'group-map':
                continue

            for gchild in child.childNodes:
                if gchild.nodeName != 'mapped-group':
                    continue

                key = gchild.getAttribute('ldap_group').encode(self._encoding)
                value = gchild.getAttribute('zope_role').encode(self._encoding)
                group_map[key] = value

        self.context._groups_mappings = group_map

    def _initGroupsStore(self, node):
        """ Initialize locally stored user/group map
        """
        groups_store = OOBTree()

        # group-users/user/dn/element
        for child in node.childNodes:
            if child.nodeName != 'group-users':
                continue

            for gchild in child.childNodes:
                if gchild.nodeName != 'user':
                    continue

                user_dn = gchild.getAttribute('dn').encode(self._encoding)
                values = [x for x in gchild.childNodes if
                          x.nodeType == child.ELEMENT_NODE]
                role_dns = self._readSequenceValue(values)
                groups_store[user_dn] = role_dns

        self.context._groups_store = groups_store

    def _initServers(self, node):
        """ Initialize LDAP server configurations
        """
        # server / host / port / protocol / conn_timeout / op_timeout
        for child in node.childNodes:
            if child.nodeName != 'ldap-servers':
                continue

            if child.getAttribute('purge').lower() == 'true':
                server_count = len(self.context.getServers())
                self.context.manage_deleteServers(range(0, server_count))

            for gchild in child.childNodes:
                if gchild.nodeName != 'ldap-server':
                    continue

                if gchild.getAttribute('protocol').lower() == u'ldaps':
                    use_ssl = 1
                elif gchild.getAttribute('protocol').lower() == u'ldapi':
                    use_ssl = 2
                else:
                    use_ssl = 0
                port = gchild.getAttribute('port')
                if port:
                    port = int(port)
                self.context.manage_addServer(
                    gchild.getAttribute('host').encode(self._encoding),
                    port=port, use_ssl=use_ssl,
                    conn_timeout=int(gchild.getAttribute('conn_timeout')),
                    op_timeout=int(gchild.getAttribute('op_timeout')))

    def _initLDAPSchema(self, node):
        """ Initialize LDAP schema information
        """
        # ldap-schema/schema-item/friendly_name/ldap_name/
        # multivalued/binary/public_name
        for child in node.childNodes:
            if child.nodeName != 'ldap-schema':
                continue

            if child.getAttribute('purge').lower() == 'true':
                self.context._ldapschema = {}

            for gchild in child.childNodes:
                if gchild.nodeName != 'schema-item':
                    continue

                def get(name):
                    attr = gchild.getAttribute(name)
                    return attr.encode(self._encoding)

                ldap_name = get('ldap_name')
                item = self.context._ldapschema.setdefault(ldap_name, {})

                item['binary'] = get('binary').lower() in ('true', 'yes')
                item['friendly_name'] = get('friendly_name')
                item['multivalued'] = (get('multivalued').lower() in
                                       ('true', 'yes'))
                item['public_name'] = get('public_name')
                item['ldap_name'] = ldap_name


def importLDAPUserFolder(context):
    """ Import LDAPUserFolder settings from an XML file

    When using this step directly, the user folder is expected to reside
    at the same level in the object hierarchy where the setup tool is.
    """
    container = context.getSite()
    uf = getattr(aq_base(container), 'acl_users', None)

    if uf is not None and ILDAPUserFolder.providedBy(uf):
        importObjects(uf, '', context)
    else:
        context.getLogger('ldapuserfolder').debug('Nothing to import.')


def exportLDAPUserFolder(context):
    """ Export LDAPUserFolder settings to an XML file
    """
    container = context.getSite()
    uf = getattr(aq_base(container), 'acl_users', None)

    if uf is not None and ILDAPUserFolder.providedBy(uf):
        exportObjects(uf, '', context)
    else:
        context.getLogger('ldapuserfolder').debug('Nothing to export.')
