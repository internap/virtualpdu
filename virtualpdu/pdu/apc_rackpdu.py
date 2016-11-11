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
from virtualpdu.pdu import PDUOutletFeature
from virtualpdu.pdu import PDUOutletState
from virtualpdu.pdu import static_info
from virtualpdu.pdu import sysDescr
from virtualpdu.pdu import sysObjectID


rPDU_sysObjectID = (1, 3, 6, 1, 4, 1, 318, 1, 3, 4, 6)

rPDU = (1, 3, 6, 1, 4, 1, 318, 1, 1, 12)
rPDU_outlet_control_outlet_command = rPDU + (3, 3, 1, 1, 4)
rPDU_outlet_config_index = rPDU + (3, 4, 1, 1, 1)
rPDU_outlet_config_outlet_name = rPDU + (3, 4, 1, 1, 2)
rPDU_outlet_status_outlet_state = rPDU + (3, 5, 1, 1, 4)
rPDU_load_status_load = rPDU + (2, 3, 1, 1, 2)
rPDU_load_status_load_state = rPDU + (2, 3, 1, 1, 3)

amp_10 = 100
phase_load_normal = 1


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


class APCRackPDUOutletControl(PDUOutletControl):
    states = APCRackPDUOutletStates()

    def __init__(self, pdu_name, outlet_number, core):
        super(APCRackPDUOutletControl, self).__init__(
            pdu_name, outlet_number, core)
        self.oid = rPDU_outlet_control_outlet_command + (self.outlet_number, )


class APCRackPDUOutletState(PDUOutletState):
    states = APCRackPDUOutletStates()

    def __init__(self, pdu_name, outlet_number, core):
        super(APCRackPDUOutletState, self).__init__(
            pdu_name, outlet_number, core)
        self.oid = rPDU_outlet_status_outlet_state + (self.outlet_number, )


class APCRackPDUOutletName(PDUOutletFeature):
    states = APCRackPDUOutletStates()

    def __init__(self, pdu_name, outlet_number, core):
        super(APCRackPDUOutletName, self).__init__(
            pdu_name, outlet_number, core)
        self.oid = rPDU_outlet_config_outlet_name + (self.outlet_number, )

    @property
    def value(self):
        return univ.OctetString('Outlet #{}'.format(self.outlet_number))


class APCRackPDUOutletConfigIndex(PDUOutletFeature):
    def __init__(self, pdu_name, outlet_number, core):
        super(APCRackPDUOutletConfigIndex, self).__init__(
            pdu_name, outlet_number, core)
        self.oid = rPDU_outlet_config_index + (self.outlet_number, )

    @property
    def value(self):
        return univ.Integer(self.outlet_number)


class APCRackPDU(PDU):
    outlet_count = 24
    outlet_index_start = 1
    outlet_features = [APCRackPDUOutletControl, APCRackPDUOutletName,
                       APCRackPDUOutletConfigIndex, APCRackPDUOutletState]
    general_features = [
        static_info(sysDescr, univ.OctetString("APC Rack PDU (virtualpdu)")),
        static_info(sysObjectID, univ.ObjectIdentifier(rPDU_sysObjectID)),
        static_info(rPDU_load_status_load, univ.Integer(amp_10)),
        static_info(rPDU_load_status_load_state,
                    univ.Integer(phase_load_normal))
    ]
