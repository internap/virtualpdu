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

from virtualpdu import core
from virtualpdu.pdu import BasePDUOutletStates
from virtualpdu.pdu import PDU
from virtualpdu.pdu import PDUOutlet

rPDU_outlet_control_outlet_command = \
    (1, 3, 6, 1, 4, 1, 318, 1, 1, 12, 3, 3, 1, 1, 4)


class APCRackPDUOutletStates(BasePDUOutletStates):
    IMMEDIATE_ON = univ.Integer(1)
    IMMEDIATE_OFF = univ.Integer(2)
    IMMEDIATE_REBOOT = univ.Integer(3)
    DELAYED_ON = univ.Integer(4)
    DELAYED_OFF = univ.Integer(5)
    DELAYED_REBOOT = univ.Integer(6)
    CANCEL_PENDING_COMMAND = univ.Integer(7)

    to_core_mapping = {
        IMMEDIATE_ON: core.POWER_ON,
        IMMEDIATE_OFF: core.POWER_OFF,
        IMMEDIATE_REBOOT: core.REBOOT
    }


class APCRackPDUOutlet(PDUOutlet):
    states = APCRackPDUOutletStates()

    def __init__(self, outlet_number, pdu, default_state):
        super(APCRackPDUOutlet, self).__init__(
            outlet_number, pdu, default_state)
        self.oid = rPDU_outlet_control_outlet_command + (self.outlet_number, )


class APCRackPDU(PDU):
    outlet_count = 8
    outlet_index_start = 1
    outlet_class = APCRackPDUOutlet
