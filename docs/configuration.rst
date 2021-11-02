===============
 Configuration
===============

These are the configuration options sorted by the :term:`ZMI` navigation tab
they appear on.

.. contents::
    :local:
    :depth: 1

Configure: Basic configuration
------------------------------

This view is used to change the basic settings of a LDAPUserFolder. The
following configuration values can be set:

- **Title**: The (optional) title for this adapter

- **Login Name Attribute**: The LDAP record attribute used as the username.
  The list of default choices can be changed by adding attributes on the
  LDAP Schema tab.

- **User ID Attribute**: The LDAP record attribute used as the user ID.
  The list of default choices can be changed by adding attributes on the
  LDAP Schema tab.

  .. note::
     You should only set this attribute to a
     LDAP record attribute that contains a single value and that does not
     get changed, otherwise you will run into problems with the Zope
     object ownership mechanism.

- **RDN Attribute**: The RDN attribute (Relative Distinguished Name) is the
  name of the LDAP attribute used as the first component of the full DN
  (Distinguished Name). In most cases the default value of *cn* is
  correct, you can select *uid* if your schema defines it. Please see
  RFC 2377 for more information.

- **Users Base DN**: The DN for the branch of your LDAP database that
  contains user records.

- **Scope**: Choose the depth for all searches from the user search base dn

- **Group storage**: Choose where to store the group (a.k.a. Role)
  information for users. You can either store roles inside LDAP itself
  or you can store it inside the LDAP User Folder, which is simpler and
  does not require that LDAP deals with user roles at all.

- **Group mapping**: If your group information is stored in LDAP and you
  do not want to set up individual LDAP group to Zope role mappings, then
  you can simply map all LDAP groups to Zope roles. Each group a user
  is member of will show up as a role with the same name on the user
  object.

- **Groups Base DN**: The DN for the branch of your LDAP database that
  contains group records. These group records are of the LDAP class
  "groupOfUniqueNames" and the entry CN attribute constitutes the group
  name. Groups embody Zope roles. A user which is part of a "Manager"
  group will have the "Manager" role after authenticating through the
  LDAPUserFolder. If you have chosen to store groups inside the user
  folder itself this setting will be disregarded.

- **Scope**: Choose the depth for all searches from the group search base
  dn. If you have chosen to store groups inside the user folder itself
  this setting will be disregarded.

- **Manager DN and password**: All LDAP operations require some form of
  authentication with the LDAP server. Under normal operation if no
  separate Manager DN is provided, the LDAPUserFolder will use the current
  user**s DN and password to try and authenticate to the LDAP server. If a
  Manager DN and password are given, those will be used instead.

- **Manager DN usage**: Specify how the Manager DN (if it has been provided)
  will be used.

  - `Never` will never apply this DN. If no Manager DN is specified this
    is the default value. Bind operations use the current user's DN and
    password if the user is known and an anonymous bind if not. Under
    normal operation only initial logins are performed without a known
    current user.

  - `Always` means the Manager DN is used to bind for every single
    operation on the LDAP server.

  - `For login data lookup only` uses the Manager DN upon user login when
    the user itself has not been instantiated yet and thus the user's DN
    is not yet known. Once the user has been instantiated its DN and
    password are used for binding.

  .. note::
     The modes `Never` and `For login data lookup only` only work if the LDAP
     server allows anonymous lookup of the distinguished name by the LDAP
     attribute you set as User ID attribute.

- **Read-only**: Check this box if you want to prevent the LDAPUserFolder
  from writing to the LDAP directory. This will disable record insertion
  or modification.

- **User object classes**: Comma-separated list of object classes for user
  records. Any new user record created through the LDAPUserFolder will
  carry this list of object classes as its objectClass attribute. The object
  classes specified here are also added to the search filter when looking up a
  user record.

- **Additional user search filter**: The additional user search filter allows
  the administrator to specify a free-form LDAP filter expression which will
  be added to the default user search filter. The default user search filter
  and this additional search filter are combined as an AND expression. Records
  must satisfy both filters to be found using the various user searches. Any
  value specified in this field must follow correct LDAP search filter syntax.

  .. warning::
     Only set this value if you really know what you are doing! You can lock
     out your users with a faulty value here.

- **User password encryption**: This dropdown specifies the encryption scheme
  used to encrypt a user record userPassword attribute. This scheme is
  applied to the plaintext password when a user edits the password or when
  a new user is created. Check your LDAP server to see which encryption
  schemes it supports, pretty much every server can at least do "crypt"
  and "SHA".

- **Default User Roles**: All users authenticated from your ldap tree
  will be given the roles you put into this comma-delimited list in addition
  to the roles already defined for the user.


LDAP Servers: Define servers
----------------------------

Use this view to specify the LDAP servers to connect to, view existing
connection data or delete a server definition. You can set up more than one
server to add redundancy. The LDAPUserFolder will use a server until it becomes
unreachable and then try the next defined server.

The following settings apply when adding new server connections:

- **Server host, IP or socket path**: The hostname, IP address or file
  socket path for the LDAP server.

- **Server port**: The port the LDAP server is listening on. By default,
  LDAP servers listen on port 389 and LDAP over SSL uses port 636.
  If LDAP over IPC has been selected the port will be ignored.

- **Protocol**: Select whether to use standard LDAP, LDAP over SSL or
  LDAP over IPC. Please note that LDAP over SSL is *not* StartTLS, which
  uses the same port as unencrypted traffic.

- **Connection Timeout**: How long the LDAPUserFolder will wait when
  establishing a connection to a LDAP server before giving up. The
  connection timeout prevents the LDAP connection from hanging indefinitely
  if the network connection cannot be established and connection
  attempts do not raise an immediate connection error.

  .. note::
     It is possible that during a request several attempts at connecting
     to the LDAP server are made. The maximum amount of time it takes for
     the LDAPUserFolder to return control to Zope will be the sum of the
     connection attempts multiplied by the chosen connection timeout value.

- **Operation Timeout**: If a connection has been established before but
  there is a chance, e.g. due to a misconfigured firewall, that the
  connection is severed without the LDAPUserFolder noticing, the
  operation timeout value can guard against a hanging site by watching
  how long it takes for a LDAP request to return.

  .. note:: 
     Please use this setting
     with caution and make sure you know how long your LDAP server might
     take to respond under high load. With this setting a long response
     time due to normal reasons, such as load on the LDAP server, can be
     misinterpreted as a hanging connection and the LDAPUserFolder can be
     caught in a vicious circle trying to re-connect again and again.


LDAP Schema: Add user attributes
--------------------------------

The structure of user data records delivered by the LDAP server may be
endlessly variable. On this view you can improve the LDAPUserFolder's
knowledge of your LDAP Schema. All schema items you define here will be added
to the Zope user objects created by the LDAPUserFolder.
Adding or removing entries will not change your LDAP server schema or LDAP
records.

The list of attributes you define is also used to populate select boxes in
other management views, such as the select box for the LDAP attribute
to search on in the "Search" tab or the list of available attributes
that can be selected for the user name in the "Configure" tab.

The following values can be defined for an LDAP schema item:


- **LDAP Attribute Name**: Enter the name of an LDAP attribute as defined
  in your LDAP schema

- **Friendly Name**: LDAP attributes oftentimes have very cryptic names.
  Use this field to give the LDAP attribute you entered in "LDAP Attribute
  Name" a descriptive name.

- **Map to Name**: This optional attribute lets you name a LDAP attribute
  to an attribute name of your choosing on the user object. This is
  useful if you have code that expects certain attributes on the user
  object, like the Tracker product which expects "email". In this case
  you would need an LDAP schema item that carries email addresses and 
  map it to "email".

- **Multi-valued**: In the underlying libraries, all user record attributes
  that are returned as part of the LDAP record are sequences of values.
  By default, in order to stay compatible with "normal" user folders, 
  Zope user objects do not have sequences as standard user attributes,
  so when a LDAPUser object is created only the first value in the 
  sequence of values for a given attribute is used to populate the 
  equivalent attribute on the user object. By declaring a schema item
  to be multi-valued the entire value sequence as delivered by the LDAP server
  is stored on the user object.


Caches: Manage the cache
------------------------

This view shows the cache of currently authenticated users and the active cache
settings. Every time an authenticated user makes a request to Zope,
the username and password are verified. Depending on site traffic
and number of users that log in through the LDAPUserFolder this
process can happen several times a second. Since a lookup on the
LDAP Server can be quite slow, the product will cache the user
information for 600 seconds by default. This is the duration of a
typical session.

Users that can be cached are created either through "real" logins
where a physical user provided a login and password (these end up
in the "authenticated" cache) or via internal lookups that are
done without passwords (those are cached in the "anonymous" cache).
The "negative" cache is for failed lookups.

Keeping separate caches for these different kinds of users avoids
intermingling and possible privilege escalation because no
"anonymous" cached user object will ever be used to perform actions
that require real authentication and elevated privileges.

- **Purge all caches**: This will purge all caches inside the
  LDAPUserFolder. This includes the cache of currently authenticated
  users, the log and any cached username lists.

- **Cache Timeout Settings**: This form allows tweaking the cache
  timeout values for the authenticated, anonymous and negative caches.

- **Cached users**: These are the users in the cache of currently
  cached users. Anonymous users or Emergency User accounts will
  not show up in this table.


Users: Manage user records
--------------------------

This form is used to add new user records to the LDAP database or
to find and edit existing records.

In order to edit an existing record you must find it first. Select
the search parameter and enter the search term into the form. You
will be presented with a view listing matching records. In order
to select a specific record click on the DN. This will lead to a
detail view in which all aspects of the user record can be
edited.

For more details on the search results listing see the **List View**
help below. Help on the detailed user view is under **Detail View**
below.

When adding new records please keep the following in mind:

- The fields you can fill in depend on the LDAP user attributes
  you define on the `LDAP Schema` tab.

- Before you add any user make sure that the `LDAP user objectclass`
  setting on the main configuration screen is correct. User records
  you create on this form will receive the object classes whose names
  you designate as LDAP user objectclasses during configuration.

- The list of roles that you see depend on the groups available
  from the LDAP server. Visit the `Groups` view to see them.

- Always keep in mind that your schema might enforce certain
  rules, like attributes that **must** be filled in. The LDAPUserFolder
  cannot discover these rules by itself and you will get an error
  if the data you enter on this form does not conform to your LDAP
  schema rules.

- Some attributes might carry more than one value. If the LDAP
  schema allows multiple values you can enter them as a
  semicolon (;) - separated list in the input field. They will
  show up semicolon-separated when you view the record again.

List view
~~~~~~~~~

After having searched the LDAP database you will see a list
of possible matches, or a message indicating no matches. You
can use the following controls:

- **Delete**: After checking one or more checkboxes next to records
  in the list hitting Delete will delete those records from the
  LDAP database. You will see a confirmation message indicating any
  errors encountered and will end up on the search page of the
  Edit User screen again.

- **Select All and Deselect All**: This button checks or unchecks
  all checkboxes on the record list.

- **Search!**: Search for another record

Detail View
~~~~~~~~~~~

This page shows all user record details. Please keep the following
in mind:

- The fields you can fill in depend on the LDAP user attributes
  you define on the `LDAP Schema` tab.

- The list of roles that you see depend on the groups available
  from the LDAP server. Visit the `Groups` view to see them.

- Always keep in mind that your schema might enforce certain
  rules, like attributes that **must** be filled in. The LDAPUserFolder
  cannot discover these rules by itself and you will get an error
  if the data you enter on this form does not conform to your LDAP
  schema rules.

- Some attributes might carry more than one value. If the LDAP
  schema allows multiple values you can enter them as a comma-separated
  list in the input field.

You can use the following controls:

- **Apply Changes**: Hitting this button after changing the record's
  attributes will modify the user record in LDAP.

- **Change Groups**: You can change a user's LDAP groups by selecting
  the desired groups from the list of available groups.

- **Change Password**: Type in the new password and hit the
  "Change Password" button.

- **Search!**: Search for another record


Groups: Manage group records
----------------------------

This view shows the groups exposed by your LDAP server for
authentication purposes. You can add new groups or delete
existing records. You can also map LDAP groups to existing
Zope roles in order to make use of them in Zope.

The following controls are available:

- **LDAP groups**: This section shows all LDAP group records
  found on the LDAP server. By checking one or more checkboxes
  next to group records and then hitting Delete you can remove
  group records from LDAP.

- **Add LDAP group**: In order to add a new group you only need to
  provide a group name and type. This name shuld be a "friendly"
  name, meaning it must not have any LDAP prefixes like "cn=".
  Once you hit "Add" you will see the new group in the listing
  or an error message above the listing.

- **LDAP group to Zope role mappings**: If an LDAP group has been
  mapped to a Zope role it will show up in this list. Checking
  the checkbox next to an entry and clicking "Delete" will remove
  the corresponding mapping. If you map a LDAP group to a Zope
  role then any user who is a member of that group in LDAP will
  receive the Zope role it is mapped to.

- **Add LDAP group to Zope role mapping**: Map a LDAP group to a Zope role
  here. Select the desired LDAP group name and the Zope role name that
  members of this group are supposed to have and hit "Add".
  This form will only show Zope roles that already exist on the
  Security tab, except for "Authenticated", "Owner" and "Anonymous".
