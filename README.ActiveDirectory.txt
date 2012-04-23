README for configuring the LDAPUserFolder product for M$ Active Directory

  Micro$oft offers two products that purport to speak LDAP, namely
  "Active Directory" and, to a lesser extent, the Exchange server.

  Just like with all other products their claim to standards-compliance
  does not hold much water. The number of users asking for advice on 
  getting the LDAPUserFolder to work with these directory servers speaks
  volumes.

  My development and testing environment does not contain any Micro$oft
  software, I have no testbed to run their products, and I do not intend
  to go out and change that.
  
  As a service to those unfortunate souls who, for whatever reason, are stuck
  with these sub-par LDAP implementations I am using this file to collect
  advice from users who have been successful. I cannot vouch that any of this
  will work for all M$ users and have no way of verifying. Please treat 
  this information with that in mind.

  **Notice**: Nested groups as used by AD are not supported at this time.


  In May 2003, Philipp Kutter wrote:

  """
  Problem: connect existing ADS installation of client with your Zope 
  application. ADS users should be used for authentication.
  
  You know: Administrator passwd on the Windows 2000 Server ADS machine, 
  the IP of the ADS. (May work for XP as well.)
  
  Next thing you need is a tree with the full DN-strings of groups and 
  users. The least-cost solution getting them is installing the W2000 Server 
  Support tools, and running the LDAP Administration Tool, called ldp.exe 
  This tool gives you the strings. Typically your Administrator user will be 
  represented as...
  
  CN=Administrator,CN=Users,DC=clientdomain,DC=com
  
  The tricky point is now, that your ldp.exe did accept you to authenticate 
  with the ADS entering "Administrator" as user/ManagerDN and your password 
  as password.  Under LDAPuserfolder and linux LDAP browser such as gq, this 
  does not work. Your Manager DN must be the full string representing the 
  Manager:
  
  CN=Administrator,CN=Users,DC=clientdomain,DC=com
  
  The complete working settings in my case where:
  
  Users Base DN:            CN=Users,DC=cliendomain,DC=com
  Scope:                    SUBTREE
  Group storage:            Groups stored on LDAP server 
  Groups Base DN:           CN=Users,DC=cliendomain,DC=com
  Scope:                    SUBTREE
  Manager DN:               CN=Administrator,CN=Users,DC=cliendomain,DC=com
  Manager DN Usage:         Always
  Read-only:                checked
  User object classes:      top,person
  User password encryption: SHA
  Default User Roles:       Anonymous
  """

  The item that tripped me up when I did some experimenting with AD was the 
  fact that the "Users" container is not a OrganizationalUnit-type container.
  Notice the "cn" as the relative distinguished name element.

  For all those people who still cannot get it to work, Larry Prikockis did
  some great detective work and found something very interesting. Apparently
  AD will serve "unmolested" data from a secondary port which is much more
  standards-compliant than the garbage AD pushes out of the standard LDAP
  port. Here is what he had to say:

  """
  after banging my head against this particular problem for a while, I
  finally stumbled across a solution!
  Apparently, Microsoft AD can be queried via LDAP in two different ways--
  port 389 is your standard LDAP port... and then there's port 3268, which is
  something Microsoft calls the "Global Catalog". For reasons I don't
  really understand (yet, anyhow), if you do an LDAP query against port 389,
  in addition to your results, you end up getting a referral that chokes
  LDAPUserFolder (I think it's a case of M$ playing fast and loose with the
  LDAP standard and issuing some sort of badly formed referral that either
  LDAPUserFolder or the underlying libraries, or both, don't know what to do
  with).

  HOWEVER-- if you issue the same LDAP query against the server at port 3268
  (the "global catalog"), you get a nice, clean result back.

  I've tried this with my servers using LDAPUserFolder and AD and it works
  perfectly!

  For further details, here's a link to the discussion that I stumbled across
  on the web explaining all this:
  http://www.mail-archive.com/activedir@mail.activedir.org/msg03887.html
  """

  "Fast and loose" with the LDAP standard - I think I could not have put it
  any better myself.


