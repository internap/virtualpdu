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

from virtualpdu.drivers import DeviceNotFound
from virtualpdu.drivers.libvirt_driver import LibvirtDriver
from virtualpdu.tests import base


LIBVIRT_TEST_PROVIDER = 'test:///default'


class TestLibvirtDeviceProviderIntegration(base.TestCase):
    def test_power_on(self):
        provider = LibvirtDriver(uri=LIBVIRT_TEST_PROVIDER)
        provider.power_on('test')

    def test_power_off(self):
        provider = LibvirtDriver(uri=LIBVIRT_TEST_PROVIDER)
        provider.power_off('test')

    def test_power_on_domain_not_found(self):
        provider = LibvirtDriver(uri=LIBVIRT_TEST_PROVIDER)
        self.assertRaises(DeviceNotFound, provider.power_on, 'i-dont-exist')

    def test_power_off_domain_not_found(self):
        provider = LibvirtDriver(uri=LIBVIRT_TEST_PROVIDER)
        self.assertRaises(DeviceNotFound, provider.power_off, 'i-dont-exist')
