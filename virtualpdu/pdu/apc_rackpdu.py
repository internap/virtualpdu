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

from pyasn1.type import univ

from virtualpdu.core import POWER_OFF
from virtualpdu.core import POWER_ON
from virtualpdu.core import REBOOT
from virtualpdu.pdu import PDU
from virtualpdu.pdu import PDUOutlet

rPDU_outlet_control_outlet_command = \
    (1, 3, 6, 1, 4, 1, 318, 1, 1, 12, 3, 3, 1, 1, 4)

rPDU_power_mappings = {
    'immediateOn': univ.Integer(1),
    'immediateOff': univ.Integer(2),
    'immediateReboot': univ.Integer(3),
    'delayedOn': univ.Integer(4),
    'delayedOff': univ.Integer(5),
    'delayedReboot': univ.Integer(6),
    'cancelPendingCommand': univ.Integer(7),
}


class APCRackPDUOutlet(PDUOutlet):
    default_state = rPDU_power_mappings['immediateOn']

    def __init__(self, outlet_number, pdu):
        super(APCRackPDUOutlet, self).__init__(outlet_number, pdu)
        self.oid = rPDU_outlet_control_outlet_command + (self.outlet_number, )


class APCRackPDU(PDU):
    outlet_count = 8
    outlet_index_start = 1
    outlet_class = APCRackPDUOutlet
    power_states = {
        rPDU_power_mappings['immediateOn']: POWER_ON,
        rPDU_power_mappings['immediateOff']: POWER_OFF,
        rPDU_power_mappings['immediateReboot']: REBOOT,
    }

    core_to_native_power_states = {
        POWER_ON: rPDU_power_mappings['immediateOn'],
        POWER_OFF: rPDU_power_mappings['immediateOff'],
        REBOOT: rPDU_power_mappings['immediateReboot']
    }
