##############################################################################
#
# Copyright (c) 2000-2021 Jens Vagelpohl and Contributors. All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
""" Utility module tests
"""

import unittest

from AccessControl import AuthEncoding

from .. import utils


class PasswordCreationTests(unittest.TestCase):

    # The encoded passwords used for reference have been created
    # using the `slappasswd` utility.

    def setUp(self):
        self.pwd = 'b1g#5ecret'

    def test_createLDAPPassword_ssha(self):
        encoded = utils._createLDAPPassword(self.pwd, 'ssha')
        self.assertTrue(encoded.startswith('{SSHA}'))
        self.assertTrue(AuthEncoding.pw_validate(encoded, self.pwd))

    def test_createLDAPPassword_sha(self):
        reference = '{SHA}pJwajxbTJu5Fvx2p4YRmsp/frQo='
        encoded = utils._createLDAPPassword(self.pwd, 'sha')
        self.assertEqual(reference, encoded)

    def test_createLDAPPassword_md5(self):
        reference = '{MD5}FZcFLcTV3v/1Rgouir4dhA=='
        encoded = utils._createLDAPPassword(self.pwd, 'md5')
        self.assertEqual(reference, encoded)

    @unittest.skipIf(utils.crypt is None, 'crypt library unavailable.')
    def test_createLDAPPassword_crypt(self):
        # Crypt is not available on all platforms
        encoded = utils._createLDAPPassword(self.pwd, 'crypt')
        self.assertTrue(encoded.startswith('{CRYPT}'))
        self.assertTrue(AuthEncoding.pw_validate(encoded, self.pwd))

    def test_createLDAPPassword_clear(self):
        reference = 'b1g#5ecret'
        encoded = utils._createLDAPPassword(self.pwd, 'clear')
        self.assertEqual(reference, encoded)
