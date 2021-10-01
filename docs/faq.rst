Frequently asked questions
==========================

General
-------

Why use LDAP to store user records?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
LDAP as a source of Zope user records is an excellent choice in many cases,
like...

- You already have an existing LDAP setup that might store user
  data and you do not want to duplicate it into a Zope user folder
- You want to make the same user database available to other applications
  like mail, address book clients, operating system authenticators
  or other network services that allow authentication against LDAP
- You have several separate Zope installations that need to share user records
- You want to be able to store more than just user name and password in your
  Zope user folder
- You want to manipulate user data outside of Zope


What should my directory tree or schema look like?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Your LDAP server should contain records that can be used as user
records. Any object types like person, organizationalPerson,
or inetOrgPerson and any derivatives thereof should work. Records
of type posixAccount should work correctly as well.
The LDAPUserFolder expects your user records to have at least the
following attributes, most of which are required for the
abovementioned object classes, anyway:

- an attribute to hold the user ID (like cn, uid, etc)
- userPassword (the password field)
- objectClass
- whatever attribute you choose as the username attribute
- optionally other person-related attributes like sn (last name),
  givenName (first name), uid or mail (email address)

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

It is outside of the scope of this documentation to describe the
different object classes and attributes in detail, please see
LDAP documentation for a better treatment.


Help, I locked myself out of my Zope site!
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Since a user folder is one of these items that can lock users out
of the site if they break I suggest testing the settings in some
inconspicuous location before replacing a site's main acl_users folder
in the root of the ZODB with a LDAPUserFolder.
As a last resort you will always be able to log in and make changes
as the superuser (or in newer Zope releases called "emergency user")
who can delete and create user folders.


Microsoft Active Directory
--------------------------
In general, with ActiveDirectory `Your Mileage May Vary`. Neither do I
have any Windows-based environment, nor any Windows-version with a running
ActiveDirectory installation. I have fixed ActiveDirectory-related issues
in the past, though, relying on feedback from users.


Are nested groups supported?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Nested groups as used by AD are not supported at this time.


Netscape directory products
---------------------------

Why does the LDAPUserFolder not show all my LDAP groups?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Netscape Directory at some point allowed the creation of empty group
records, meaning group records with no member attributes. Those records
will not show up in the LDAPUserFolder. Only group records with at least
one member attribute are considered.
