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

from virtualpdu import core


class BasePDUTests(object):
    def test_power_on_notifies_core(self):
        self.pdu.oids[0].state = \
            self.pdu.outlet_class.states.from_core(core.POWER_ON)

        self.core_mock.pdu_outlet_state_changed.assert_called_with(
            pdu='my_pdu',
            outlet=1,
            state=core.POWER_ON)

    def test_reboot_notifies_core(self):
        self.pdu.oids[0].state = \
            self.pdu.outlet_class.states.from_core(core.REBOOT)

        self.core_mock.pdu_outlet_state_changed.assert_called_with(
            pdu='my_pdu',
            outlet=1,
            state=core.REBOOT)

    def test_power_off_notifies_core(self):
        self.pdu.oids[0].state = \
            self.pdu.outlet_class.states.from_core(core.POWER_OFF)

        self.core_mock.pdu_outlet_state_changed.assert_called_with(
            pdu='my_pdu',
            outlet=1,
            state=core.POWER_OFF)

    def test_read_power_on(self):
        self.core_mock.get_pdu_outlet_state.return_value = core.POWER_ON

        self.assertEqual(
            self.pdu.outlet_class.states.from_core(core.POWER_ON),
            self.pdu.oids[0].state
        )

        self.core_mock.get_pdu_outlet_state.assert_called_with(
            pdu='my_pdu',
            outlet=1)

    def test_read_power_off(self):
        self.core_mock.get_pdu_outlet_state.return_value = core.POWER_OFF

        self.assertEqual(
            self.pdu.outlet_class.states.from_core(core.POWER_OFF),
            self.pdu.oids[0].state
        )

        self.core_mock.get_pdu_outlet_state.assert_called_with(
            pdu='my_pdu',
            outlet=1)
