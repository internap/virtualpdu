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

from virtualpdu import power_states


class BasePDUTests(object):
    def test_power_on_notifies_core(self):
        self.pdu.oids[0].value = \
            self.pdu.get_native_power_state_from_core(power_states.POWER_ON)

        self.core_mock.pdu_outlet_state_changed.assert_called_with(
            name='my_pdu',
            outlet_number=1,
            state=power_states.POWER_ON)

    def test_reboot_notifies_core(self):
        self.pdu.oids[0].value = \
            self.pdu.get_native_power_state_from_core(power_states.REBOOT)

        self.core_mock.pdu_outlet_state_changed.assert_called_with(
            name='my_pdu',
            outlet_number=1,
            state=power_states.REBOOT)

    def test_power_off_notifies_core(self):
        self.pdu.oids[0].value = \
            self.pdu.get_native_power_state_from_core(power_states.POWER_OFF)

        self.core_mock.pdu_outlet_state_changed.assert_called_with(
            name='my_pdu',
            outlet_number=1,
            state=power_states.POWER_OFF)
