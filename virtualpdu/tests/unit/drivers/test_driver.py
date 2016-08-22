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

from virtualpdu.drivers import Driver
from virtualpdu.tests import base


class TestDriver(base.TestCase):
    def test_power_on(self):
        driver = Driver()
        self.assertRaises(NotImplementedError, driver.power_on, 'domainA')

    def test_power_off(self):
        driver = Driver()
        self.assertRaises(NotImplementedError, driver.power_off, 'domainA')

    def test_get_power_state(self):
        driver = Driver()
        self.assertRaises(NotImplementedError,
                          driver.get_power_state, 'domainA')
