import os
from setuptools import setup
from setuptools import find_packages

NAME = 'LDAPUserFolder'
here = os.path.abspath(os.path.dirname(__file__))
package = os.path.join(here, 'Products', NAME)

def _read(name):
    f = open(os.path.join(package, name))
    return f.read()

_boundary = '\n' + ('-' * 60) + '\n\n'

setup(name='Products.%s' % NAME,
      version=_read('VERSION.txt').strip(),
      description='A LDAP-enabled Zope 2 user folder',
      long_description=( _read('README.txt') 
                       + _boundary
                       + _read('CHANGES.txt')
                       + _boundary
                       + "Download\n========"
                       ),
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
      url="http://pypi.python.org/pypi/Products.%s" % NAME,
      license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      install_requires=[
        #"Zope >= 2.8",
        "setuptools",
        "dataflake.ldapconnection",
        ],
      extras_require={
          'cmfldap': [
                #'Zope >= 2.10.4',
                'Products.CMFDefault >= 2.1.0'
                ],
          'exportimport': [
                #'Zope >= 2.10.0
                'Products.GenericSetup >= 1.4.0'
                ],
          },
      entry_points="""
      [zope2.initialize]
      Products.%s = Products.%s:initialize
      """ % (NAME, NAME),
      )

