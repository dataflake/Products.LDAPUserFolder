############################################################################
#
# Copyright (c) 2009-2011 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__version__ = '3.0dev'

import os
from setuptools import setup
from setuptools import find_packages

NAME = 'Products.LDAPUserFolder'
here = os.path.abspath(os.path.dirname(__file__))

def _read(name):
    f = open(os.path.join(here, name))
    return f.read()

_boundary = '\n' + ('-' * 60) + '\n\n'

setup(name=NAME,
      version=__version__,
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
      url="http://pypi.python.org/pypi/%s" % NAME,
      license="ZPL 2.1 (http://www.zope.org/Resources/License/ZPL-2.1)",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages=['Products'],
      zip_safe=False,
      setup_requires=['setuptools-git'],
      install_requires=[
        'setuptools',
        'Zope2',
        'dataflake.ldapconnection >= 0.2',
        'dataflake.fakeldap',
        ],
      extras_require={
          'exportimport': [
                'Products.GenericSetup >= 1.4.0'
                ],
          },
      entry_points="""
      [zope2.initialize]
      %s = %s:initialize
      """ % (NAME, NAME),
      )

