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

from virtualpdu.device_provider import DeviceProvider
from virtualpdu.tests import base


class TestDeviceProvider(base.TestCase):
    def test_power_on(self):
        provider = DeviceProvider()
        self.assertRaises(NotImplementedError, provider.power_on, 'domainA')

    def test_power_off(self):
        provider = DeviceProvider()
        self.assertRaises(NotImplementedError, provider.power_off, 'domainA')
