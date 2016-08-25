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

from virtualpdu.core import POWER_OFF
from virtualpdu.core import POWER_ON
from virtualpdu.pdu.apc_rackpdu import APCRackPDU

from virtualpdu.tests.integration.pdu import PDUTestCase


class TestAPCRackPDU(PDUTestCase):
    pdu_class = APCRackPDU

    def test_all_ports_are_on_by_default(self):
        enterprises = (1, 3, 6, 1, 4, 1)
        rPDUControl = (318, 1, 1, 12, 3, 3, 1, 1, 4)

        self.assertEqual(1, self.snmp_get(enterprises + rPDUControl + (1,)))
        self.assertEqual(1, self.snmp_get(enterprises + rPDUControl + (2,)))
        self.assertEqual(1, self.snmp_get(enterprises + rPDUControl + (3,)))
        self.assertEqual(1, self.snmp_get(enterprises + rPDUControl + (4,)))
        self.assertEqual(1, self.snmp_get(enterprises + rPDUControl + (5,)))
        self.assertEqual(1, self.snmp_get(enterprises + rPDUControl + (6,)))
        self.assertEqual(1, self.snmp_get(enterprises + rPDUControl + (7,)))
        self.assertEqual(1, self.snmp_get(enterprises + rPDUControl + (8,)))

        self.assertFalse(self.core_mock.pdu_outlet_state_changed.called)

    def test_port_state_can_be_changed(self):
        enterprises = (1, 3, 6, 1, 4, 1)
        rPDUControl = (318, 1, 1, 12, 3, 3, 1, 1, 4)
        outlet_1 = enterprises + rPDUControl + (1,)

        native_power_on = self.pdu.get_native_power_state_from_core(POWER_ON)
        native_power_off = self.pdu.get_native_power_state_from_core(POWER_OFF)

        self.assertEqual(native_power_on,
                         self.snmp_get(outlet_1))

        self.snmp_set(outlet_1, native_power_off)

        self.assertEqual(native_power_off,
                         self.snmp_get(outlet_1))
