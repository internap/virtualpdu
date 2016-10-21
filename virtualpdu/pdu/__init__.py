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
import logging

from pyasn1.type import univ

from virtualpdu import core

logger = logging.getLogger(__name__)


class BasePDUOutletStates(object):
    to_core_mapping = {}

    def to_core(self, state):
        return self.to_core_mapping[state]

    def from_core(self, state):
        return {v: k for (k, v) in self.to_core_mapping.items()}[state]


class PDUOutletStates(BasePDUOutletStates):
    ON = univ.Integer(4)
    OFF = univ.Integer(5)
    REBOOT = univ.Integer(6)

    to_core_mapping = {
        ON: core.POWER_ON,
        OFF: core.POWER_OFF,
        REBOOT: core.REBOOT
    }


class PDUOutlet(object):
    states = PDUOutletStates()

    def __init__(self, pdu_name, outlet_number, core):
        self.pdu_name = pdu_name
        self.outlet_number = outlet_number
        self.core = core
        self.oid = None

    @property
    def state(self):
        return self.states.from_core(
            self.core.get_pdu_outlet_state(
                pdu=self.pdu_name,
                outlet=self.outlet_number))

    @state.setter
    def state(self, state):
        self.core.pdu_outlet_state_changed(
            pdu=self.pdu_name,
            outlet=self.outlet_number,
            state=self.states.to_core(state))


class PDU(object):
    outlet_count = 1
    outlet_index_start = 1
    outlet_class = PDUOutlet

    def __init__(self, name, core):
        self.name = name

        self.oids = [
            self.outlet_class(pdu_name=self.name,
                              outlet_number=o + self.outlet_index_start,
                              core=core,
                              ) for o in range(self.outlet_count)
            ]

        self.oid_mapping = {oid.oid: oid for oid in self.oids}
