import os
from setuptools import setup
from setuptools import find_packages

NAME = 'LDAPUserFolder'
here = os.path.abspath(os.path.dirname(__file__))
package = os.path.join(here, 'Products', NAME)

def _package_doc(name):
    f = open(os.path.join(package, name))
    return f.read()

VERSION = _package_doc('VERSION.txt').strip()

_boundary = '\n' + ('-' * 60) + '\n'
README = (open(os.path.join(here, 'README.txt')).read()
        + _boundary + _package_doc('README.txt')
        + _boundary + _package_doc('CHANGES.txt')
         )

setup(name='Products.LDAPUserFolder',
      version=VERSION,
      description='A LDAP-enabled Zope 2 user folder',
      long_description=README,
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development",
        "Topic :: System :: Systems Administration :: Authentication/Directory :: LDAP",
        ],
      keywords='web application server zope zope2 ldap',
      author="Jens Vagelpohl and contributors",
      author_email="jens@dataflake.org",
      url="http://www.dataflake.org/software/ldapuserfolder",
      license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      #install_requires=['Zope >= 2.8']
      entry_points="""
      [zope2.initialize]
      Products.LDAPUserFolder = Products.LDAPUserFolder:initialize
      """,
      )

