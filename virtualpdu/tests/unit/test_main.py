# Copyright 2016 Internap
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from virtualpdu.drivers import libvirt_driver
from virtualpdu.main import get_driver_from_config
from virtualpdu.main import get_mapping_for_config
from virtualpdu.main import UnableToParseConfig
from virtualpdu.tests import base


class TestMain(base.TestCase):
    def test_get_driver_from_config(self):
        conf = configparser.RawConfigParser()
        conf.add_section('global')
        conf.set('global', 'libvirt_uri', 'test:///default')

        driver = get_driver_from_config(conf)
        self.assertIsInstance(driver, libvirt_driver.LibvirtDriver)

        self.assertEqual('test:///default', driver.uri)

    def test_get_driver_from_config_missing_libvirt_uri(self):
        conf = configparser.RawConfigParser()
        conf.add_section('global')
        conf.set('global', '')

        self.assertRaises(UnableToParseConfig, get_driver_from_config, conf)

    def test_get_mapping_for_config_single_port(self):
        conf = configparser.RawConfigParser()
        conf.add_section('my_pdu')
        conf.set('my_pdu', 'ports', '5:test')

        expected_mapping = {
            ('my_pdu', 5): 'test'
        }
        self.assertDictEqual(expected_mapping, get_mapping_for_config(conf))

    def test_get_mapping_for_config_multiple_port(self):
        conf = configparser.RawConfigParser()
        conf.add_section('my_pdu')
        conf.set('my_pdu', 'ports', '5:test,8:hello')

        expected_mapping = {
            ('my_pdu', 5): 'test',
            ('my_pdu', 8): 'hello'
        }
        self.assertDictEqual(expected_mapping, get_mapping_for_config(conf))

    def test_get_mapping_for_config_multiple_pdu(self):
        conf = configparser.RawConfigParser()
        conf.add_section('my_pdu_1')
        conf.set('my_pdu_1', 'ports', '5:test,8:hello')
        conf.add_section('my_pdu_2')
        conf.set('my_pdu_2', 'ports', '1:best,2:jello')

        expected_mapping = {
            ('my_pdu_1', 5): 'test',
            ('my_pdu_1', 8): 'hello',
            ('my_pdu_2', 1): 'best',
            ('my_pdu_2', 2): 'jello'
        }
        self.assertDictEqual(expected_mapping, get_mapping_for_config(conf))

    def test_get_mapping_for_config_missing_ports(self):
        conf = configparser.RawConfigParser()
        conf.add_section('my_pdu')

        self.assertRaises(UnableToParseConfig, get_mapping_for_config, conf)

    def test_get_mapping_for_config_no_pdus(self):
        conf = configparser.RawConfigParser()

        expected_mapping = {}
        self.assertEqual(expected_mapping, get_mapping_for_config(conf))
