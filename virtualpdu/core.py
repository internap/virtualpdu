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

POWER_ON = 'POWER_ON'
POWER_OFF = 'POWER_OFF'
REBOOT = 'REBOOT'


class Core(object):
    def __init__(self, driver, mapping):
        self.driver = driver
        self.mapping = mapping
        self.logger = logging.getLogger(__name__)

    def pdu_outlet_state_changed(self, name, outlet_number, state):
        self.logger.info("PDU '{}', outlet '{}' has new state: '{}'".format(
            name, outlet_number, state)
        )
        try:
            server_name = self._get_server_name(name, outlet_number)

            self.logger.debug(
                "Found server '{}' on PDU '{}' outlet '{}'".format(
                    server_name, name, outlet_number)
            )
        except KeyError:
            return

        if state == POWER_ON:
            self.driver.power_on(server_name)
        elif state == POWER_OFF:
            self.driver.power_off(server_name)
        elif state == REBOOT:
            self.driver.power_off(server_name)
            self.driver.power_on(server_name)

    def _get_server_name(self, pdu_name, outlet_number):
        return self.mapping[(pdu_name, outlet_number)]
