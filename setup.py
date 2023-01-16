##############################################################################
#
# Copyright (c) 2009-2021 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

import os

from setuptools import find_packages
from setuptools import setup


NAME = 'Products.LDAPUserFolder'


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


setup(name=NAME,
      version='4.1',
      description='A LDAP-enabled Zope user folder',
      long_description=read('README.rst'),
      classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Zope",
        "Framework :: Zope :: 4",
        "Framework :: Zope :: 5",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development",
        "Topic :: System :: Systems Administration ::"
        " Authentication/Directory :: LDAP",
        ],
      keywords='web application server zope authentication ldap',
      author="Jens Vagelpohl and contributors",
      author_email="jens@dataflake.org",
      url="https://github.com/dataflake/%s" % NAME,
      project_urls={
        'Documentation': 'https://productsldapuserfolder.readthedocs.io/',
        'Issue Tracker': ('https://github.com/dataflake/'
                          'Products.LDAPUserFolder/issues'),
        'Sources': 'https://github.com/dataflake/Products.LDAPUserFolder',
      },
      license="ZPL 2.1",
      packages=find_packages('src'),
      include_package_data=True,
      namespace_packages=['Products'],
      package_dir={'': 'src'},
      zip_safe=False,
      python_requires='>=3.5',
      install_requires=[
        'setuptools',
        'six',
        'Zope >= 4.0b5',
        'dataflake.cache',
        'dataflake.fakeldap',
        'python-ldap >= 3.3, < 3.4; python_version < "3.6"',
        'python-ldap >= 3.3; python_version >= "3.6"',
        ],
      extras_require={
        'exportimport': ['Products.GenericSetup >= 2.0b1'],
        'docs': [
          'Sphinx',
          'sphinx_rtd_theme',
          'repoze.sphinx.autointerface',
          'pkginfo'],
        },
      entry_points="""
      [zope2.initialize]
      %s = %s:initialize
      """ % (NAME, NAME),
      )
