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
from concurrent.futures import ThreadPoolExecutor
import logging

POWER_ON = 'POWER_ON'
POWER_OFF = 'POWER_OFF'
REBOOT = 'REBOOT'

command_state_mapping = {
    POWER_ON: POWER_ON,
    POWER_OFF: POWER_OFF,
    REBOOT: POWER_ON
}


class Core(object):
    def __init__(self, driver, mapping, store, default_state):
        self.driver = driver
        self.mapping = mapping
        self.store = store
        self.default_state = default_state
        self.logger = logging.getLogger(__name__)
        self.executor = ThreadPoolExecutor(max_workers=1)

    def set_pdu_outlet_command(self, pdu, outlet, command):
        self.store[(pdu, outlet)] = command_state_mapping[command]

        self.logger.info("PDU '{}', outlet '{}' has new command: '{}'".format(
            pdu, outlet, command)
        )
        try:
            device = self._get_device(pdu, outlet)

            self.logger.debug(
                "Found server '{}' on PDU '{}' outlet '{}'".format(
                    device, pdu, outlet)
            )
        except KeyError:
            return

        self._async_change(device, command)

    def _async_change(self, device, command):
        if command == POWER_ON:
            def switch_power():
                self.driver.power_on(device)
        elif command == POWER_OFF:
            def switch_power():
                self.driver.power_off(device)
        elif command == REBOOT:
            def switch_power():
                self.driver.power_off(device)
                self.driver.power_on(device)
        else:
            self.logger.error("Unknown power command: {}".format(command))
            return

        self.executor.submit(switch_power)

    def get_pdu_outlet_state(self, pdu, outlet):
        try:
            return self.store[(pdu, outlet)]
        except KeyError:
            pass

        try:
            device = self._get_device(pdu, outlet)
            power_state = self.driver.get_power_state(device)
        except KeyError:
            power_state = self.default_state

        self.store[(pdu, outlet)] = power_state
        return power_state

    def _get_device(self, pdu, outlet):
        return self.mapping[(pdu, outlet)]
