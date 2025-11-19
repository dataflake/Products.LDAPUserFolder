##############################################################################
#
# Copyright (c) 2000-2023 Jens Vagelpohl and Contributors. All Rights Reserved.
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

from setuptools import setup


NAME = 'Products.LDAPUserFolder'


def read(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as fp:
        return fp.read()


setup(
    name='Products.LDAPUserFolder',
    version='6.0',
    description='A LDAP-enabled Zope user folder',
    long_description=read('README.rst'),
    long_description_content_type='text/x-rst',
    classifiers=[
        "Development Status :: 6 - Mature",
        "Environment :: Web Environment",
        "Framework :: Zope",
        "Framework :: Zope :: 5",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Zope Public License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP :: Site Management",
        "Topic :: Software Development",
        "Topic :: System :: Systems Administration ::"
        "Authentication/Directory :: LDAP",
    ],
    keywords='web application server zope authentication ldap',
    author="Jens Vagelpohl and contributors",
    author_email="jens@dataflake.org",
    url="https://github.com/dataflake/Products.LDAPUserFolder",
    project_urls={
        'Documentation': 'https://productsldapuserfolder.readthedocs.io/',
        'Issue Tracker': (
            'https://github.com/dataflake/'
            'Products.LDAPUserFolder/issues'),
        'Sources': 'https://github.com/dataflake/Products.LDAPUserFolder',
    },
    license="ZPL-2.1",
    python_requires='>=3.10',
    install_requires=[
                    'Zope >= 5',
                    'dataflake.cache',
                    'dataflake.fakeldap',
                    'python-ldap >= 3.3',
    ],
    extras_require={
        'exportimport': ['Products.GenericSetup >= 2.0b1'],
        'docs': [
            'Sphinx',
            'furo',
            'repoze.sphinx.autointerface',
        ],
    },
)
