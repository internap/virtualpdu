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

# A textual description of the entity.
sysDescr = (1, 3, 6, 1, 2, 1, 1, 1, 0)

# The vendor's authoritative identification of the network management
# subsystem contained in the entity.
sysObjectID = (1, 3, 6, 1, 2, 1, 1, 2, 0)


class PDUFeature(object):
    def __init__(self, oid=None, value=univ.Null):
        self.oid = oid
        self.default_value = value

    @property
    def value(self):
        return self.default_value


class PDUFeatureFactory(object):
    def __init__(self, oid, value):
        self.oid = oid
        self.value = value

    def __call__(self, *args, **kwargs):
        return PDUFeature(oid=self.oid, value=self.value)


def static_info(oid, value):
    return PDUFeatureFactory(oid, value)


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


class PDUOutletFeature(PDUFeature):
    def __init__(self, pdu_name, outlet_number, core):
        super(PDUOutletFeature, self).__init__()
        self.pdu_name = pdu_name
        self.outlet_number = outlet_number
        self.core = core


class PDUOutletControl(PDUOutletFeature):
    states = PDUOutletStates()

    def __init__(self, pdu_name, outlet_number, core):
        super(PDUOutletControl, self).__init__(pdu_name, outlet_number, core)

    @property
    def value(self):
        return self.states.from_core(
            self.core.get_pdu_outlet_state(
                pdu=self.pdu_name,
                outlet=self.outlet_number))

    @value.setter
    def value(self, state):
        self.core.set_pdu_outlet_command(
            pdu=self.pdu_name,
            outlet=self.outlet_number,
            command=self.states.to_core(state))


class PDUOutletState(PDUOutletFeature):
    states = PDUOutletStates()

    def __init__(self, pdu_name, outlet_number, core):
        super(PDUOutletState, self).__init__(pdu_name, outlet_number, core)

    @property
    def value(self):
        return self.states.from_core(
            self.core.get_pdu_outlet_state(
                pdu=self.pdu_name,
                outlet=self.outlet_number))


class TraversableOidMapping(dict):
    def next(self, to):
        set_oid = set(self.keys())
        set_oid.add(to)
        sorted_oids = sorted(set_oid)
        index = sorted_oids.index(to)
        return sorted_oids[index + 1]


class PDU(object):
    outlet_count = 1
    outlet_index_start = 1
    outlet_features = [PDUOutletControl]
    general_features = []

    def __init__(self, name, core, outlet_count=None):
        if outlet_count is not None:
            self.outlet_count = outlet_count
        self.name = name

        mapping = {}
        for outlet_number in range(self.outlet_count):
            for outlet_feature in self.outlet_features:
                obj = outlet_feature(
                    pdu_name=self.name,
                    outlet_number=outlet_number + self.outlet_index_start,
                    core=core)
                mapping[obj.oid] = obj

        for general_feature in self.general_features:
            obj = general_feature(
                pdu_name=self.name,
                core=core)
            mapping[obj.oid] = obj

        self.oid_mapping = mapping
