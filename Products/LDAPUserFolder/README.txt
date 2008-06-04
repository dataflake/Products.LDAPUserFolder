README for the Zope LDAPUserFolder Product

  **NOTE**: Do not install the CMFLDAP extensions into a Plone site. 
  They are meant for pure CMF sites only and will break Plone. You have 
  been warned!

  This product is a replacement for a Zope user folder. It 
  does not store its own user objects but builds them on the 
  fly after authenticating a user against the LDAP database.


  **How to upgrade**

    Upgrading entails not only unpacking the new code, you
    should also delete and recreate all LDAPUserFolder
    instances in your Zope installation to prevent errors. A safe
    upgrade strategy looks like this:

      - log in as an emergency user
      - delete all LDAPUserFolder instances
      - upgrade the filesystem product
      - restart Zope
      - log in as emergency user
      - recreate the LDAPUserFolder instances

    How to create an emergency user is described in the SECURITY.txt
    document in the 'doc' folder at the root of your Zope software
    installation. The mentioned 'zpasswd.py' script resides in the 
    'bin' folder at the root of your Zope installation.


  **Debugging problems**

    All log messages are sent to the standard Zope event log 'event.log'.
    In order to see more verbose logging output you need to increase the 
    log level in your Zope instance's zope.conf. See the 'eventlog'
    directive. Setting the 'level' key to 'debug' will maximize log 
    output and may help pinpoint problems during setup and testing.


  **Custom login page**

    If you want custom login pages instead of the standard authentication
    popup dialogs I recommend installing the CookieCrumbler product 
    alongside the LDAPUserFolder which provides cookie authentication
    functionality for user folders.


  **Why does the LDAPUserFolder not show all my LDAP groups?**

    According to feedback received from people who use Netscape
    directory products the way a new group is instantiated allows
    empty groups to exist in the system. However, according to 
    the canonical definition for group records groups must always
    have a group member attribute.
    The LDAPUserFolder looks up group records by looking for group 
    member entries. If a group record has no members then it will
    be skipped. As said above, this only seems to affect Netscape
    directory servers.
    To work around this (Netscape) phenomenon add one or more 
    members to the group in question using the tools that came with
    the directory server. It should appear in the LDAPUserFolder
    after that.


  **Note about multi-valued attributes**

    If you want your user objects to expose the full sequence of values
    for a multi-valued attribute field you need to explicitly "bless"
    that attribute as Multi-valued on the "LDAP Schema" management tab.
    Multi-valued attributes will show up as a semicolon-separated string
    in the Zope Management interface itself. The user object carries these
    attrinutes as a list.


  **Using LDAP over IPC (ldapi) to talk to the LDAP server**

    The LDAP over IPC protocol allows you to talk to your LDAP server
    through a filesystem socket file. The protocol is faster due to the
    lack of network and TCP/IP overhead and it is considered slightly
    safer because no network sockets are involved and you can secure the
    socket file using filesystem security.
    In order to use ldapi the server needs to support it. My tests were
    on OpenLDAP version 2.1 and higher. 
    The LDAP server and the Zope site with the LDAPUserFolder must have 
    access to the filesystem socket, so either the LDAP server needs to 
    run on the same machine or the partition with the socket must be 
    mounted on the Zope server host.  
    Getting ldapi to work can be difficult due to filesystem permissions.
    Keep in mind that in order to communicate the user account accessing
    the LDAP server must have read and write permissions to the socket
    file.


  **Why use LDAP to store user records?**

    LDAP as a source of Zope user records is an excellent 
    choice in many cases, like...

    o You already have an existing LDAP setup that might store
      company employee data and you do not want to duplicate 
      any data into a Zope user folder

    o You want to make the same user database available to 
      other applications like mail, address book clients,
      operating system authenticators (PAM-LDAP) or other 
      network services that allow authentication against
      LDAP

    o You have several Zope installations that need to share
      user records or a ZEO setup

    o You want to be able to store more than just user name
      and password in your Zope user folder

    o You want to manipulate user data outside of Zope

    ... the list continues.


  **Requirements**

    The requirements and dependencies are described in INSTALL.txt


  **The LDAP Schema**

    Your LDAP server should contain records that can be used as user 
    records. Any object types like person, organizationalPerson, 
    or inetOrgPerson and any derivatives thereof should work. Records
    of type posixAccount should work correctly as well.
    The LDAPUserFolder expects your user records to have at least the 
    following attributes, most of which are required for the 
    abovementioned object classes, anyway:

    * an attribute to hold the user ID (like cn, uid, etc)

    * userPassword (the password field)

    * objectClass

    * whatever attribute you choose as the username attribute

    * typcial person-related attributes like sn (last name), 
      givenName (first name), uid or mail (email address) will make 
      working with the LDAPUserFolder nicer

    Zope users have certain roles associated with them, these roles
    determine what permissions the user have. For the LDAPUserFolder,
    role information can be expressed through membership in group
    records in LDAP.

    Group records can be of any object type that accepts multiple 
    attributes of type "uniqueMember" or "member" and that has a 
    "cn" attribute. One such type is "groupOfUniqueNames". The cn 
    describes the group / role name while the member attributes point 
    back to all those user records that are part of this group. Only
    those group-style records that use full DNs for its members
    are supported, which excludes classes like posixGroup.

    For examples of valid group- and user-records for LDAP please
    see the file SAMPLE_RECORDS.txt in this distribution. It has 
    samples for a user- and a group record in LDIF format.

    It is outside of the scope of this documentation to describe the 
    different object classes and attributes in detail, please see 
    LDAP documentation for a better treatment.


  **Things to watch out for**

    Since a user folder is one of these items that can lock users out 
    of your site if they break I suggest testing the settings in some 
    inconspicuous location before replacing a site's main acl_users folder 
    with a LDAPUserFolder.

    As a last resort you will always be able to log in and make changes 
    as the superuser (or in newer Zope releases called "emergency user") 
    who, as an added bonus, can delete and create user folders. This is 
    a breach of the standard "the superuser cannot create / own anything" 
    policy, but can save your skin in so many ways.


 **LDAP Schema considerations when used with the CMF**

    The CMF (and by extension, Plone) expect that every user has an email
    address. In order to make everything work correctly your LDAP user
    records must have a "mail" attribute, and this attribute must be set
    up in the "LDAP Schema" tab of your LDAPUserFolder. When you add the
    "mail" schema item make sure you set the "Map to Name" field to
    "email". 

    The attributes that show up on the join form and the personalize view
    are governed by the properties you 'register' using the 
    'Member Properties' tab in the portal_memberdata tool ZMI view, which
    in turn is sourced from the 'LDAP Schema' tab in the LDAPUserFolder
    ZMI view. Attributes you would like to enable for portal members
    must be set up on the LDAPUserFolder 'LDAP Schema' tab first, and
    then registered using the 'Membeer properties' screen in the 
    Member data tool ZMI view.

