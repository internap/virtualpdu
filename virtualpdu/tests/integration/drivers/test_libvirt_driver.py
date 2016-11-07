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

from virtualpdu import drivers
from virtualpdu.drivers import libvirt_driver
from virtualpdu.tests import base


LIBVIRT_TEST_PROVIDER = 'test:///default'


class TestLibvirtDeviceProviderIntegration(base.TestCase):
    def setUp(self):
        super(TestLibvirtDeviceProviderIntegration, self).setUp()
        self.driver = libvirt_driver.KeepaliveLibvirtDriver(
            uri=LIBVIRT_TEST_PROVIDER)
        self.server_name = 'test'

    def test_power_on(self):
        self.driver.power_on(self.server_name)

    def test_power_off(self):
        self.driver.power_off(self.server_name)

    def test_get_power_state(self):
        self.driver.power_off(self.server_name)
        self.assertEqual(drivers.POWER_OFF,
                         self.driver.get_power_state(self.server_name))

        self.driver.power_on(self.server_name)
        self.assertEqual(drivers.POWER_ON,
                         self.driver.get_power_state(self.server_name))

    def test_power_on_domain_not_found(self):
        self.assertRaises(drivers.DeviceNotFound,
                          self.driver.power_on, 'i-dont-exist')

    def test_power_off_domain_not_found(self):
        self.assertRaises(drivers.DeviceNotFound,
                          self.driver.power_off, 'i-dont-exist')

    def test_get_power_domain_not_found_raises(self):
        self.assertRaises(drivers.DeviceNotFound,
                          self.driver.get_power_state, 'i-dont-exist')
