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
from virtualpdu.pdu import PDUOutletControl
from virtualpdu.pdu import static_info
from virtualpdu.pdu import sysDescr
from virtualpdu.pdu import sysObjectID

sBTA = (1, 3, 6, 1, 4, 1, 4779)
sBTA_modules_RPC_outlet_state = sBTA + (1, 3, 5, 3, 1, 3)


class BaytechMRP27PDUOutletStates(BasePDUOutletStates):
    OFF = univ.Integer(0)
    ON = univ.Integer(1)
    REBOOT = univ.Integer(2)
    LOCKON = univ.Integer(3)
    LOCKOFF = univ.Integer(4)
    UNLOCK = univ.Integer(5)

    to_core_mapping = {
        ON: core.POWER_ON,
        OFF: core.POWER_OFF,
        REBOOT: core.REBOOT
    }


class BaytechMRP27PDUOutletControl(PDUOutletControl):
    states = BaytechMRP27PDUOutletStates()

    def __init__(self, pdu_name, outlet_number, core):
        super(BaytechMRP27PDUOutletControl, self).__init__(
            pdu_name, outlet_number, core)
        self.oid = sBTA_modules_RPC_outlet_state + (1, self.outlet_number)


class BaytechMRP27PDU(PDU):
    outlet_count = 24
    outlet_index_start = 1
    outlet_features = [BaytechMRP27PDUOutletControl]
    general_features = [
        static_info(sysDescr, univ.OctetString(
            "Universal RPC Host Module (virtualpdu)")),
        static_info(sysObjectID, univ.ObjectIdentifier(sBTA)),
    ]
