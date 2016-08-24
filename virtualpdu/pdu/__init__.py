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


class PDUOutlet(object):
    oid = None
    default_state = univ.Integer(1)

    def __init__(self, outlet_number, pdu):
        self.outlet_number = outlet_number
        self.pdu = pdu
        self._value = self.default_state

    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, value):
        self._value = value
        self.pdu.outlet_state_changed(self.outlet_number, value)


class PDU(object):
    outlet_count = 1
    outlet_index_start = 1
    outlet_class = PDUOutlet
    power_states = {
        'on': POWER_ON,
        'off': POWER_OFF,
        'reboot': REBOOT
    }

    core_to_native_power_states = {
        POWER_ON: 'on',
        POWER_OFF: 'off',
        REBOOT: 'reboot'
    }

    def __init__(self, name, core):
        self.name = name
        self.core = core

        self.oids = [
            self.outlet_class(outlet_number=i + self.outlet_index_start,
                              pdu=self) for i in range(self.outlet_count)
            ]

        self.oid_mapping = {}
        for oid in self.oids:
            self.oid_mapping[oid.oid] = oid

    def get_core_power_state_from_native(self, native_value):
        return self.power_states[native_value]

    def get_native_power_state_from_core(self, core_value):
        return self.core_to_native_power_states[core_value]

    def outlet_state_changed(self, outlet_number, value):
        self.core.pdu_outlet_state_changed(
            name=self.name,
            outlet_number=outlet_number,
            state=self.get_core_power_state_from_native(value))
