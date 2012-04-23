import os
from setuptools import setup
from setuptools import find_packages

NAME = 'LDAPUserFolder'

def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()

_boundary = '\n' + ('-' * 60) + '\n\n'

setup(name='Products.%s' % NAME,
      version=read('VERSION.txt').strip(),
      description='A LDAP-enabled Zope 2 user folder',
      long_description=( read('README.txt') 
                       + _boundary
                       + read('CHANGES.txt')
                       + _boundary
                       + "Download\n========"
                       ),
      classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Zope2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 2 :: Only",
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
      setup_requires=['setuptools-git'],
      install_requires=[
        'setuptools',
        'Zope2',
        'dataflake.fakeldap',
        'python-ldap',
        ],
      extras_require={
          'cmfldap': ['Products.CMFDefault >= 2.1.0'],
          'exportimport': ['Products.GenericSetup >= 1.4.0'],
          },
      entry_points="""
      [zope2.initialize]
      Products.%s = Products.%s:initialize
      """ % (NAME, NAME),
      )

