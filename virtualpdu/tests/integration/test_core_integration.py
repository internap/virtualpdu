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

import random

from pysnmp.entity.rfc3413.oneliner import cmdgen

from virtualpdu import core
from virtualpdu import drivers
from virtualpdu.drivers import libvirt_driver
from virtualpdu.pdu import apc_rackpdu
from virtualpdu.pdu import pysnmp_handler
from virtualpdu.tests import base
from virtualpdu.tests import snmp_client


class TestCoreIntegration(base.TestCase):
    def tearDown(self):
        self.pdu_test_harness.stop()
        super(TestCoreIntegration, self).tearDown()

    def test_pdu_outlet_state_changed_on_power_off(self):
        mapping = {
            ('my_pdu', 5): 'test'
        }
        driver = libvirt_driver.KeepaliveLibvirtDriver('test:///default')

        core_ = core.Core(driver=driver, mapping=mapping)

        pdu_ = apc_rackpdu.APCRackPDU('my_pdu', core_)
        outlet_oid = apc_rackpdu.rPDU_outlet_control_outlet_command + (5,)

        listen_address = '127.0.0.1'
        port = random.randint(20000, 30000)
        community = 'public'

        self.pdu_test_harness = pysnmp_handler.SNMPPDUHarness(
            pdu_,
            listen_address,
            port,
            community)
        self.pdu_test_harness.start()

        snmp_client_ = snmp_client.SnmpClient(cmdgen,
                                              listen_address,
                                              port,
                                              community,
                                              timeout=1,
                                              retries=1)

        snmp_client_.set(outlet_oid,
                         apc_rackpdu.rPDU_power_mappings['immediateOff'])
        self.assertEqual(drivers.POWER_OFF,
                         driver.get_power_state('test'))

        snmp_client_.set(outlet_oid,
                         apc_rackpdu.rPDU_power_mappings['immediateOn'])
        self.assertEqual(drivers.POWER_ON,
                         driver.get_power_state('test'))
