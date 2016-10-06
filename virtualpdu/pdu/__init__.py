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

    def __init__(self, outlet_number, pdu, default_state):
        self.outlet_number = outlet_number
        self.pdu = pdu
        self._state = default_state
        self.oid = None

    @property
    def state(self):
        return self._state

    @state.setter
    def state(self, state):
        self._state = state
        self.pdu.outlet_state_changed(self.outlet_number, self._state)


class PDU(object):
    outlet_count = 1
    outlet_index_start = 1
    outlet_class = PDUOutlet

    def __init__(self, name, core, outlet_default_state=core.POWER_ON):
        self.name = name
        self.core = core

        outlet_native_default_state = \
            self.outlet_class.states.from_core(outlet_default_state)

        self.oids = [
            self.outlet_class(outlet_number=o + self.outlet_index_start,
                              pdu=self,
                              default_state=outlet_native_default_state
                              ) for o in range(self.outlet_count)
            ]

        self.oid_mapping = {oid.oid: oid for oid in self.oids}

    def outlet_state_changed(self, outlet_number, value):
        self.core.pdu_outlet_state_changed(
            name=self.name,
            outlet_number=outlet_number,
            state=self.outlet_class.states.to_core(value))
