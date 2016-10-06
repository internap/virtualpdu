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
    def __init__(self, *args, **kwargs):
        super(TestCoreIntegration, self).__init__(*args, **kwargs)
        self.driver = libvirt_driver.KeepaliveLibvirtDriver('test:///default')
        self.core = core.Core(driver=self.driver,
                              mapping={
                                  ('my_pdu', 5): 'test'
                              })

        self.outlet_oid = apc_rackpdu.rPDU_outlet_control_outlet_command + (5,)

    def tearDown(self):
        self.pdu_test_harness.stop()
        super(TestCoreIntegration, self).tearDown()

    def get_harness_client(self, pdu_):
        listen_address = '127.0.0.1'
        port = random.randint(20000, 30000)
        community = 'public'

        self.pdu_test_harness = pysnmp_handler.SNMPPDUHarness(pdu_,
                                                              listen_address,
                                                              port,
                                                              community)
        self.pdu_test_harness.start()

        return snmp_client.SnmpClient(cmdgen,
                                      listen_address,
                                      port,
                                      community,
                                      timeout=1,
                                      retries=1)

    def test_pdu_outlet_state_changed_on_power_off(self):
        pdu = apc_rackpdu.APCRackPDU('my_pdu', self.core)
        snmp_client_ = self.get_harness_client(pdu)

        snmp_client_.set(self.outlet_oid,
                         pdu.outlet_class.states.IMMEDIATE_OFF)
        self.assertEqual(drivers.POWER_OFF,
                         self.driver.get_power_state('test'))

        snmp_client_.set(self.outlet_oid,
                         pdu.outlet_class.states.IMMEDIATE_ON)
        self.assertEqual(drivers.POWER_ON,
                         self.driver.get_power_state('test'))

    def test_initial_outlet_power_state_on(self):
        pdu = apc_rackpdu.APCRackPDU('my_pdu', self.core, core.POWER_ON)
        snmp_client_ = self.get_harness_client(pdu)

        self.assertEqual(pdu.outlet_class.states.IMMEDIATE_ON,
                         snmp_client_.get_one(self.outlet_oid))

    def test_initial_outlet_power_state_off(self):
        pdu = apc_rackpdu.APCRackPDU('my_pdu', self.core, core.POWER_OFF)
        snmp_client_ = self.get_harness_client(pdu)

        self.assertEqual(pdu.outlet_class.states.IMMEDIATE_OFF,
                         snmp_client_.get_one(self.outlet_oid))
