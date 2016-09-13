#
# Copyright (c) 2014 ThoughtWorks, Inc.
#
# Pixelated is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Pixelated is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Pixelated. If not, see <http://www.gnu.org/licenses/>.
from mock import patch, MagicMock
from mockito import when
from unittest import TestCase
from pixelated.bitmask_libraries.keymanager import Keymanager
from pixelated.config import leap_config


class KeymanagerTest(TestCase):

    def setUp(self):
        self.provider = MagicMock()
        self.soledad = MagicMock()
        self.auth = MagicMock(token='token', auth='auth')
        with patch('pixelated.bitmask_libraries.keymanager.KeyManager'):
            self.keymanager = Keymanager(self.provider,
                                         self.soledad,
                                         'test_user@some-server.test',
                                         self.auth.token,
                                         self.auth.uuid)

    def tearDown(self):
        reload(leap_config)

    @patch('pixelated.bitmask_libraries.keymanager.KeyManager')
    def test_keymanager_is_created(self, keymanager_mock):
        when(self.provider)._discover_nicknym_server().thenReturn('nicknym_server')
        self.provider.provider_api_cert = 'ca_cert_path'
        self.provider.api_uri = 'api_uri'
        self.provider.api_version = '1'
        self.provider.combined_cerfificates_path = 'combined_ca_bundle'
        leap_config.gpg_binary = '/path/to/gpg'

        Keymanager(self.provider,
                   self.soledad,
                   'test_user@some-server.test',
                   self.auth.token,
                   self.auth.uuid)

        keymanager_mock.assert_called_with(
            'test_user@some-server.test',
            'nicknym_server',
            self.soledad,
            token=self.auth.token,
            ca_cert_path='ca_cert_path',
            api_uri='api_uri',
            api_version='1',
            uid=self.auth.uuid,
            gpgbinary='/path/to/gpg',
            combined_ca_bundle='combined_ca_bundle')

    def test_keymanager_generate_openpgp_key_generates_key_correctly(self):
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(False)

        self.keymanager._gen_key = MagicMock()
        self.keymanager._send_key_to_leap = MagicMock()

        self.keymanager.generate_openpgp_key()

        self.keymanager._gen_key.assert_called_once()
        self.keymanager._send_key_to_leap.assert_called_once()

    def test_keymanager_generate_openpgp_key_dont_regenerate_preexisting_key(self):
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(True)

        self.keymanager._gen_key = MagicMock()

        self.keymanager.generate_openpgp_key()

        self.keymanager._gen_key.assert_not_called()

    def test_keymanager_generate_openpgp_key_dont_upload_preexisting_key(self):
        when(self.keymanager)._key_exists('test_user@some-server.test').thenReturn(True)

        self.keymanager._send_key_to_leap = MagicMock()

        self.keymanager.generate_openpgp_key()

        self.keymanager._send_key_to_leap.assert_not_called()
